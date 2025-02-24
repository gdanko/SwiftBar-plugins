#!/usr/bin/env python3

# <xbar.title>RsaToken</xbar.title>
# <xbar.version>v0.3.1</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>fetches current rsa token, and allows you to copy your pin from keychain to your paste buffer</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-RsaToken.10s.py</xbar.abouturl>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[]</swiftbar.environment>

# Credit to Marcus D'Camp for the original, which was a shell script.
# Requirements:
# Set up stoken with your sdtid XML file
# stoken import --file=<PATH_TO_YOUR_SDTID_FILE>
# more info: https://github.com/cernekee/stoken
#
# Use the password from above setup to populate "rsatoken" in your keychain
# security add-generic-password -U -a $USER -s rsatoken -w
#
# Repeat this process for your AD "snad", for LDAP we use what is stored for bssh

# "rsatoken" is the credential to decrypt from "stoken" stored in keychain
# Here we use it to fetch the current token and also get our pin from keychain
# x86_64 arch
# token=$(/usr/bin/security find-generic-password -w -s rsatoken 2>&1 | /usr/local/bin/stoken --stdin | tr -d '\n')

# arm64 aarch

from swiftbar import util
from swiftbar.plugin import Plugin
from typing import Dict, List, Tuple, Union
import shutil

def process_actions(plugin: Plugin=None) -> None:
    for _, data in plugin.defaults_dict.items():
        if 'action_configuration' in data:
            setting_flag = data['action_configuration']['flag']
            setting_title = data['action_configuration']['title']
            plugin.print_menu_item(
                setting_title,
                cmd=[plugin.plugin_name, setting_flag],
                terminal=False,
                refresh=True,
            )
            plugin.print_menu_separator()

def refresh_token() -> Tuple[Union[str, None], Union[str, None]]:
    _, stdout, stderr = util.execute_command('security find-generic-password -w -s rsatoken | stoken --stdin')
    if stderr:
        return None, stderr
    return stdout, None

def get_item(key: str=None) -> Tuple[Union[str, None], Union[str, None]]:
    _, stdout, stderr = util.execute_command(f'security find-generic-password -w -s {key}')
    if stderr:
        return None, stderr
    return stdout, None

def get_data() -> Tuple[Dict[str, str], List[str]]:
    output = {}
    errors = []

    brew = shutil.which('brew')
    if not brew:
        return ['homebrew not installed'], None

    stoken = shutil.which('stoken')
    if not stoken:
        return ['stoken not installed - brew install stoken'], None

    output['token'], error = refresh_token()
    if error:
        errors.append(error)
    
    for key in ['rsatoken-pin', 'snad', 'snc.bssh.ldap_pass']:
        output[key], error =  get_item(key)
        if error:
            errors.append(f'Failed to retrieve "{key}": {error}')
    return output, errors

def pbcopy(text: str=None) -> None:
    util.execute_command('pbcopy', input=text)
    
def main() -> None:
    plugin = Plugin()
    plugin.defaults_dict['COPY_TOKEN'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'action_configuration': {
            'default': False,
            'flag': '--token',
            'title': 'Copy PIN + token',
        },
    }
    plugin.defaults_dict['NEXT_TOKEN'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'action_configuration': {
            'default': False,
            'flag': '--next',
            'title': 'Cycle token'
        },
    }
    plugin.defaults_dict['COPY_SNAD'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'action_configuration': {
            'default': False,
            'flag': '--snad',
            'title': 'Copy AD password',
        },
    }
    plugin.defaults_dict['COPY_LDAP'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'action_configuration': {
            'default': False,
            'flag': '--ldap',
            'title': 'Copy LDAP password',
        },
    }
    plugin.setup()

    output, errors = get_data()
    if len(errors) > 0:
        plugin.print_menu_title('RSA Token Error')
        for error in errors:
            plugin.print_menu_item(error)
    else:
        plugin.print_menu_title('RSA Token')
        process_actions(plugin=plugin)
        if plugin.args.token:
            pbcopy(f'{output["rsatoken-pin"]}{output["token"]}')
        elif plugin.args.snad:
            pbcopy(output['snad'])
        elif plugin.args.ldap:
            pbcopy(output['snc.bssh.ldap_pass'])
        elif plugin.args.next:
            refresh_token()   
    plugin.render_footer()

if __name__ == '__main__':
    main()
