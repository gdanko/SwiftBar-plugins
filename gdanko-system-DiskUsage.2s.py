#!/usr/bin/env python3

# <xbar.title>Disk Usage</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show disk usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_DISK_USAGE_DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_DISK_USAGE_MOUNTPOINT=/): A valid mountpoint</xbar.var>
# <xbar.var>string(VAR_DISK_USAGE_UNIT=auto): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei, auto]</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_DISK_USAGE_DEBUG_ENABLED=false, VAR_DISK_USAGE_MOUNTPOINT=/, VAR_DISK_USAGE_UNIT=auto]</swiftbar.environment>

from collections import namedtuple, OrderedDict
from swiftbar.plugin import Plugin
from swiftbar import util
import argparse
import os
import re
import shutil

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    parser.add_argument('--mountpoint', help='Select the mountpoint to view', required=False)
    parser.add_argument('--unit', help='Select the unit to use', required=False)
    args = parser.parse_args()
    return args

def get_partion_tuple(device=None, mountpoint=None, fstype=None, opts=None):
    sdiskpart = namedtuple('sdiskpart', 'device mountpoint fstype opts')
    return sdiskpart(device=device, mountpoint=mountpoint, fstype=fstype, opts=opts)

def get_partition_info():
    partitions = []
    returncode, stdout, _ = util.execute_command('mount')
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
    partitions = get_partition_info()
    valid_mountpoints = [partition.mountpoint for partition in partitions]
    defaults_dict = {
        'VAR_DISK_USAGE_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_DISK_USAGE_MOUNTPOINT': {
            'default_value': '/',
            'valid_values': ','.join(valid_mountpoints),
        },
        'VAR_DISK_USAGE_UNIT': {
            'default_value': 'auto',
            'valid_values': util.valid_storage_units(),
        },
    }
    plugin.read_config(defaults_dict)
    plugin.invoked_by = 'xbar'
    args = configure()
    if args.debug:
        plugin.update_setting('VAR_DISK_USAGE_DEBUG_ENABLED', True if plugin.configuration['VAR_DISK_USAGE_DEBUG_ENABLED'] == False else False)
    elif args.mountpoint:
        plugin.update_setting('VAR_DISK_USAGE_MOUNTPOINT', args.mountpoint)
    elif args.unit:
        plugin.update_setting('VAR_DISK_USAGE_UNIT', args.unit)
    
    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_DISK_USAGE_DEBUG_ENABLED']
    mountpoint = plugin.configuration['VAR_DISK_USAGE_MOUNTPOINT']
    unit = plugin.configuration['VAR_DISK_USAGE_UNIT']

    partition = next((p for p in partitions if p.mountpoint == mountpoint), None)
    try:
        total, used, _ = shutil.disk_usage(mountpoint)
        if total and used:
            total = util.format_number(total) if unit == 'auto' else util.byte_converter(total, unit)
            used = util.format_number(used) if unit == 'auto' else util.byte_converter(used, unit)
            plugin.print_menu_title(f'Disk: "{mountpoint}" {used} / {total}')
            plugin.print_menu_separator()
            plugin.print_menu_item(mountpoint)
            mountpoint_output = OrderedDict()
            mountpoint_output['mountpoint'] = partition.mountpoint
            mountpoint_output['device'] = partition.device
            mountpoint_output['type'] = partition.fstype
            mountpoint_output['options'] = partition.opts
            plugin.print_ordered_dict(mountpoint_output, justify='left', indent=2)
    except:
        plugin.print_menu_item('Disk: Not found')
    plugin.print_menu_separator()
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} "Debugging" menu',
        cmd=[plugin.plugin_name, '--debug'],
        terminal=False,
        refresh=True,
    )
    plugin.print_menu_item('--Mountpoint')
    for mountpoint_name in valid_mountpoints:
        color = 'blue' if mountpoint_name == mountpoint else 'black'
        plugin.print_menu_item(
            f'----{mountpoint_name}',
            color=color,
            cmd=[plugin.plugin_name, '--mountpoint', f'{mountpoint_name}'],
            refresh=True,
            terminal=False,
        )
    plugin.print_menu_item('--Unit')
    for valid_storage_unit in util.valid_storage_units():
        color = 'blue' if valid_storage_unit == unit else 'black'
        plugin.print_menu_item(
            f'----{valid_storage_unit}',
            color=color,
            cmd=[plugin.plugin_name, '--unit', valid_storage_unit],
            refresh=True,
            terminal=False,
        )
    if debug_enabled:
        plugin.display_debug_data()
    plugin.print_menu_item('Refresh', refresh=True)

if __name__ == '__main__':
    main()
