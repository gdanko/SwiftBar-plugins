#!/usr/bin/env python3

# <xbar.title>Disk Usage</xbar.title>
# <xbar.version>v0.5.3</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show disk usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_DISK_USAGE_EXTENDED_DETAILS_ENABLED=true): Show extended information about the specified mountpoint</xbar.var>
# <xbar.var>string(VAR_DISK_USAGE_MOUNTPOINT=/): A valid mountpoint</xbar.var>
# <xbar.var>string(VAR_DISK_USAGE_UNIT=auto): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei, auto]</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[DEBUG_ENABLED=false, VAR_DISK_USAGE_EXTENDED_DETAILS_ENABLED=true, VAR_DISK_USAGE_MOUNTPOINT=/, VAR_DISK_USAGE_UNIT=auto]</swiftbar.environment>

from collections import OrderedDict
from swiftbar.plugin import Plugin
from swiftbar import images, util
from typing import List, NamedTuple
import re
import shutil

class MountpointData(NamedTuple):
    device: str
    mountpoint: str
    fstype: str
    opts: list[str]

def get_partition_info() -> List[MountpointData]:
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
                opts = opts_list[1:]
                partitions.append(MountpointData(device=device, mountpoint=mountpoint, fstype=fstype, opts=opts))
    return partitions

def main() -> None:
    plugin = Plugin(no_brew=True)
    partitions = get_partition_info()
    valid_mountpoints = [partition.mountpoint for partition in partitions]
    plugin.defaults_dict = OrderedDict()
    plugin.defaults_dict['DEBUG_ENABLED'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': None,
            'flag': '--debug',
            'title': 'the "Debugging" menu',
        },
    }
    plugin.defaults_dict['VAR_DISK_USAGE_EXTENDED_DETAILS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--extended-details',
            'title': 'extended mountpoint details',
        },
    }
    plugin.defaults_dict['VAR_DISK_USAGE_MOUNTPOINT'] = {
        'default_value': '/',
        'valid_values': valid_mountpoints,
        'type': str,
        'setting_configuration': {
            'default': False,
            'flag': '--mountpoint',
            'title': 'Mountpoint',
        },
    }
    plugin.defaults_dict['VAR_DISK_USAGE_UNIT'] = {
        'default_value': 'auto',
        'valid_values': util.valid_storage_units(),
        'type': str,
        'setting_configuration': {
            'default': False,
            'flag': '--unit',
            'title': 'Unit',
        },
    }

    plugin.read_config()
    plugin.generate_args()
    plugin.update_json_from_args()

    partition = next((p for p in partitions if p.mountpoint == plugin.configuration['VAR_DISK_USAGE_MOUNTPOINT']), None)
    try:
        total, used, _ = shutil.disk_usage(plugin.configuration['VAR_DISK_USAGE_MOUNTPOINT'])
        if total and used:
            total = util.format_number(total) if plugin.configuration['VAR_DISK_USAGE_UNIT'] == 'auto' else util.byte_converter(total, plugin.configuration['VAR_DISK_USAGE_UNIT'])
            used = util.format_number(used) if plugin.configuration['VAR_DISK_USAGE_UNIT'] == 'auto' else util.byte_converter(used, plugin.configuration['VAR_DISK_USAGE_UNIT'])
            plugin.print_menu_title(f'Disk: "{plugin.configuration["VAR_DISK_USAGE_MOUNTPOINT"]}" {used} / {total}')
            if plugin.configuration['VAR_DISK_USAGE_EXTENDED_DETAILS_ENABLED']:
                plugin.print_menu_separator()
                mountpoint_output = OrderedDict()
                mountpoint_output['mountpoint'] = partition.mountpoint
                mountpoint_output['device'] = partition.device
                mountpoint_output['type'] = partition.fstype
                mountpoint_output['options'] = ','.join(partition.opts)
                plugin.print_ordered_dict(mountpoint_output, justify='left', indent=0)
    except:
        plugin.print_menu_item('Disk: Not found')
    plugin.render_footer()

if __name__ == '__main__':
    main()
