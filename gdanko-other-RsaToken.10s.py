#!/usr/bin/env python3

# <xbar.title>RsaToken</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>fetches current rsa token, and allows you to copy your pin from keychain to your paste buffer</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-RsaToken.10s.py</xbar.abouturl>
#
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

import argparse
import os
import plugin
import shutil
import sys

def get_args():
    parser = argparse.ArgumentParser()
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
    returncode, stdout, stderr = plugin.execute_command('security find-generic-password -w -s rsatoken | stoken --stdin')
    if stderr:
        return None, stderr
    return stdout, None

def get_item(key):
    returncode, stdout, stderr = plugin.execute_command(f'security find-generic-password -w -s {key}')
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
    plugin.execute_command('pbcopy', input=text)
    
def main():
    os.environ['PATH'] = '/opt/homebrew/bin:/opt/homebrew/sbin:/bin:/sbin:/usr/bin:/usr/sbin'
    invoker, config_dir = plugin.get_config_dir()
    plugin_name = os.path.abspath(sys.argv[0])
    emojize = ' | emojize=true symbolize=false' if invoker == 'SwiftBar' else ''
    error = setup()
    if error:
        print('RSA Token Error')
        print('---')
        print(error)
        print(os.environ['PATH'])
    else:
        output, errors = get_data()
        if len(errors) > 0:
            print('RSA Token Error')
            print('---')
            for error in errors:
                print(error)
        else:
            args = get_args()
            if args.token:
                pbcopy(f'{output["rsatoken-pin"]}{output["token"]}')
            elif args.snad:
                pbcopy(output['snad'])
            elif args.ldap:
                pbcopy(output['snc.bssh.ldap_pass'])
            elif args.next:
                refresh_token()

            print('RSA Token')
            print('---')
            print(output['token'])
            print('---')
            print(f':scissors: | bash="{plugin_name}" param1="--token" terminal=false refresh=true{emojize}')
            print('---')
            print(f':fast_forward: | bash="{plugin_name}" param1="--refresh" terminal=false refresh=true{emojize}')
            print('---')
            print(f':man: | bash="{plugin_name}" param1="--snad" terminal=false refresh=true{emojize}')
            print('---')
            print(f':key: | bash="{plugin_name}" param1="--ldap" terminal=false refresh=true{emojize}')
            print('---')
            print('Refresh | refresh=true')

if __name__ == '__main__':
    main()
