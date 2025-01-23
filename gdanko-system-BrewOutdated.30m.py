#!/usr/bin/env python3

# <xbar.title>BrewOutdated</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number upgradeable Homebrew packages</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-BrewOutdated.30m.py</xbar.abouturl>

import os
import plugin
import shutil
import time

def main():
    os.environ['PATH'] = '/opt/homebrew/bin:/opt/homebrew/sbin:/bin:/sbin:/usr/bin:/usr/sbin'
    invoker, config_dir = plugin.get_config_dir()
    invoker='SwiftBar'
    emojize = ' | emojize=true symbolize=false' if invoker == 'SwiftBar' else ''
    error_message = None
    success = True
    upgradeable = []
    

    if shutil.which('brew'):
        returncode, _, _ = plugin.execute_command('brew update')
        if returncode == 0:
            returncode, stdout, _ = plugin.execute_command('brew outdated -q')
            if returncode == 0:
                if stdout:
                    upgradeable = stdout.split('\n')
            else:
                success = False
                error_message = 'Failed to execute "brew outdated"'
        else:
            success = False
            error_message = 'Failed to update Homebrew'
    else:
        success = False
        error_message = 'Homebrew isn\'t installed'
    
    if success:
        print(f'Brew Outdated: {len(upgradeable)}')
        print('---')
        print(f'Updated {plugin.get_timestamp(int(time.time()))}')
        if len(upgradeable) > 0:
            print('---')
            for package in sorted(upgradeable):
                bits = [
                    f':beer: Upgrade {package}',
                    f'bash=brew param1="upgrade" param2="{package}" terminal=true refresh=true',
                ]
                if invoker == 'SwiftBar':
                    bits.append('emojize=true symbolize=false')
                print(' | '.join(bits))
            print('---')
            bits = [
                ':beer: Upgrade all | bash=brew param1="upgrade" terminal=true refresh=true'
            ]
            if invoker == 'SwiftBar':
                bits.append('emojize=true symbolize=false')
            print(' | '.join(bits))
        print('Refresh | refresh=true')
    else:
        print(f'Brew Outdated: Failed')
        print('---')
        print(error_message)

if __name__ == '__main__':
    main()
