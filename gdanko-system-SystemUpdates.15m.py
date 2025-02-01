#!/usr/bin/env python3

# <xbar.title>System Updates</xbar.title>
# <xbar.version>v0.4.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number of available system updates</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-SystemUpdates.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_SYSTEM_UPDATES_DEBUG_ENABLED=false): Show debugging menu</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_SYSTEM_UPDATES_DEBUG_ENABLED=false]</swiftbar.environment>

from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import NamedTuple, Tuple, Union
import os
import re

class SystemUpdate(NamedTuple):
    label: str
    title: str
    version: str
    size: int
    recommended: bool
    action: str

def generate_update_data(entry: Tuple=None) -> SystemUpdate:
    items = re.split(r'\s*,\s*', entry[1].strip().rstrip(','))
    attributes = dict(re.split(r'\s*:\s*', pair) for pair in items)
    attributes = {k.lower(): v for k, v in attributes.items()}
    if 'size' in attributes:
        match = re.search(r'(\d+)', attributes['size'])
        if match:
            attributes['size'] = int(match.group(1))
    attributes['title'] = attributes['title'].replace(attributes['version'], '', -1).strip()
 
    return SystemUpdate(
        label=entry[0],
        title=attributes['title'],
        version=attributes['version'],
        size=attributes['size'],
        recommended=(True if attributes['recommended'].lower() == 'yes' else False),
        action=(attributes['action'].title() if 'action' in attributes else 'N/A'),
    )

def find_software_updates() -> Union[list[SystemUpdate], str, None]:
    updates = []
    returncode, stdout, stderr = util.execute_command('softwareupdate --list')
    if returncode == 0 and stdout:
        pattern = r'\* Label:\s*(.*)\n\s*(.*)'
        matches = re.findall(pattern, stdout)
        if matches:
            for match in matches:
                if len(match) == 2:
                    update_data = generate_update_data(match)
                    if type(update_data) == SystemUpdate:
                        updates.append(update_data)
        return updates, None
    else:
        return updates, stderr

def main() -> None:
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_SYSTEM_UPDATES_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
            'setting_configuration': {
                'default': False,
                'flag': '--debug',
                'help': 'Toggle the Debugging menu',
                'type': bool,
            },
        },
    }
    plugin.read_config(defaults_dict)
    args = util.generate_args(defaults_dict)
    if args.debug:
        plugin.update_setting('VAR_SYSTEM_UPDATES_DEBUG_ENABLED', True if plugin.configuration['VAR_SYSTEM_UPDATES_DEBUG_ENABLED'] == False else False)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_SYSTEM_UPDATES_DEBUG_ENABLED']
    updates, err = find_software_updates()
    if err:
        plugin.print_menu_title('Updates: Error')
        plugin.print_menu_item(err)
    else:
        plugin.print_menu_title(f'Updates: {len(updates)}')
        if len(updates) > 0:
            longest = plugin.find_longest(updates)
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
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} "Debugging" menu',
        cmd=[plugin.plugin_name, '--debug'],
        terminal=False,
        refresh=True,
    )
    if debug_enabled:
        plugin.display_debugging_menu()
    plugin.print_menu_item('Refresh system update data', refresh=True)
    
if __name__ == '__main__':
    main()
