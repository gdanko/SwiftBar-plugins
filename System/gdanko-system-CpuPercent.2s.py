#!/usr/bin/env python3

# <xbar.title>CPU Percent</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display CPU % for user, system, and idle</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-CpuPercent.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_CPU_USAGE_CLICK_TO_KILL="false"): Will clicking a member of the top offender list attempt to kill it?</xbar.var>
# <xbar.var>string(VAR_CPU_USAGE_KILL_SIGNAL=<int>): The Darwin kill signal to use when killing a process</xbar.var>
# <xbar.var>string(VAR_CPU_USAGE_MAX_CONSUMERS=<int>): Maximum number of offenders to display</xbar.var>

from collections import namedtuple
from math import ceil
import argparse
import datetime
import getpass
import json
import os
import re
import signal
import subprocess
import sys
import time

try:
    from psutil import cpu_freq, cpu_times, cpu_times_percent
except ModuleNotFoundError:
    print('Error: missing "psutil" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install psutil')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def get_signal_map():
    return {
        'SIHGUP': signal.SIGHUP,
        'SIGINT': signal.SIGINT,
        'SIGQUIT': signal.SIGQUIT,
        'SIGILL': signal.SIGILL,
        'SIGTRAP': signal.SIGTRAP,
        'SIGABRT': signal.SIGABRT,
        'SIGEMT': signal.SIGEMT,
        'SIGFPE': signal.SIGFPE,
        'SIGKILL': signal.SIGKILL,
        'SIGBUS': signal.SIGBUS,
        'SIGSEGV': signal.SIGSEGV,
        'SIGSYS': signal.SIGSYS,
        'SIGPIPE': signal.SIGPIPE,
        'SIGALRM': signal.SIGALRM,
        'SIGTERM': signal.SIGTERM,
        'SIGURG': signal.SIGURG,
        'SIGSTOP': signal.SIGSTOP,
        'SIGTSTP': signal.SIGTSTP,
        'SIGCONT': signal.SIGCONT,
        'SIGCHLD': signal.SIGCHLD,
        'SIGTTIN': signal.SIGTTIN,
        'SIGTTOU': signal.SIGTTOU,
        'SIGIO': signal.SIGIO,
        'SIGXCPU': signal.SIGXCPU,
        'SIGXFSZ': signal.SIGXFSZ,
        'SIGVTALRM': signal.SIGVTALRM,
        'SIGPROF': signal.SIGPROF,
        'SIGWINCH': signal.SIGWINCH,
        'SIGINFO': signal.SIGINFO,
        'SIGUSR1': signal.SIGUSR1,
        'SIGUSR2': signal.SIGUSR2,
    }

