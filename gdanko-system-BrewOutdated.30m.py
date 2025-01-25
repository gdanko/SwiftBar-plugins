#!/usr/bin/env python3

# <xbar.title>BrewOutdated</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number upgradeable Homebrew packages</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-BrewOutdated.30m.py</xbar.abouturl>

from dataclasses import dataclass
from swiftbar import util
from swiftbar.plugin import Plugin
import json
import os
import shutil

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
    retcode, _, _ = util.execute_command(command)
    if retcode > 0:
        return None, f'Failed to execute "{command}"'
    
    command = 'brew list --installed-on-request'
    retcode, stdout, _ = util.execute_command(command)
    if retcode > 0:
        return None, f'Failed to execute "{command}"'
    manually_installed = {line for line in stdout.splitlines()}

    command = 'brew outdated --json'
    retcode, stdout, _ = util.execute_command(command)
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
    plugin = Plugin()
    defaults_dict = {
        'BREW_OUTDATED_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
    }
    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['BREW_OUTDATED_DEBUG_ENABLED']

    if plugin.invoked_by == 'SwiftBar':
        data, err = get_brew_data()
        if err:
            plugin.print_menu_item('Brew Outdated: Failure')
            plugin.print_menu_separator()
            plugin.print_menu_item(err)
        else:
            total = len(data['Formulae']) + len(data['Casks'])
            plugin.print_menu_item(f'Brew Outdated: {total}')
            if total > 0:
                plugin.print_menu_separator()
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
        plugin.print_menu_separator()
        if debug_enabled:
            plugin.display_debug_data()
        plugin.print_menu_item('Refresh', refresh=True)
    elif plugin.invoked_by == 'xbar':
        plugin.print_menu_item(title='Brew Outdated: Failure')
        plugin.print_menu_separator()
        plugin.print_menu_item('I do not yet support xbar')

if __name__ == '__main__':
    main()
