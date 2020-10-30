import hashlib
import multiprocessing
import os
import queue
import threading
import time
from queue import Queue
from typing import Any, TextIO, Dict
import yaml

start_time = time.time()
DEBUG = True

path_queue = queue.Queue()
result_queue = queue.Queue()

all_files_dict: Dict[Any, Any] = {}
all_fh: TextIO = open('all_files.csv', 'a')


class PrintThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    @staticmethod
    def write_to_file(q_item):
        file_path, fhash = q_item
        all_fh.write('%s,%s\n' % (file_path, fhash))
        if fhash in all_files_dict:
            all_files_dict[fhash].append(file_path)
        else:
            all_files_dict[fhash] = [file_path]

    def run(self):
        while True:
            result = self.queue.get()
            self.write_to_file(result)
            self.queue.task_done()


class FindFilesThread(threading.Thread):
    def __init__(self, in_queue, out_queue):
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue

    def search_files(self, directory: str) -> bool:
        if not os.path.exists(directory):
            debug("Could not find path %s" % directory)
            return False
        for dir_path, dir_names, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(dir_path, file_name)
                fhash = file_hash(file_path)
                # TODO: Add more info about specific file(s)
                # statistics = os.stat(file_path)
                self.out_queue.put((file_path, fhash))
        return True

    def run(self):
        while True:
            result = self.in_queue.get()
            self.search_files(result)
            self.in_queue.task_done()


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


def main():
    with open('.file_paths.yaml') as fh:
        search_paths = yaml.load(fh, Loader=yaml.FullLoader)

    for my_path in search_paths['file_paths']:
        debug("Creating queue, %s" % my_path)
        path_queue.put(my_path)
    debug("Finished creating path queues")

    cpu_count = multiprocessing.cpu_count()
    # If the queue size is less than the number of CPUs, it makes no sense to
    # instantiate more threads and we stop.
    # TODO: If num_threads == 1, program doesn't work for some reason. Need to fix.
    # TODO: Temporary solution is to find the max with 2 to ensure no less than 2 threads.
    num_threads = max(min(path_queue.qsize(), cpu_count), 2)
    for cnt in range(num_threads):
        debug("Instantiating Worker %d" % cnt)
        t = FindFilesThread(in_queue=path_queue, out_queue=result_queue)
        t.setDaemon(True)
        t.start()
    debug("Finished creating FindFiles Threads")
    t = PrintThread(result_queue)
    t.setDaemon(True)
    t.start()
    path_queue.join()
    result_queue.join()

    # Write everything to a file.
    dict_file_name = r'all_files_dict.yaml'
    with open(dict_file_name, 'w') as file_handle:
        debug("Writing to file %s" % dict_file_name)
        yaml.dump(all_files_dict, file_handle)

    all_fh.close()


if __name__ == '__main__':
    main()
    print("Run Time: %0.6f seconds" % (time.time() - start_time))
