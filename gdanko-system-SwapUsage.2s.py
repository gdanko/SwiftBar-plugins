#!/usr/bin/env python3

# <xbar.title>Swap Usage</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system swap usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-SwapUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_SWAP_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

from collections import namedtuple
from swiftbar import util
from swiftbar.plugin import Plugin
import argparse
import os
import re

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    parser.add_argument('--unit', help='Select the unit to use', required=False)
    args = parser.parse_args()
    return args

def get_swap_usage_tuple(total=0, used=0, free=0):
    swap_usage = namedtuple('swap_usage', 'total free used')
    return swap_usage(total=total, free=free, used=used)

def get_swap_usage():
    output = util.get_sysctl('vm.swapusage')
    if output:
        match = re.search(r'^total = (\d+\.\d+)M\s+used = (\d+\.\d+)M\s+free = (\d+\.\d+)M\s+', output)
        if match:
            total = int(float(match.group(1))) * 1024 * 1024
            used = int(float(match.group(2))) * 1024 * 1024
            free = int(float(match.group(3))) * 1024 * 1024
            return get_swap_usage_tuple(total=total, free=free, used=used)
    return None

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_SWAP_USAGE_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_SWAP_USAGE_UNIT': {
            'default_value': 'Gi',
            'valid_values': util.valid_storage_units(),
        },
    }
    plugin.read_config(defaults_dict)
    args = configure()
    if args.debug:
        plugin.update_setting('VAR_SWAP_USAGE_DEBUG_ENABLED', True if plugin.configuration['VAR_SWAP_USAGE_DEBUG_ENABLED'] == False else False)
    elif args.unit:
        plugin.update_setting('VAR_SWAP_USAGE_UNIT', args.unit)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_SWAP_USAGE_DEBUG_ENABLED']
    unit = plugin.configuration['VAR_SWAP_USAGE_UNIT']

    swap = get_swap_usage()
    if swap:
        used = util.byte_converter(swap.used, unit)
        total = util.byte_converter(swap.total, unit)
        plugin.print_menu_title(f'Swap: {used} / {total}')
    else:
        plugin.print_menu_title('Swap: Failed')
        plugin.print_menu_separator()
        plugin.print_menu_item('Failed to gather swap information')
    plugin.print_menu_separator()
    plugin.print_update_time()
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} debug data',
        cmd=[plugin.plugin_name, '--debug'],
        terminal=False,
        refresh=True,
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

if __name__ == '__main__':
    main()
