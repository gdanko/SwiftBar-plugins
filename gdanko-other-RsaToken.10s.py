#!/usr/bin/env python3

# <xbar.title>RsaToken</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>fetches current rsa token, and allows you to copy your pin from keychain to your paste buffer</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/Other/gdanko-system-RsaToken.10s.py</xbar.abouturl>
#
# Credit goes to Marcus D'Camp for the original, which was a shell script.
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
import shutil
import subprocess
import sys
import re

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snad', help='Copy AD password to the clipboard', required=False, default=False, action='store_true')
    parser.add_argument('--ldap', help='Copy LDAP password to the clipboard', required=False, default=False, action='store_true')
    parser.add_argument('--token', help='Copy {pin}{token} to the clipboard', required=False, default=False, action='store_true')
    parser.add_argument('--next', help='Refesh the token and copy it to the clipboard', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args   

def get_command_output2(command):
    previous = None
    for command in re.split(r'\s*\|\s*', command):
        cmd = re.split(r'\s+', command)
        p = subprocess.Popen(cmd, stdin=(previous.stdout if previous else None), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        previous = p
    return p.stdout.read().strip(), p.stderr.read().strip()

def get_command_output(command, input=None):
    previous = None
    for command in re.split(r'\s*\|\s*', command):
        cmd = re.split(r'\s+', command)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdin = input if input else (previous.stdout.read().strip() if previous else None)
        if stdin:
            p.stdin.write(stdin)
            p.stdin.close()
        input = None
        previous = p
    return p.stdout.read().strip(), p.stderr.read().strip()

def setup():
    brew = shutil.which('brew')
    if not brew:
        return 'homebrew not installed'

    stoken = shutil.which('stoken')
    if not stoken:
        return 'stoken not installed - brew install stoken'

def refresh_token():
    output, error = get_command_output('security find-generic-password -w -s rsatoken | stoken --stdin')
    if error:
        return None, error
    return output, None

def get_item(key):
    output, error = get_command_output(f'security find-generic-password -w -s {key}')
    if error:
        return None, error
    return output, None

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
    get_command_output('pbcopy', input=text)
    
def main():
    os.environ['PATH'] = '/opt/homebrew/bin:/opt/homebrew/sbin:/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = os.path.abspath(sys.argv[0])
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
            print(f':scissors: | shell="{plugin}" | param1="--token" | terminal=false | refresh=true')
            print('---')
            print(f':fast_forward: | shell="{plugin}" | param1="--refresh" | terminal=false | refresh=true')
            print('---')
            print(f':man: | shell="{plugin}" | param1="--snad" | terminal=false | refresh=true')
            print('---')
            print(f':key: | shell="{plugin}" | param1="--ldap" | terminal=false | refresh=true')
            print('---')
            print('Refresh | refresh=true')

if __name__ == '__main__':
    main()
