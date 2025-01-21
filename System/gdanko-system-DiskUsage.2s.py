#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show disk usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_DISK_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>
# <xbar.var>string(VAR_DISK_MOUNTPOINTS="/"): A comma-delimited list of mount points</xbar.var>

# "Run in Terminal..."" currently uses the default values, not reading the config file

from collections import namedtuple
from pathlib import Path
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time

def get_command_output(command):
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    return stdout.strip().decode(), stderr.strip().decode()

def get_config_dir():
    ppid = os.getppid()
    stdout, stderr = get_command_output(f'/bin/ps -o command -p {ppid} | tail -n+2')
    if stderr:
        return None
    if stdout:
        if stdout == '/Applications/xbar.app/Contents/MacOS/xbar':
            return os.path.dirname(os.path.abspath(sys.argv[0]))
        elif stdout == '/Applications/SwiftBar.app/Contents/MacOS/SwiftBar':
            return os.path.join(Path.home(), '.config', 'SwiftBar')
    return Path.home()

def get_partion_tuple(device=None, mountpoint=None, fstype=None, opts=None):
    sdiskpart = namedtuple('sdiskpart', 'device mountpoint fstype opts')
    return sdiskpart(device=device, mountpoint=mountpoint, fstype=fstype, opts=opts)

def get_partition_info():
    partitions = []
    stdout, _ = get_command_output('mount')
    if stdout:
        entries = stdout.split('\n')
        for entry in entries:
            match = re.search(r'^(/dev/disk[s0-9]+)\s+on\s+([^(]+)\s+\((.*)\)', entry)
            if match:
                device = match.group(1)
                mountpoint = match.group(2)
                opts_string = match.group(3)
                opts_list = re.split('\s*,\s*', opts_string)
                fstype = opts_list[0]
                opts = ','.join(opts_list[1:])
                partitions.append(get_partion_tuple(device=device, mountpoint=mountpoint, fstype=fstype, opts=opts))
    return partitions

def pad_float(number):
   return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def read_config(vars_file, param, default):
    value = os.environ.get(param)
    if value:
        return value
    if os.path.exists(vars_file):
        with open(vars_file, 'r') as fh:
            contents = json.load(fh)
            if param in contents:
                return contents[param]
    return default

def get_defaults(config_dir, plugin_name):
    vars_file = os.path.join(config_dir, plugin_name) + '.vars.json'
    mountpoints = read_config(vars_file, 'VAR_DISK_MOUNTPOINTS', '/')
    unit = read_config(vars_file, 'VAR_DISK_USAGE_UNIT', 'Gi')

    mountpoints_list = re.split(r'\s*,\s*', mountpoints)
    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    if not unit in valid_units:
        unit = 'Gi'
    return mountpoints_list, unit

def byte_converter(bytes, unit):
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{pad_float(bytes / (divisor ** prefix_map[prefix]))} {unit}{suffix}'

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    config_dir = get_config_dir()
    plugin_name = os.path.abspath(sys.argv[0])
    output = []
    partition_data = {}
    valid_mountpoints = []
    mountpoints_list, unit = get_defaults(config_dir, os.path.basename(plugin_name))
    partitions = get_partition_info()

    for partition in partitions:
        partition_data[partition.mountpoint] = partition

    for mountpoint in mountpoints_list:
        try:
            total, used, free = shutil.disk_usage(mountpoint)
            if total and used:
                valid_mountpoints.append(mountpoint)
                total = byte_converter(total, unit)
                used = byte_converter(used, unit)
                output.append(f'"{mountpoint}" {used} / {total}')
        except:
            pass

    if len(output) > 0:
        print(f'Disk: {"; ".join(output)}')
        print('---')
        print(f'Updated {get_timestamp(int(time.time()))}')
        print('---')
        for valid_mountpoint in valid_mountpoints:
            print(valid_mountpoint)
            print(f'--mountpoint: {partition_data[valid_mountpoint].mountpoint}')
            print(f'--device: {partition_data[valid_mountpoint].device}')
            print(f'--type: {partition_data[valid_mountpoint].fstype}')
            print(f'--options: {partition_data[valid_mountpoint].opts}')
    else:
        print('Disk: Not found')

if __name__ == '__main__':
    main()
