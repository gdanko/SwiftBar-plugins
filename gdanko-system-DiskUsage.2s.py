#!/usr/bin/env python3

# <xbar.title>Disk Usage</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show disk usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_DISK_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>
# <xbar.var>string(VAR_DISK_USAGE_MOUNTPOINTS="/"): A comma-delimited list of mount points</xbar.var>

# "Run in Terminal..."" currently uses the default values, not reading the config file

from collections import namedtuple
from swiftbar.plugin import Plugin
from swiftbar import util
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
    returncode, stdout, _ = plugin.execute_command('mount')
    if returncode == 0:
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

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_DISK_USAGE_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_DISK_USAGE_MOUNTPOINTS': {
            'default_value': '/',
            'split_value': True,
        },
        'VAR_DISK_USAGE_UNIT': {
            'default_value': 'Gi',
            'valid_values': ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei'],
        },
    }
    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_DISK_USAGE_DEBUG_ENABLED']
    mountpoints_list = re.split(r'\s*,\s*', plugin.configuration['VAR_DISK_USAGE_MOUNTPOINTS'])
    unit = plugin.configuration['VAR_DISK_USAGE_UNIT']

    plugin_output = []
    partition_data = {}
    valid_mountpoints = []
    partitions = get_partition_info()

    for partition in partitions:
        partition_data[partition.mountpoint] = partition

    for mountpoint in mountpoints_list:
        try:
            total, used, _ = shutil.disk_usage(mountpoint)
            if total and used:
                valid_mountpoints.append(mountpoint)
                total = util.byte_converter(total, unit)
                used = util.byte_converter(used, unit)
                plugin_output.append(f'"{mountpoint}" {used} / {total}')
        except:
            pass

    if len(plugin_output) > 0:
        plugin.print_menu_item(f'Disk: {"; ".join(plugin_output)}')
        plugin.print_menu_separator()
        plugin.print_menu_item(f'Updated {util.get_timestamp(int(time.time()))}')
        plugin.print_menu_separator()
        for valid_mountpoint in valid_mountpoints:
            print(valid_mountpoint)
            print(f'--mountpoint: {partition_data[valid_mountpoint].mountpoint}')
            print(f'--device: {partition_data[valid_mountpoint].device}')
            print(f'--type: {partition_data[valid_mountpoint].fstype}')
            print(f'--options: {partition_data[valid_mountpoint].opts}')
    else:
        plugin.print_menu_item('Disk: Not found')
    if debug_enabled:
        plugin.display_debug_data()

if __name__ == '__main__':
    main()
