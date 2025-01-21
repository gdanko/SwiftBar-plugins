#!/usr/bin/env python3

# <xbar.title>Disk Usage</xbar.title>
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
import plugin
import re
import shutil
import sys
import time

def get_partion_tuple(device=None, mountpoint=None, fstype=None, opts=None):
    sdiskpart = namedtuple('sdiskpart', 'device mountpoint fstype opts')
    return sdiskpart(device=device, mountpoint=mountpoint, fstype=fstype, opts=opts)

def get_partition_info():
    partitions = []
    stdout, _ = plugin.get_command_output('mount')
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

def get_defaults(config_dir, plugin_name):
    vars_file = os.path.join(config_dir, plugin_name) + '.vars.json'
    mountpoints = plugin.read_config(vars_file, 'VAR_DISK_MOUNTPOINTS', '/')
    unit = plugin.read_config(vars_file, 'VAR_DISK_USAGE_UNIT', 'Gi')

    mountpoints_list = re.split(r'\s*,\s*', mountpoints)
    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    if not unit in valid_units:
        unit = 'Gi'
    return mountpoints_list, unit

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    invoker, config_dir = plugin.get_config_dir()
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
                total = plugin.byte_converter(total, unit)
                used = plugin.byte_converter(used, unit)
                output.append(f'"{mountpoint}" {used} / {total}')
        except:
            pass

    if len(output) > 0:
        print(f'Disk: {"; ".join(output)}')
        print('---')
        print(f'Updated {plugin.get_timestamp(int(time.time()))}')
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
