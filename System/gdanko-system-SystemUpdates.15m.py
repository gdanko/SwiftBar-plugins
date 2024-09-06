#!/usr/bin/env python3

# <xbar.title>System Updates</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number of available system updates</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-SystemUpdates.15m.py</xbar.abouturl>

import datetime
import subprocess
import time

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def main():
    updates = 0
    p = subprocess.Popen(
        ['softwareupdate', '--list'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        lines = stdout.split('\n')
        for line in lines:
            if '* Label' in line:
                updates += 1
        print(f'Updates: {updates}')
        print('---')
        print(f'Updated {get_timestamp(int(time.time()))}')
        print('---')
        print('Refresh system update data | refresh=true')
    else:
        print('Updates: Unknown')
        print('---')
        print(f'Failed to find update count: {stderr}')
    
if __name__ == '__main__':
    main()
