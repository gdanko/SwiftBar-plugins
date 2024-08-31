#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>This plugin shows memery usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-MemoryUsage.5s.py</xbar.abouturl>
# <xbar.var>string(VAR_MEM_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>
# <xbar.var>string(VAR_DISK_MOUNT_POINTS=/): A comma-delimited list of mount points</xbar.var>

import os
import re
import shutil

def pad_float(number):
   return '{:.2f}'.format(float(number))

def get_defaults():
    default_mount_points = '/'
    mount_points = os.getenv('VAR_DISK_MOUNT_POINTS', default_mount_points)
    
    if mount_points == '':
        mount_points = default_mount_points
    mount_points_list = re.split(r'\s*,\s*', mount_points)

    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    default_unit = 'Gi'
    unit = os.getenv('VAR_MEM_USAGE_UNIT', default_unit)
    
    if unit != '':
        if not unit in valid_units:
            unit = default_unit
    else:
        unit = default_unit
    
    return mount_points_list, unit

def byte_converter(bytes, unit):
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{pad_float(bytes / (divisor ** prefix_map[prefix]))} {unit}{suffix}'

def main():
    output = []
    mount_points_list, unit = get_defaults()

    for mount_point in mount_points_list:
        total, used, free = shutil.disk_usage(mount_point)
        if total and used:
            total = byte_converter(total, unit)
            used = byte_converter(used, unit)
            output.append(f'"{mount_point}" {used} / {total}')

    if len(output) > 0:
        print(f'Disk: {"; ".join(output)}')
    else:
        print('Disk: Not found')

if __name__ == '__main__':
    main()
