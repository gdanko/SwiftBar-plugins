#!/usr/bin/env python3

# <xbar.title>Swap Usage</xbar.title>
# <xbar.version>v0.5.2</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system swap usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-SwapUsage.2s.py</xbar.abouturl>
# <xbar.var>string(UNIT=auto): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei, auto]</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[UNIT=auto]</swiftbar.environment>

from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import NamedTuple, Union
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
    plugin = Plugin()
    plugin.defaults_dict['UNIT'] = {
        'default_value': 'auto',
        'valid_values': util.valid_storage_units(),
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--unit',
            'title': 'Unit',
        },
    }
    plugin.setup()

    swap = get_swap_usage()
    if swap:
        used = util.format_number(swap.used) if plugin.configuration['UNIT'] == 'auto' else util.byte_converter(swap.used, plugin.configuration['UNIT'])
        total = util.format_number(swap.total) if plugin.configuration['UNIT'] == 'auto' else util.byte_converter(swap.total, plugin.configuration['UNIT'])
        plugin.print_menu_title(f'Swap: {used} / {total}')
    else:
        plugin.print_menu_title('Swap: Failed')
        plugin.print_menu_item('Failed to gather swap information')
    plugin.render_footer()

if __name__ == '__main__':
    main()
