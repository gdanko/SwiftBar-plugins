#!/usr/bin/env python3

# <xbar.title>Swap Usage</xbar.title>
# <xbar.version>v0.5.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system swap usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-SwapUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_SWAP_USAGE_DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_SWAP_USAGE_UNIT=auto): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei, auto]</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_SWAP_USAGE_DEBUG_ENABLED=false, VAR_SWAP_USAGE_UNIT=auto]</swiftbar.environment>

from collections import OrderedDict
from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import NamedTuple, Union
import os
import re

class SwapUsage(NamedTuple):
    total: int
    free: int
    used: int

def get_swap_usage() -> Union[SwapUsage, None]:
    output = util.get_sysctl('vm.swapusage')
    if output:
        match = re.search(r'^total = (\d+\.\d+)M\s+used = (\d+\.\d+)M\s+free = (\d+\.\d+)M\s+', output)
        if match:
            total = int(float(match.group(1))) * 1024 * 1024
            used = int(float(match.group(2))) * 1024 * 1024
            free = int(float(match.group(3))) * 1024 * 1024
            return SwapUsage(total=total, free=free, used=used)
    return None

def main() -> None:
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    plugin.defaults_dict = OrderedDict()
    plugin.defaults_dict['VAR_SWAP_USAGE_DEBUG_ENABLED'] = {
        'default_value': False,
        'valid_values': [True, False],
        'setting_configuration': {
            'default': False,
            'flag': '--debug',
            'help': 'Toggle the Debugging menu',
            'title': 'the "Debugging" menu',
            'type': bool,
        },
    }
    plugin.defaults_dict['VAR_SWAP_USAGE_UNIT'] = {
        'default_value': 'auto',
        'valid_values': util.valid_storage_units(),
        'setting_configuration': {
            'default': False,
            'flag': '--unit',
            'help': 'The unit to use',
            'title': 'Unit',
            'type': str,
        },
    }
    plugin.read_config()
    plugin.generate_args()
    if plugin.args.debug:
        plugin.update_setting('VAR_SWAP_USAGE_DEBUG_ENABLED', True if plugin.configuration['VAR_SWAP_USAGE_DEBUG_ENABLED'] == False else False)
    elif plugin.args.unit:
        plugin.update_setting('VAR_SWAP_USAGE_UNIT', plugin.args.unit)

    plugin.read_config()
    debug_enabled = plugin.configuration['VAR_SWAP_USAGE_DEBUG_ENABLED']
    unit = plugin.configuration['VAR_SWAP_USAGE_UNIT']

    swap = get_swap_usage()
    if swap:
        used = util.format_number(swap.used) if unit == 'auto' else util.byte_converter(swap.used, unit)
        total = util.format_number(swap.total) if unit == 'auto' else util.byte_converter(swap.total, unit)
        plugin.print_menu_title(f'Swap: {used} / {total}')
    else:
        plugin.print_menu_title('Swap: Failed')
        plugin.print_menu_item('Failed to gather swap information')
    if plugin.defaults_dict:
        plugin.display_settings_menu()
    if debug_enabled:
        plugin.display_debugging_menu()
    plugin.print_menu_item('Refresh', refresh=True)

if __name__ == '__main__':
    main()
