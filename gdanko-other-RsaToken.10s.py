#!/usr/bin/env python3

# <xbar.title>RsaToken</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>fetches current rsa token, and allows you to copy your pin from keychain to your paste buffer</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-RsaToken.10s.py</xbar.abouturl>
# <xbar.var>string(VAR_RSA_TOKEN_DEBUG_ENABLED=false"): Show debugging menu</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

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
import argparse
import os
import shutil
import sys

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    parser.add_argument('--snad', help='Copy AD password to the clipboard', required=False, default=False, action='store_true')
    parser.add_argument('--ldap', help='Copy LDAP password to the clipboard', required=False, default=False, action='store_true')
    parser.add_argument('--token', help='Copy {pin}{token} to the clipboard', required=False, default=False, action='store_true')
    parser.add_argument('--next', help='Refesh the token and copy it to the clipboard', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args   

def setup():
    brew = shutil.which('brew')
    if not brew:
        return 'homebrew not installed'

    stoken = shutil.which('stoken')
    if not stoken:
        return 'stoken not installed - brew install stoken'

def refresh_token():
    _, stdout, stderr = util.execute_command('security find-generic-password -w -s rsatoken | stoken --stdin')
    if stderr:
        return None, stderr
    return stdout, None

def get_item(key):
    _, stdout, stderr = util.execute_command(f'security find-generic-password -w -s {key}')
    if stderr:
        return None, stderr
    return stdout, None

def get_data():
    errors = []
    output = {}
    output['token'], error = refresh_token()
    if error:
        errors.append(error)
    
    for key in ['rsatoken-pin', 'snad', 'snc.bssh.ldap_pass']:
        output[key], error =  get_item(key)
        if error:
            errors.append(f'Failed to retrieve "{key}": {error}')
    return output, errors

def pbcopy(text):
    util.execute_command('pbcopy', input=text)
    
def main():
    os.environ['PATH'] = '/opt/homebrew/bin:/opt/homebrew/sbin:/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()

    defaults_dict = {
        'VAR_RSA_TOKEN_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
    }
    plugin.read_config(defaults_dict)
    args = configure()
    if args.debug:
        plugin.update_setting('VAR_RSA_TOKEN_DEBUG_ENABLED', True if plugin.configuration['VAR_RSA_TOKEN_DEBUG_ENABLED'] == False else False)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_RSA_TOKEN_DEBUG_ENABLED']
    error = setup()
    if error:
        plugin.print_menu_title('RSA Token Error')
        plugin.print_menu_separator()
        plugin.print_menu_item(error)
    else:
        output, errors = get_data()
        if len(errors) > 0:
            plugin.print_menu_title('RSA Token Error')
            plugin.print_menu_separator()
            for error in errors:
                plugin.print_menu_item(error)
        else:
            if args.token:
                pbcopy(f'{output["rsatoken-pin"]}{output["token"]}')
            elif args.snad:
                pbcopy(output['snad'])
            elif args.ldap:
                pbcopy(output['snc.bssh.ldap_pass'])
            elif args.next:
                refresh_token()

            plugin.print_menu_title('RSA Token')
            plugin.print_menu_separator()
            plugin.print_menu_item(output['token'])
            plugin.print_menu_separator()
            plugin.print_menu_item(
                'Copy PIN + token',
                cmd=[plugin.plugin_name, '--token'],
                terminal=False,
                refresh=True,
            )
            plugin.print_menu_separator()
            plugin.print_menu_item(
                'Cycle token',
                cmd=[plugin.plugin_name, '--refresh'],
                terminal=False,
                refresh=True,
            )
            plugin.print_menu_separator()
            plugin.print_menu_item(
                'Copy AD password',
                cmd=[plugin.plugin_name, '--snad'],
                terminal=False,
                refresh=True,
            )
            plugin.print_menu_separator()
            plugin.print_menu_item(
                'Copy LDAP password',
                cmd=[plugin.plugin_name, '--ldap'],
                terminal=False,
                refresh=True,
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
                plugin.display_debug_data()
            plugin.print_menu_item('Refresh', refresh=True)

if __name__ == '__main__':
    main()
