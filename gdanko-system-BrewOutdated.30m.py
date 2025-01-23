#!/usr/bin/env python3

# <xbar.title>BrewOutdated</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number upgradeable Homebrew packages</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-BrewOutdated.30m.py</xbar.abouturl>

from dataclasses import dataclass
import json
import os
import plugin
import shutil

from pprint import pprint

@dataclass
class Package:
    def __init__(self, name: str, current_version: str, installed_versions: list, **_: object):
        self.name = name
        self.current_version = current_version
        self.installed_version = installed_versions[0]

def get_brew_data():
    if not shutil.which('brew'):
        return None, 'Homebrew isn\'t installed'

    command = 'brew update'
    retcode, _, _ = plugin.execute_command(command)
    if retcode > 0:
        return None, f'Failed to execute "{command}"'
    
    command = 'brew list --installed-on-request'
    retcode, stdout, _ = plugin.execute_command(command)
    if retcode > 0:
        return None, f'Failed to execute "{command}"'
    manually_installed = {line for line in stdout.splitlines()}

    command = 'brew outdated --json'
    retcode, stdout, _ = plugin.execute_command(command)
    if retcode > 0:
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
    os.environ['PATH'] = '/opt/homebrew/bin:/opt/homebrew/sbin:/bin:/sbin:/usr/bin:/usr/sbin'
    invoker, _ = plugin.get_config_dir()
    invoker = 'SwiftBar'
    if invoker == 'SwiftBar':
        data, err = get_brew_data()
        if err:
            plugin.print_menu_title(title='Brew Outdated: Failure')
            plugin.print_menu_separator()
            plugin.print_menu_item(err, font='AndaleMono', size=13)
        else:
            total = len(data['Formulae']) + len(data['Casks'])
            plugin.print_menu_title(title=f'Brew Outdated: {total}')
            print()
            if total > 0:
                plugin.print_menu_separator()
                plugin.print_menu_item(
                    f'Update {total} package(s)',
                    cmd=['brew', 'upgrade'],
                    font='AndaleMono',
                    refresh=True,
                    sfimage='arrow.up.square',
                    size=13, 
                    terminal=True,
                )
            for key, formulae in data.items():
                if len(formulae) > 0:
                    longest_name_length = max(len(formula.name) for formula in formulae)
                    plugin.print_menu_separator()
                    plugin.print_menu_item(key, font='AndaleMono', size=13)
                    for formula in formulae:
                        plugin.print_menu_item(
                            f'Update {formula.name:<{longest_name_length}}    {formula.installed_version.rjust(7)} > {formula.current_version}',
                            cmd=['brew', 'upgrade', formula.name],
                            font='AndaleMono',
                            refresh=True,
                            sfimage='shippingbox',
                            size=13,
                            terminal=True,
                        )
        plugin.print_menu_separator()
        plugin.print_menu_item('Refresh', font='AndaleMono', size=13, refresh=True)
    elif invoker == 'xbar':
        plugin.print_menu_title(title='Brew Outdated: Failure')
        plugin.print_menu_separator()
        plugin.print_menu_item('I do not yet support xbar')

if __name__ == '__main__':
    main()
