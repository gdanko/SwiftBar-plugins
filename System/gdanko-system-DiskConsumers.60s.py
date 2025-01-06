#!/usr/bin/env python3

# <xbar.title>Disk Consumers</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show files and directories using the most disk space for a given path</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-DiskConsumers.60s.py</xbar.abouturl>
# <xbar.var>string(VAR_DISK_CONSUMERS_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>
# <xbar.var>string(VAR_DISK_CONSUMERS_PATHS="/"): A comma-delimited list of mount points</xbar.var>

import datetime
import os
import re
import shutil
import subprocess
import sys
import time

def pad_float(number):
   return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_defaults():
    paths = os.getenv('VAR_DISK_CONSUMERS_PATHS', '~,~/Library')
    paths_list = re.split(r'\s*,\s*', paths)
    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    unit = os.getenv('VAR_DISK_CONSUMERS_UNIT', 'Mi')
    if not unit in valid_units:
        unit = 'Gi'
    return paths_list, unit

def byte_converter(bytes, unit):
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{pad_float(bytes / (divisor ** prefix_map[prefix]))} {unit}{suffix}'

def get_command_output(command):
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    stdout, stderr = proc.communicate()
    return stdout.strip().decode()

def get_top_consumers(path):
    top_consumers = []
    command = f'/usr/bin/du -sk {path}/* | /usr/bin/sort -rn -k 1'
    output = get_command_output(command)
    if output:
        lines = output.strip().split('\n')
        for line in lines:
            match = re.search(r'^(\d+)\s+(.*)$', line)
            if match:
                bytes = int(match.group(1)) * 1024
                path = match.group(2)
                if bytes > 0:
                    top_consumers.append({'path': path, 'bytes': bytes})
    return top_consumers

def format_number(size):
    factor = 1024
    bytes = factor
    megabytes = bytes * factor
    gigabytes = megabytes * factor
    if size < gigabytes:
        if size < megabytes:
            if size < bytes:
                return f'{size} B'
            else:
                return byte_converter(size, "Ki")
        else:
            return byte_converter(size, "Mi")
    else:
        return byte_converter(size, "Gi")

def main():
    paths_list, unit = get_defaults()

    print('Disk Consumption')
    print('---')
    if len(paths_list) > 0:
        for path in paths_list:
            print(os.path.expanduser(path))
            top_consumers = get_top_consumers(path)
            for top_consumer in top_consumers:
                bytes = top_consumer["bytes"]
                max_len = 11
                print('--' + f'{format_number(bytes).rjust(max_len)} - {top_consumer["path"]} | trim=false | size=14 font="Andale Mono"')
    else:
        print('N/A')
    print('Refresh data | refresh=true')

if __name__ == '__main__':
    main()
