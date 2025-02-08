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

from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import Dict, List, NamedTuple, Union
import json

class Package(NamedTuple):
    CurrentVersion: str
    InstalledVersions: List[str]
    Name: str

def get_brew_data() -> Union[None, str, Dict[str, List[Package]]]:
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
        formulae: List[Package] = []
        casks: List[Package] = []
        data = json.loads(stdout)
        for obj in data['formulae']:
            if obj['name'] in manually_installed:
                formulae.append(
                    Package(
                        Name=obj['name'],
                        CurrentVersion=obj['current_version'],
                        InstalledVersions=obj['installed_versions'],
                    )
                )
        for obj in data['casks']:
            casks.append(
                Package(
                    Name=obj['name'],
                    CurrentVersion=obj['current_version'],
                    InstalledVersions=obj['installed_versions'],
                )
            )

        if type(formulae) == list and type(casks) == list:
            return {'Formulae': formulae, 'Casks': casks}, None
        else:
            return None, 'Invalid data returned from brew'
    except Exception as e:
        return None, f'Failed to parse JSON output from "{command}": {e}'

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
                longest_name_length = max(len(formula.Name) for formula in formulae)
                plugin.print_menu_separator()
                plugin.print_menu_item(key)
                for formula in formulae:
                    plugin.print_menu_item(
                        f'Update {formula.Name:<{longest_name_length}}    {sorted(formula.InstalledVersions)[-1].rjust(7)} > {formula.CurrentVersion}',
                        cmd=['brew', 'upgrade', formula.Name],
                        refresh=True,
                        sfimage='shippingbox',
                        terminal=True,
                    )
    plugin.render_footer()

if __name__ == '__main__':
    main()
