#!/usr/bin/env python3

# <xbar.title>System Updates</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number of available system updates</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-SystemUpdates.15m.py</xbar.abouturl>

from collections import namedtuple, OrderedDict
from swiftbar import util
from swiftbar.plugin import Plugin
import argparse
import os
import re
import time
from pprint import pprint

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args

def get_update_tuple(title=None, version=None, size=0, recommended=False, action=None):
    update = namedtuple('update', 'title version size recommended action')
    return update(title=title, version=version, size=size, recommended=recommended, action=action)

def find_software_updates():
    updates = []
    returncode, stdout, stderr = util.execute_command('softwareupdate --list')
    if returncode == 0 and stdout:
        pattern = r'Title.*'
        matches = re.findall(pattern, stdout)
        if matches:
            for match in matches:
                match = match.strip().rstrip(',')
                update_dict = {}
                match_bits = re.split(r'\s*,\s*', match)
                for match_bit in match_bits:
                    item_bits = re.split(r'\s*:\s', match_bit)
                    key = item_bits[0]
                    value = item_bits[1]
                    if key == 'Size':
                        match = re.search(r'(\d+)', value)
                        if match:
                            value = int(match.group(1))
                    update_dict[key.lower()] = value
                updates.append(get_update_tuple(
                    title=update_dict['title'],
                    version=update_dict['version'],
                    size=update_dict['size'],
                    recommended=(True if update_dict['recommended'].lower() == 'yes' else False),
                    action=(update_dict['action'].title() if 'action' in update_dict else 'N/A'),
                ))
        return updates, None
    else:
        return updates, stderr

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_SYSTEM_UPDATES_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
    }
    plugin.read_config(defaults_dict)
    args = configure()
    if args.debug:
        plugin.update_setting('VAR_SYSTEM_UPDATES_DEBUG_ENABLED', True if plugin.configuration['VAR_SYSTEM_UPDATES_DEBUG_ENABLED'] == False else False)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_SYSTEM_UPDATES_DEBUG_ENABLED']
    updates, error = find_software_updates()
    if len(updates) > 0:
        plugin.print_menu_title(f'Updates: {len(updates)}')
        plugin.print_menu_separator()
        plugin.print_update_time()
        plugin.print_menu_separator()
        update_output = OrderedDict()
        for update in updates:
            update_output[update.title] = update.version
        plugin.print_ordered_dict(update_output, justify='left', delimiter='', sfimage='shippingbox')
        plugin.print_menu_separator()
    else:
        plugin.print_menu_title('Updates: Unknown')
        plugin.print_menu_separator()
        # Need to capture the error
        plugin.print_menu_title('Failed to find update count')
    plugin.print_menu_separator()
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} debug data',
        cmd=[plugin.plugin_name, '--debug'],
        terminal=False,
        refresh=True,
    )
    if debug_enabled:
        plugin.display_debug_data()
    plugin.print_menu_item('Refresh system update data', refresh=True)
    
if __name__ == '__main__':
    main()
