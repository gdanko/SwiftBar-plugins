#!/usr/bin/env python3

from pprint import pprint
import re
import subprocess

def get_command_output(command):
    previous = None
    for command in re.split(r'\s*\|\s*', command):
        cmd = re.split(r'\s+', command)
        # stdin = previous.stdout if previous else None
        p = subprocess.Popen(cmd, stdin=(previous.stdout if previous else None), stdout=subprocess.PIPE)
        previous = p
    return p.stdout.read().strip().decode()

command = '/bin/ps -axm -o %cpu,pid,user,comm | /usr/bin/tail -n+2 | /usr/bin/sort -rn -k 1'
print(get_command_output(command))
