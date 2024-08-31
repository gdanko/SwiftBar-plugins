#!/usr/bin/env python3

# <xbar.title>System Updates</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>This plugin displays the number of available system updates.</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-SystemUpdates.15m.py</xbar.abouturl>

import subprocess

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
    
if __name__ == '__main__':
    main()
