#!/usr/bin/env python3

# <xbar.title>Disk Usage</xbar.title>
# <xbar.version>v0.5.3</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show disk usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(EXTENDED_DETAILS_ENABLED=true): Show extended information about the specified mountpoint</xbar.var>
# <xbar.var>string(MOUNTPOINT=/): A valid mountpoint</xbar.var>
# <xbar.var>string(UNIT=auto): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei, auto]</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[DEBUG_ENABLED=false, EXTENDED_DETAILS_ENABLED=true, MOUNTPOINT=/, UNIT=auto]</swiftbar.environment>

from collections import OrderedDict
from swiftbar.plugin import Plugin
from swiftbar import util
import shutil

def main() -> None:
    plugin = Plugin(disable_brew=True)
    partitions = util.find_partitions()
    plugin.defaults_dict['EXTENDED_DETAILS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--extended-details',
            'title': 'extended mountpoint details',
        },
    }
    plugin.defaults_dict['MOUNTPOINT'] = {
        'default_value': '/',
        'valid_values': [partition.mountpoint for partition in partitions],
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--mountpoint',
            'title': 'Mountpoint',
        },
    }
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
    plugin.defaults_dict['OUTPUT_FORMAT'] = {
        'default_value': 'Used / Total',
        'valid_values': [
            'Used / Total',
            '% Used',
            '% Free',
        ],
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--output-format',
            'title': 'Output format',
        },
    }
    plugin.setup()

    partition = next((p for p in partitions if p.mountpoint == plugin.configuration['MOUNTPOINT']), None)
    try:
        total, used, _ = shutil.disk_usage(plugin.configuration['MOUNTPOINT'])
        if total and used:
            free = total - used
            total_str = util.format_number(total) if plugin.configuration['UNIT'] == 'auto' else util.byte_converter(total, plugin.configuration['UNIT'])
            used_str = util.format_number(used) if plugin.configuration['UNIT'] == 'auto' else util.byte_converter(used, plugin.configuration['UNIT'])
            free_str = util.format_number(free) if plugin.configuration['UNIT'] == 'auto' else util.byte_converter(used, plugin.configuration['UNIT'])
            percent_used = util.float_to_pct(used/total)
            percent_free = util.float_to_pct(free/total)
            if plugin.configuration['OUTPUT_FORMAT'] == 'Used / Total':
                title_text = f'{used_str} / {total_str}'
            elif plugin.configuration['OUTPUT_FORMAT'] == '% Used':
                title_text = f'{percent_used} used'
            elif plugin.configuration['OUTPUT_FORMAT'] == '% Free':
                title_text = f'{percent_free} free'
            plugin.print_menu_title(f'Disk: {plugin.configuration["MOUNTPOINT"]} {title_text}')
            if plugin.configuration['EXTENDED_DETAILS_ENABLED']:
                plugin.print_menu_separator()
                mountpoint_output = OrderedDict()
                mountpoint_output['mountpoint'] = partition.mountpoint
                mountpoint_output['device'] = partition.device
                mountpoint_output['type'] = partition.fstype
                mountpoint_output['options'] = ','.join(partition.opts)
                plugin.print_ordered_dict(mountpoint_output, justify='left', indent=0)
    except:
        plugin.print_menu_title('Disk: Not found')
    plugin.render_footer()

if __name__ == '__main__':
    main()
