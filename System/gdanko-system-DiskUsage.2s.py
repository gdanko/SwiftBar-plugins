#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show disk usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_DISK_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>
# <xbar.var>string(VAR_DISK_MOUNTPOINTS="/"): A comma-delimited list of mount points</xbar.var>

import os
import re
import shutil

def pad_float(number):
   return '{:.2f}'.format(float(number))

def get_defaults():
    mountpoints = os.getenv('VAR_DISK_MOUNTPOINTS', '/')
    mountpoints_list = re.split(r'\s*,\s*', mountpoints)

    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    unit = os.getenv('VAR_DISK_USAGE_UNIT', 'Gi')
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
    try:
        from psutil import disk_partitions

        output = []
        partition_data = {}
        valid_mountpoints = []
        mountpoints_list, unit = get_defaults()

        partitions = disk_partitions()
        for partition in partitions:
            partition_data[partition.mountpoint] = partition

        for mountpoint in mountpoints_list:
            total, used, free = shutil.disk_usage(mountpoint)
            if total and used:
                valid_mountpoints.append(mountpoint)
                total = byte_converter(total, unit)
                used = byte_converter(used, unit)
                output.append(f'"{mountpoint}" {used} / {total}')

        if len(output) > 0:
            print(f'Disk: {"; ".join(output)}')
            print('---')
            for valid_mountpoint in valid_mountpoints:
                print(valid_mountpoint)
                print(f'--mountpoint: {partition_data[valid_mountpoint].mountpoint}')
                print(f'--device: {partition_data[valid_mountpoint].device}')
                print(f'--type: {partition_data[valid_mountpoint].fstype}')
                print(f'--options: {partition_data[valid_mountpoint].opts}')
        else:
            print('Disk: Not found')

    except ModuleNotFoundError:
        print('Error: missing "psutil" library.')
        print('---')
        import sys
        import subprocess
        subprocess.run('pbcopy', universal_newlines=True,
                       input=f'{sys.executable} -m pip install psutil')
        print('Fix copied to clipboard. Paste on terminal and run.')
if __name__ == '__main__':
    main()
