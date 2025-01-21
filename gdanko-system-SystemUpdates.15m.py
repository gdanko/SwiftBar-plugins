#!/usr/bin/env python3

# <xbar.title>System Updates</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the number of available system updates</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-SystemUpdates.15m.py</xbar.abouturl>

import datetime
import os
import re
import subprocess
import time

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_command_output(command):
    previous = None
    for command in re.split(r'\s*\|\s*', command):
        cmd = re.split(r'\s+', command)
        p = subprocess.Popen(cmd, stdin=(previous.stdout if previous else None), stdout=subprocess.PIPE)
        previous = p
    return p.stdout.read().strip().decode()

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    updates = 0
    command = f'softwareupdate --list'
    output = get_command_output(command)
    if output:
        lines = output.split('\n')
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
        # Need to capture the error
        print(f'Failed to find update count')
    
if __name__ == '__main__':
    main()
