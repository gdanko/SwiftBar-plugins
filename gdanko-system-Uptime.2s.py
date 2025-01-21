#!/usr/bin/env python3

# <xbar.title>Uptime</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system uptime</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-Uptime.2s.py</xbar.abouturl>

from collections import namedtuple
import datetime
import plugin
import re
import time

def get_duration(seconds):
    try:
        seconds = int(seconds)
        days = int(seconds / 86400)
        hours = int(((seconds - (days * 86400)) / 3600))
        minutes = int(((seconds - days * 86400 - hours * 3600) / 60))
        secs = int((seconds - (days * 86400) - (hours * 3600) - (minutes * 60)))

        duration = namedtuple('duration', 'days hours minutes seconds')
        return duration(days=days, hours=hours, minutes=minutes, seconds=secs)
    except:
        return None

def get_boot_time():
    stdout, stderr = plugin.get_command_output('sysctl -n kern.boottime')
    if stderr:
        return None
    pattern = re.compile(r'sec = ([0-9]{10,13})')
    match = re.search(pattern, stdout)
    if match:
        timestamp = int(match.group(1))
        return timestamp
    return None

def get_duration_tuple():
    boot_time = get_boot_time()
    if boot_time:
        return boot_time, get_duration(int(time.time()) - boot_time)
    else:
        return None, None

def main():
    boot_time, duration_tuple = get_duration_tuple()
    if duration_tuple:
        uptime = []
        if duration_tuple.days > 0:
            uptime.append(f'{duration_tuple.days} {"day" if duration_tuple.days == 1 else "days"}')
        uptime.append(f'{str(duration_tuple.hours).zfill(2)}:{str(duration_tuple.minutes).zfill(2)}')
        print(f'up {" ".join(uptime)}')
        print('---')
        print(f'Last boot: {datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")}')
    else:
        print('Uptime: N/A')
        print('---')
        print('Failed to determine boot time')

if __name__ == '__main__':
    main()
