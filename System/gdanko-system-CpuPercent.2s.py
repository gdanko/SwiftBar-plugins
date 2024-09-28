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
import re
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

def get_cpu_family_strings():
    # We get this information from /Library/Developer/CommandLineTools/SDKs/MacOSX14.4.sdk/usr/include/mach/machine.h
    return {
        0xcee41549: 'PowerPC G3',
        0x77c184ae: 'PowerPC G4',
        0xed76d8aa: 'PowerPC G5',
        0xaa33392b: 'Intel 6_13',
        0x78ea4fbc: 'Intel Penryn',
        0x6b5a4cd2: 'Intel Nehalem',
        0x573b5eec: 'Intel Westmere',
        0x5490b78c: 'Intel Sandybridge',
        0x1f65e835: 'Intel Ivybridge',
        0x10b282dc: 'Intel Haswell',
        0x582ed09c: 'Intel Broadwell',
        0x37fc219f: 'Intel Skylake',
        0x0f817246: 'Intel Kabylake',
        0x38435547: 'Intel Icelake',
        0x1cf8a03e: 'Intel Cometlake',
        0xe73283ae: 'ARM9',
        0x8ff620d8: 'ARM11',
        0x53b005f5: 'ARM XScale',
        0xbd1b0ae9: 'ARM12',
        0x0cc90e64: 'ARM13',
        0x96077ef1: 'ARM14',
        0xa8511bca: 'ARM15',
        0x1e2d6381: 'ARM Swift',
        0x37a09642: 'ARM Cyclone',
        0x2c91a47e: 'ARM Typhoon',
        0x92fb37c8: 'ARM Twister',
        0x67ceee93: 'ARM Hurricane',
        0xe81e7ef6: 'ARM Monsoon Mistral',
        0x07d34b9f: 'ARM Vortex Tempest',
        0x462504d2: 'ARM Lightning Thunder',
        0x1b588bb3: 'ARM Firestorm Icestorm',
        0xda33d83d: 'ARM Blizzard Avalanche',
        0x8765edea: 'ARM Everest Sawtooth',
        0xfa33415e: 'ARM Ibiza',
        0x72015832: 'ARM Palma',
        0x2876f5b5: 'ARM Coll',
        0x5f4dea93: 'ARM Lobos',
    }

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_time_stats_tuple(cpu='cpu-total', cpu_type=None, user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_times = namedtuple('cpu_times', 'cpu cpu_type user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_times(cpu=cpu, cpu_type=cpu_type, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

def get_sysctl(metric):
    p = subprocess.Popen(
        ['/usr/sbin/sysctl', '-n', metric],
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

def get_top_cpu_usage():
    # This performs the equivalent of `ps -axm -o %cpu,comm | egrep -v "^top" | sort -rn -k 1 | head -n 10`
    command_length = 75
    number_of_offenders = 20
    cpu_info = []
    cmd1 = ['/bin/ps', '-axm', '-o', '%cpu,comm']
    cmd2 = ['sort', '-rn', '-k', '1']

    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
    output = p2.stdout.read().decode()
    lines = output.strip().split('\n')

    for line in lines:
        match = re.search(r'^\s*(\d+\.\d+)\s+(.*)$', line)
        if match:
            cpu_usage = match.group(1)
            command_name = match.group(2)
            if len(command_name) > command_length:
                command_name = command_name[0:command_length] + '...'

            if float(cpu_usage) > 0.0 and command_name != 'top':
                cpu_info.append({
                    'command': command_name,
                    'cpu_usage': cpu_usage + '%'
                })
    if len(cpu_info) > number_of_offenders:
        return cpu_info[0:number_of_offenders]
    else:
        return cpu_info

def main():
    cpu_type = get_sysctl('machdep.cpu.brand_string')
    cpu_family = get_cpu_family_strings().get(int(get_sysctl('hw.cpufamily')), int(get_sysctl('hw.cpufamily')))
    max_cpu_freq = cpu_freq().max if cpu_freq().max is not None else None
    individual_cpu_pct = []
    combined_cpu_pct = []

    individual_cpu_percent = cpu_times_percent(interval=1.0, percpu=True)

    for i, cpu_instance in enumerate(individual_cpu_percent):
        individual_cpu_pct.append(get_time_stats_tuple(cpu=i, cpu_type=cpu_type, user=cpu_instance.user, system=cpu_instance.system, nice=cpu_instance.nice, idle=cpu_instance.idle))
    combined_cpu_pct.append(combine_stats(individual_cpu_pct, cpu_type))

    print(f'CPU: user {pad_float(combined_cpu_pct[0].user)}%, sys {pad_float(combined_cpu_pct[0].system)}%, idle {pad_float(combined_cpu_pct[0].idle)}%')
    print('---')
    print(f'Updated {get_timestamp(int(time.time()))}')
    print('---')
    if cpu_type is not None:
        processor = cpu_type
        if cpu_family:
            processor = processor + f' ({cpu_family})'
        if max_cpu_freq:
            processor = processor + f' @ {pad_float(max_cpu_freq / 1000)} GHz'
        print(f'Processor: {processor}')
        
    for cpu in individual_cpu_pct:
        print(f'Core {cpu.cpu}: user {cpu.user}%, sys {cpu.system}%, idle {cpu.idle}%')

    cpu_offenders = get_top_cpu_usage()
    if len(cpu_offenders) > 0:
        print(f'Top {len(cpu_offenders)} CPU Consumers')
        for offender in cpu_offenders:
            print(f'--{offender["cpu_usage"]} - {offender["command"]}')

if __name__ == '__main__':
    main()
