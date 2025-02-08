#!/usr/bin/env python3

# <xbar.title>BrewOutdated</xbar.title>
# <xbar.version>v0.3.2</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number upgradeable Homebrew packages</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-BrewOutdated.30m.py</xbar.abouturl>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[]</swiftbar.environment>

from dataclasses import dataclass
from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import Dict, Union
import json

@dataclass
class Package:
    def __init__(self, name: str, current_version: str, installed_versions: list, **_: object):
        self.name = name
        self.current_version = current_version
        self.installed_version = installed_versions[0]

def get_brew_data() -> Union[None, str, Dict[str, list[Package]]]:
    if not util.binary_exists('brew'):
        return None, 'Homebrew isn\'t installed'

    command = 'brew update'
    returncode, _, _ = util.execute_command(command)
    if returncode > 0:
        return None, f'Failed to execute "{command}"'
    
    command = 'brew list --installed-on-request'
    returncode, stdout, _ = util.execute_command(command)
    if returncode > 0:
        return None, f'Failed to execute "{command}"'
    manually_installed = {line for line in stdout.splitlines()}

    command = 'brew outdated --json'
    returncode, stdout, _ = util.execute_command(command)
    if returncode > 0:
        return None, f'Failed to execute "{command}"'
    
    try:
        data = json.loads(stdout)
        formulae = [Package(**obj) for obj in data['formulae'] if obj['name'] in manually_installed]
        casks = [Package(**obj) for obj in data['casks']]
        if type(formulae) == list and type(casks) == list:
            return {'Formulae': formulae, 'Casks': casks}, None
        else:
            return None, 'Invalid data returned from brew'
    except:
        return None, f'Failed to parse JSON output from "{command}"'

def main() -> None:
    plugin = Plugin()
    plugin.setup()

    data, err = get_brew_data()
    if err:
        plugin.print_menu_title('Brew Outdated: Failure')
        plugin.print_menu_item(err)
    else:
        total = len(data['Formulae']) + len(data['Casks'])
        plugin.print_menu_title(f'Brew Outdated: {total}')
        if total > 0:
            plugin.print_menu_item(
                f'Update {total} package(s)',
                cmd=['brew', 'upgrade'],
                refresh=True,
                sfimage='arrow.up.square',
                terminal=True,
            )
        for key, formulae in data.items():
            if len(formulae) > 0:
                longest_name_length = max(len(formula.name) for formula in formulae)
                plugin.print_menu_separator()
                plugin.print_menu_item(key)
                for formula in formulae:
                    plugin.print_menu_item(
                        f'Update {formula.name:<{longest_name_length}}    {formula.installed_version.rjust(7)} > {formula.current_version}',
                        cmd=['brew', 'upgrade', formula.name],
                        refresh=True,
                        sfimage='shippingbox',
                        terminal=True,
                    )
    plugin.render_footer()

if __name__ == '__main__':
    main()
