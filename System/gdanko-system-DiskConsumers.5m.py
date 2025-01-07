#!/usr/bin/env python3

# <xbar.title>Disk Consumers</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show files and directories using the most disk space for a given path</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-DiskConsumers.5m.py</xbar.abouturl>
# <xbar.var>string(VAR_DISK_CONSUMERS_PATHS="/"): A comma-delimited list of mount points</xbar.var>

import datetime
import os
import re
import shutil
import subprocess
import time

def pad_float(number):
   return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def unix_time_in_ms():
    return int(time.time() * 1000)

def get_defaults():
    paths = os.getenv('VAR_DISK_CONSUMERS_PATHS', '~,~/Library')
    paths_list = re.split(r'\s*,\s*', paths)

    return paths_list

def byte_converter(bytes, unit):
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{pad_float(bytes / (divisor ** prefix_map[prefix]))} {unit}{suffix}'

def get_size(path):
    """Returns the size of the file or directory."""
    if os.path.isfile(path):
        return os.path.getsize(path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            total_size += os.path.getsize(os.path.join(dirpath, filename))
    return total_size

def get_command_output(command):
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    return stdout.strip().decode(), stderr.strip().decode()

def get_consumers(path):
    consumers = []
    command = f'{shutil.which("find")} {path} -depth 1 -exec {shutil.which("du")} -sk {{}} \; | {shutil.which("sort")} -rn -k 1'
    output, error = get_command_output(command)
    if output:
        lines = output.strip().split('\n')
        for line in lines:
            match = re.search(r'^(\d+)\s+(.*)$', line)
            if match:
                bytes = int(match.group(1)) * 1024
                path = match.group(2)
                if os.path.basename(path) not in ['.', '..']:
                    if bytes > 0:
                        consumers.append({'path': path.strip(), 'bytes': bytes})

    return sorted(consumers, key=lambda item: item['bytes'], reverse=True)

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
    start_time = unix_time_in_ms()
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    paths_list = get_defaults()
    font_name = 'Andale Mono'
    font_size = 13
    font_data = f'size="{font_size}" font="{font_name}"'

    print('Disk Consumption')
    print('---')
    if len(paths_list) > 0:
        for path in paths_list:
            print(os.path.expanduser(path))
            total = 0
            consumers = get_consumers(path)
            for consumer in consumers:
                bytes = consumer["bytes"]
                path = consumer["path"]
                total += bytes
                max_len = 11
                icon = ':file_folder:' if os.path.isdir(path) else ':page_facing_up:'
                print(f'--{icon}' + f'{format_number(bytes).rjust(max_len)} - {path} | trim=false | {font_data} | shell=/bin/sh | param1="-c" | param2="{shutil.which("open")} {path}"')
            print(f'--Total: {format_number(total)} | {font_data}')
    else:
        print('N/A')
    end_time = unix_time_in_ms()
    print(f'Data fetched at {get_timestamp(int(time.time()))} in {end_time - start_time}ms')
    print('Refresh data | refresh=true')

if __name__ == '__main__':
    main()
