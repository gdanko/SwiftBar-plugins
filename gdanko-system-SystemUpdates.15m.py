#!/usr/bin/env python3

# <xbar.title>System Updates</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number of available system updates</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-SystemUpdates.15m.py</xbar.abouturl>

import os
import plugin
import time

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    updates = 0
    command = f'softwareupdate --list'
    returncode, stdout, stderr = plugin.execute_command(command)
    if stdout:
        lines = stdout.split('\n')
        for line in lines:
            if '* Label' in line:
                updates += 1
        print(f'Updates: {updates}')
        print('---')
        print(f'Updated {plugin.get_timestamp(int(time.time()))}')
        print('---')
        print('Refresh system update data | refresh=true')
    else:
        print('Updates: Unknown')
        print('---')
        # Need to capture the error
        print(f'Failed to find update count')
    
if __name__ == '__main__':
    main()
