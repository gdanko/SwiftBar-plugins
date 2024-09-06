#!/usr/bin/env python3

# <xbar.title>CPU Percent</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display CPU % for user, system, and idle</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-CpuPercent.2s.py</xbar.abouturl>

from collections import namedtuple
from math import ceil
import datetime
import subprocess
import sys
import time
from pprint import pprint

try:
    from psutil import cpu_freq, cpu_times, cpu_times_percent
except ModuleNotFoundError:
    print('Error: missing "psutil" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install psutil')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_time_stats_tuple(cpu='cpu-total', cpu_type=None, user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_times = namedtuple('cpu_times', 'cpu cpu_type user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_times(cpu=cpu, cpu_type=cpu_type, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

def get_cpu_type():
    p = subprocess.Popen(
        ['/usr/sbin/sysctl', '-n', 'machdep.cpu.brand_string'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, _ = p.communicate()
    if p.returncode == 0:
        return stdout.strip()
    else:
        return None

def combine_stats(cpu_time_stats, cpu_type):
    idle      = 0.0
    nice      = 0.0
    system    = 0.0
    user      = 0.0

    for cpu_time_stat in cpu_time_stats:
        idle   += cpu_time_stat.idle
        nice   += cpu_time_stat.nice
        system += cpu_time_stat.system
        user   += cpu_time_stat.user
    return get_time_stats_tuple(
        cpu_type=cpu_type,
        idle=(idle / len(cpu_time_stats)),
        nice=(nice / len(cpu_time_stats)),
        system=(system / len(cpu_time_stats)),
        user=(user / len(cpu_time_stats)),
    )

def gather_cpu_info():
    cpu_type = get_cpu_type()
    max_cpu_freq = cpu_freq().max if cpu_freq().max is not None else None
    individual_cpu_pct = []
    combined_cpu_pct = []

    individual_cpu_percent = cpu_times_percent(interval=1.0, percpu=True)

    # Create more detailed tuples for the cpu_times_percent() output
    for i, cpu_instance in enumerate(individual_cpu_percent):
        individual_cpu_pct.append(get_time_stats_tuple(cpu=i, cpu_type=cpu_type, user=cpu_instance.user, system=cpu_instance.system, nice=cpu_instance.nice, idle=cpu_instance.idle))
    combined_cpu_pct.append(combine_stats(individual_cpu_pct, cpu_type))

    return combined_cpu_pct, individual_cpu_pct, cpu_type, max_cpu_freq

def main():
    combined_cpu_pct, individual_cpu_pct, cpu_type, max_cpu_freq = gather_cpu_info()

    print(f'CPU: user {pad_float(combined_cpu_pct[0].user)}%, sys {pad_float(combined_cpu_pct[0].system)}%, idle {pad_float(combined_cpu_pct[0].idle)}%')
    print('---')
    print(f'Updated {get_timestamp(int(time.time()))}')
    print('---')
    if cpu_type is not None:
        processor = cpu_type
        if max_cpu_freq:
            processor = processor + f' @ {pad_float(max_cpu_freq / 1000)} GHz'
        print(f'Processor: {processor}')
        
    for cpu in individual_cpu_pct:
        print(f'Core {cpu.cpu}: user {cpu.user}%, sys {cpu.system}%, idle {cpu.idle}%')

if __name__ == '__main__':
    main()
