#!/usr/bin/env python
# coding=utf-8

import collections

try:
    fh = open("Books_sums.txt")
except IOError as e:
    print("e:", e)
except Exception as e:
    print("boo:", e)

seen = set()
uniq = []

data = []
dups = []

for line in fh.readlines():
    cksum, path = line.split(" ", 1)
    path = path.strip()
    data.append((cksum,path))

d = collections.defaultdict(list)
for cksum, path in data:
    d[cksum].append(path)

delete_list = []
fh = open("delete_list.sh","w")
fh.write("rm -f \\\n")
for a, b in list(d.items()):
    if len(b) > 1:
        print(a)
        cnt = 0
        for thingy in b:
            print(cnt, "  ", thingy)
            cnt += 1
        choice = input("> ")
        if choice.isdigit():
            choice = int(choice)
        else:
            next

        if choice >= 0 and choice <= (len(b)-1):
            delete_list.append(b[choice])
            fh.write('"'+b[choice]+'"'+" \\\n")
            print("You selected:", b[choice])
        else:
            print("None will be appended.")

fh.close()

