import hashlib
import multiprocessing
import os
import queue
import threading
import time
from typing import Any, TextIO, Dict
import yaml

start_time = time.time()
DEBUG = True
q = queue.Queue()
all_fh: TextIO = open('all_files.csv', 'a')
all_files_dict: Dict[Any, Any] = {}


def debug(my_string: str):
    if DEBUG:
        print(my_string)


def file_hash(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def search_files(directory: str) -> bool:
    if not os.path.exists(directory):
        debug("Could not find path %s" % directory)
        return False
    for dir_path, dir_names, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(dir_path, file_name)
            # TODO: Add more info about specific file(s)
            # statistics = os.stat(file_path)
            fhash = file_hash(file_path)
            if fhash in all_files_dict:
                all_files_dict[fhash].append(file_path)
            else:
                all_files_dict[fhash] = [file_path]
                all_fh.write('%s,%s\n' % (file_path, fhash))
    return True


def worker() -> bool:
    while True:
        file_path = q.get()
        debug("Searching {FILEPATH}".format(FILEPATH=file_path))
        search_files(file_path)
        q.task_done()
        return True


def main():
    with open('.file_paths.yaml') as fh:
        search_paths = yaml.load(fh, Loader=yaml.FullLoader)

    for my_path in search_paths['file_paths']:
        debug("Creating queue, %s" % my_path)
        q.put(my_path)
    debug("Finished creating Queues")

    cpu_count = multiprocessing.cpu_count()
    # If the queue size is less than the number of CPUs, it makes no sense to
    # instantiate more threads and we stop.
    # TODO: If num_threads == 1, program doesn't work for some reason. Need to fix.
    # TODO: Temporary solution is to find the max with 2 to ensure no less than 2 threads.
    num_threads = max(min(q.qsize(), cpu_count), 2)

    threads = []
    for cnt in range(num_threads):
        debug("Instantiating Worker %d" % cnt)
        threads.append(threading.Thread(target=worker, daemon=True))
    debug("Finished creating Threads")

    [x.start() for x in threads]

    q.join()
    debug("Queue joined (all workers are done with all items in queue")

    # Write everything to a file.
    dict_file_name = r'all_files_dict.yaml'
    file_handle: TextIO
    with open(dict_file_name, 'w') as file_handle:
        debug("Writing to file %s" % dict_file_name)
        yaml.dump(all_files_dict, file_handle)
    all_fh.close()


if __name__ == '__main__':
    main()
    print("Run Time: %0.6f seconds" % (time.time() - start_time))
