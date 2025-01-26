#!/usr/bin/env python3

# <xbar.title>System Updates</xbar.title>
# <xbar.version>v0.3.1</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number of available system updates</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-SystemUpdates.15m.py</xbar.abouturl>

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
from pprint import pprint

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args

def get_update_tuple(label=None, title=None, version=None, size=0, recommended=False, action=None):
    system_update = namedtuple('system_update', 'label title version size recommended action')
    return system_update(label=label, title=title, version=version, size=size, recommended=recommended, action=action)

def generate_update_tuple(entry: tuple) ->tuple:
    items = re.split(r'\s*,\s*', entry[1].strip().rstrip(','))
    attributes = dict(re.split(r'\s*:\s*', pair) for pair in items)
    attributes = {k.lower(): v for k, v in attributes.items()}
    if 'size' in attributes:
        match = re.search(r'(\d+)', attributes['size'])
        if match:
            attributes['size'] = match.group(1)
    attributes['title'] = attributes['title'].replace(attributes['version'], '', -1).strip()
 
    return get_update_tuple(
        label=entry[0],
        title=attributes['title'],
        version=attributes['version'],
        size=attributes['size'],
        recommended=(True if attributes['recommended'].lower() == 'yes' else False),
        action=(attributes['action'].title() if 'action' in attributes else 'N/A'),
    )

def find_software_updates():
    updates = []
    returncode, stdout, stderr = util.execute_command('softwareupdate --list')
    if returncode == 0 and stdout:
        pattern = r'\* Label:\s*(.*)\n\s*(.*)'
        matches = re.findall(pattern, stdout)
        if matches:
            for match in matches:
                if len(match) == 2:
                    update_tuple = generate_update_tuple(match)
                    if str(type(update_tuple)) == "<class '__main__.system_update'>":
                        updates.append(update_tuple)
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
        longest = max(len(item.title) for item in updates)
        for update in updates:
            plugin.print_menu_item(
                f'{update.title.ljust(longest)}  {update.version}',
                cmd=['softwareupdate', '--install', f'"{update.label}"'],
                refresh=True,
                sfimage='shippingbox',
                terminal=True,
                trim=False,
            )
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