def get_cpu_family_strings():
    # We get this information from /Library/Developer/CommandLineTools/SDKs/MacOSX<version>.sdk/usr/include/mach/machine.h
    # Current: /Library/Developer/CommandLineTools/SDKs/MacOSX15.sdk/usr/include/mach/machine.h
    return {
        0:          'Unknown',
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
        0x6f5129ac: 'ARM Donan',
        0x75d4acb9: 'ARM Tahiti',
        0x204526d0: 'ARM Tupai',
    }

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable', help='Disable "Click to Kill" functionality', required=False, default=False, action='store_true')
    parser.add_argument('--enable', help='Enable "Click to Kill" functionality', required=False, default=False, action='store_true')
    parser.add_argument('--max-consumers', help='Maximum number of CPU consumers to display', required=False, default=0, type=int)
    parser.add_argument('--signal', help='The signal level to use when killing a process', required=False)
    args = parser.parse_args()
    return args

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_time_stats_tuple(cpu='cpu-total', cpu_type=None, user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_times = namedtuple('cpu_times', 'cpu cpu_type user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_times(cpu=cpu, cpu_type=cpu_type, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

def read_config(param, default):
    plugin = os.path.abspath(sys.argv[0])
    jsonfile = f'{plugin}.vars.json'
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as fh:
            contents = json.load(fh)
            if param in contents:
                return contents[param]
    return default

def write_config(jsonfile, contents):
    with open(jsonfile, 'w') as fh:
        fh.write(json.dumps(contents, indent=4))


def update_setting(plugin, key, value):
    jsonfile = f'{plugin}.vars.json'
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as fh:
            contents = json.load(fh)
            if key in contents:
                contents[key] = value
                write_config(jsonfile, contents)

def get_defaults():
    click_to_kill = read_config('VAR_CPU_USAGE_CLICK_TO_KILL', 'false')
    click_to_kill = True if click_to_kill == 'true' else False
    signal = read_config('VAR_CPU_USAGE_KILL_SIGNAL', 'SIGQUIT')
    max_consumers = read_config('VAR_CPU_USAGE_MAX_CONSUMERS', 30)

    return click_to_kill, signal, max_consumers

def get_sysctl(metric):
    command = f'sysctl -n {metric}'
    output = get_command_output(command)
    return output

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

def get_command_output(command):
    previous = None
    for command in re.split(r'\s*\|\s*', command):
        cmd = re.split(r'\s+', command)
        p = subprocess.Popen(cmd, stdin=(previous.stdout if previous else None), stdout=subprocess.PIPE)
        previous = p
    return p.stdout.read().strip().decode()

def get_top_cpu_usage():
    cpu_info = []
    command = f'ps -axm -o %cpu,pid,user,comm | tail -n+2'
    output = get_command_output(command)
    if output:
        lines = output.strip().split('\n')
        for line in lines:
            match = re.search(r'^\s*(\d+\.\d+)\s+(\d+)\s+([A-Za-z0-9\-\.\_]+)\s+(.*)$', line)
            if match:
                cpu_usage = float(match.group(1))
                pid = match.group(2)
                user = match.group(3)
                command_name = match.group(4)
                if cpu_usage > 0.0:
                    cpu_info.append({'command': command_name, 'cpu_usage': float(cpu_usage), 'pid': pid, 'user': user})

    return sorted(cpu_info, key=lambda item: float(item['cpu_usage']), reverse=True)

def get_disabled_flag(process_owner, click_to_kill):
    return ('false' if process_owner == getpass.getuser() else 'true') if click_to_kill else 'true'

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = os.path.abspath(sys.argv[0])
    args = configure()
    if args.enable:
        update_setting(plugin, 'VAR_CPU_USAGE_CLICK_TO_KILL', 'true')
    elif args.disable:
        update_setting(plugin, 'VAR_CPU_USAGE_CLICK_TO_KILL', 'false')
    elif args.signal:
        update_setting(plugin, 'VAR_CPU_USAGE_KILL_SIGNAL', args.signal)
    elif args.max_consumers > 0:
        update_setting(plugin, 'VAR_CPU_USAGE_MAX_CONSUMERS', args.max_consumers)
        
    click_to_kill, signal, max_consumers = get_defaults()
    command_length = 125
    font_name = 'Andale Mono'
    font_size = 13
    font_data = f'size="{font_size}" font="{font_name}"'
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

    top_cpu_consumers = get_top_cpu_usage()
    if len(top_cpu_consumers) > 0:
        if len(top_cpu_consumers) > max_consumers:
            top_cpu_consumers = top_cpu_consumers[0:max_consumers]
        print(f'Top {len(top_cpu_consumers)} CPU Consumers')
        for consumer in top_cpu_consumers:
            command = consumer['command']
            cpu_usage = consumer['cpu_usage']
            pid = consumer['pid']
            user = consumer['user']
            # Auto-set the width based on the widest member
            padding_width = 6
            print(f'--{":skull: " if click_to_kill else ""}{str(cpu_usage).rjust(padding_width)}% - {command} | length={command_length} | {font_data} | shell=/bin/sh | param1="-c" | param2="kill -{get_signal_map()[signal]} {pid}" | disabled={get_disabled_flag(user, click_to_kill)}')
    print('---')
    print('Settings')
    print(f'{"--Disable" if click_to_kill else "--Enable"} "Click to Kill" | shell="{plugin}" | param1={"--disable" if click_to_kill else "--enable"} | terminal=false | refresh=true')
    print('--Kill Signal')
    for key, _ in get_signal_map().items():
        color = ' | color=blue' if key == signal else ''
        print(f'----{key} | shell="{plugin}" param1="--signal" | param2={key} | terminal=false | refresh=true{color}')
    print('--Maximum Number of Top Consumers')
    for number in range(1, 51):
        if number %5 == 0:
            color = ' | color=blue' if number == max_consumers else ''
            print(f'----{number} | shell="{plugin}" param1="--max-consumers" | param2={number} | terminal=false | refresh=true{color}')

if __name__ == '__main__':
    main()
