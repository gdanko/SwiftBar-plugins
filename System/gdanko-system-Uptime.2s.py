#!/usr/bin/env python3

# <xbar.title>Uptime</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system uptime</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-Uptime.2s.py</xbar.abouturl>

import calendar
import datetime
import subprocess
import sys
import time
from collections import namedtuple

try:
    from psutil import boot_time
except ModuleNotFoundError:
    print('Error: missing "psutil" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install psutil')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_duration_tuple(days=0, hours=0, minutes=0, seconds=0):
    duration = namedtuple('duration', 'days hours minutes seconds')
    return duration(days=days, hours=hours, minutes=minutes, seconds=seconds)

def get_plural(count, string):
    return string if count == 1 else f'{string}s'

def get_duration(boot_time):
    days, hours, minutes, seconds = 0, 0, 0, 0
    delta = datetime.datetime.fromtimestamp(int(time.time())) - datetime.datetime.fromtimestamp(boot_time)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return get_duration_tuple(days=days, hours=hours, minutes=minutes, seconds=seconds)

def main():
    uptime = []
    duration = get_duration(boot_time())
    if duration.days > 0:
        uptime.append(f'{duration.days} {get_plural(duration.days, "day")}')
    uptime.append(f'{str(duration.hours).zfill(2)}:{str(duration.minutes).zfill(2)}')
    print(f'up {" ".join(uptime)}')
    print('---')
    print(f'Last boot: {datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")}')

if __name__ == '__main__':
    main()
