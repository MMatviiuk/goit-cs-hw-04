import multiprocessing
import logging
import time
from collections import defaultdict

def search_in_files(file_list, keywords, results):
    """Searches for keywords in a list of files.

    Args:
        file_list: A list of file paths.
        keywords: A list of keywords to search for.
        results: A shared dictionary to store the results.
    """
    logging.debug(f"Searching in: {file_list} ...")
    local_results = defaultdict(list)
    for file in file_list:
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    for keyword in keywords:
                        if keyword in line:
                            local_results[keyword].append(file)
        except FileNotFoundError:
            logging.warning(f"File not found: {file}")
        except Exception as e:
            logging.error(f"Error processing file {file}: {e}")

    # Use a manager to share the results dictionary between processes
    with manager.get_lock():
        for keyword, files in local_results.items():
            results[keyword].extend(files)

def multiprocess_search(files, keywords, num_processes=4):
    """Performs a multiprocess search for keywords in files.

    Args:
        files: A list of file paths.
        keywords: A list of keywords to search for.
        num_processes: The number of processes to use.

    Returns:
        A dictionary mapping keywords to a list of files where they were found.
    """
    if not files or not keywords:
        return {}

    logging.basicConfig(level=logging.INFO, format="%(process)d %(message)s")
    manager = multiprocessing.Manager()
    results = manager.dict()
    processes = []
    files_per_process = len(files) // num_processes

    for i in range(num_processes):
        start_index = i * files_per_process
        end_index = min((i + 1) * files_per_process, len(files))
        process_files = files[start_index:end_index]
        process = multiprocessing.Process(target=search_in_files, args=(process_files, keywords, results))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    return results

# Example usage:
if __name__ == "__main__":
    files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt", "file6.txt"]
    keywords = ["python", "javascript", "<html>"]
    num_processes = 4

    start_time = time.time()
    results = multiprocess_search(files, keywords, num_processes)
    end_time = time.time()
    print(f"Results: {results}")
    print(f"Execution time: {end_time - start_time} seconds")
