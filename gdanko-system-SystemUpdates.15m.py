#!/usr/bin/env python3

# <xbar.title>System Updates</xbar.title>
# <xbar.version>v0.5.2</xbar.version>
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
# <swiftbar.environment>[]</swiftbar.environment>

from swiftbar import util
from swiftbar.plugin import Plugin
from typing import List, NamedTuple, Tuple, Union
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

def find_software_updates() -> Tuple[Union[List[SystemUpdate]], Union[str, None]]:
    updates: List[SystemUpdate] = []
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
    plugin = Plugin()
    plugin.setup()

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
    plugin.render_footer()
    
if __name__ == '__main__':
    main()
