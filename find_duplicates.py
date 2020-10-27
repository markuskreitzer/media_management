import json
import os
from typing import Any, Union
import hashlib

all_files = {}


def file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def search_files(directories=None, extension=''):
    if directories is None:
        directories = ['.']
    directory: Union[str, Any]
    for directory in directories:
        if not os.path.exists(directory):
            continue
        # file_list = []
        # extension = extension.lower()
        for dir_path, dir_names, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(dir_path, file_name)
                statistics = os.stat(file_path)
                fhash = file_hash(file_path)
                if fhash in all_files:
                    print(file_path)
                    all_files[fhash].append(file_path)
                else:
                    all_files[fhash] = [file_path]


try:
    search_files(directories=['/mnt/MEDIA', '/mnt/onethreesix'])
# all_files = search_files()
except KeyboardInterrupt as e:
    print(all_files)
    with open('all_files.json', 'w') as fh:
        fh.write(json.dumps(all_files,indent=2))
    exit(0)

print(all_files)
with open('all_files.json', 'w') as fh:
    fh.write(json.dumps(all_files, indent=2))
