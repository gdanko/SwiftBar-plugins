#!/usr/bin/env python3

# <xbar.title>CPU Percent</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display CPU % for user, system, and idle</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-CpuPercent.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_CPU_USAGE_CLICK_TO_KILL="false"): Will clicking a member of the top offender list attempt to kill it?</xbar.var>
# <xbar.var>string(VAR_CPU_USAGE_DEBUG_ENABLED=false"): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_CPU_USAGE_KILL_SIGNAL=<int>): The Darwin kill signal to use when killing a process</xbar.var>
# <xbar.var>string(VAR_CPU_USAGE_MAX_CONSUMERS=<int>): Maximum number of offenders to display</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

from collections import namedtuple
from swiftbar import util
from swiftbar.plugin import Plugin
import argparse
import os
import re
import subprocess
import sys

try:
    from psutil import cpu_freq, cpu_times_percent
except ModuleNotFoundError:
    print('Error: missing "psutil" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install psutil')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

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
    parser.add_argument('--click-to-kill', help='Toggle "Click to kill" functionality', required=False, default=False, action='store_true')
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    parser.add_argument('--max-consumers', help='Maximum number of CPU consumers to display', required=False, default=0, type=int)
    parser.add_argument('--signal', help='The signal level to use when killing a process', required=False)
    args = parser.parse_args()
    return args

def get_time_stats_tuple(cpu='cpu-total', cpu_type=None, user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_times = namedtuple('cpu_times', 'cpu cpu_type user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_times(cpu=cpu, cpu_type=cpu_type, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

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
    cpu_info = []
    command = f'ps -axm -o %cpu,pid,user,comm | tail -n+2'
    returncode, stdout, _ = util.execute_command(command)
    if returncode == 0:
        lines = stdout.strip().split('\n')
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

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_CPU_USAGE_CLICK_TO_KILL': {
            'default_value': True,
            'valid_values': [True, False],
        },
        'VAR_CPU_USAGE_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_CPU_USAGE_KILL_SIGNAL': {
            'default_value': 'SIGQUIT',
            'valid_values': list(util.get_signal_map().keys()),
        },
        'VAR_CPU_USAGE_MAX_CONSUMERS': {
            'default_value': 30,
        }
    }

    plugin.read_config(defaults_dict)
    args = configure()
    if args.click_to_kill:
        plugin.update_setting('VAR_CPU_USAGE_CLICK_TO_KILL', True if plugin.configuration['VAR_CPU_USAGE_CLICK_TO_KILL'] == False else False)
    elif args.debug:
        plugin.update_setting('VAR_CPU_USAGE_DEBUG_ENABLED', True if plugin.configuration['VAR_CPU_USAGE_DEBUG_ENABLED'] == False else False)
    elif args.signal:
        plugin.update_setting('VAR_CPU_USAGE_KILL_SIGNAL', args.signal)
    elif args.max_consumers > 0:
        plugin.update_setting('VAR_CPU_USAGE_MAX_CONSUMERS', args.max_consumers)
        
    plugin.read_config(defaults_dict)
    click_to_kill = plugin.configuration['VAR_CPU_USAGE_CLICK_TO_KILL']
    debug_enabled = plugin.configuration['VAR_CPU_USAGE_DEBUG_ENABLED']
    signal = plugin.configuration['VAR_CPU_USAGE_KILL_SIGNAL']
    max_consumers = plugin.configuration['VAR_CPU_USAGE_MAX_CONSUMERS']
    command_length = 125
    cpu_type = util.get_sysctl('machdep.cpu.brand_string')
    cpu_family = get_cpu_family_strings().get(int(util.get_sysctl('hw.cpufamily')), int(util.get_sysctl('hw.cpufamily')))
    max_cpu_freq = cpu_freq().max if cpu_freq().max is not None else None
    individual_cpu_pct = []
    combined_cpu_pct = []

    individual_cpu_percent = cpu_times_percent(interval=1.0, percpu=True)

    for i, cpu_instance in enumerate(individual_cpu_percent):
        individual_cpu_pct.append(get_time_stats_tuple(cpu=i, cpu_type=cpu_type, user=cpu_instance.user, system=cpu_instance.system, nice=cpu_instance.nice, idle=cpu_instance.idle))
    combined_cpu_pct.append(combine_stats(individual_cpu_pct, cpu_type))

    plugin.print_menu_title(f'CPU: user {util.pad_float(combined_cpu_pct[0].user)}%, sys {util.pad_float(combined_cpu_pct[0].system)}%, idle {util.pad_float(combined_cpu_pct[0].idle)}%')
    plugin.print_menu_separator()
    plugin.print_update_time()
    plugin.print_menu_separator()
    if cpu_type is not None:
        processor = cpu_type
        if cpu_family:
            processor = processor + f' ({cpu_family})'
        if max_cpu_freq:
            processor = processor + f' @ {util.pad_float(max_cpu_freq / 1000)} GHz'
        plugin.print_menu_item(f'Processor: {processor}')
        
    for cpu in individual_cpu_pct:
        plugin.print_menu_item(f'Core {str(cpu.cpu)}: user {cpu.user}%, sys {cpu.system}%, idle {cpu.idle}%')

    top_cpu_consumers = get_top_cpu_usage()
    if len(top_cpu_consumers) > 0:
        if len(top_cpu_consumers) > max_consumers:
            top_cpu_consumers = top_cpu_consumers[0:max_consumers]
        plugin.print_menu_item(
            f'Top {len(top_cpu_consumers)} CPU Consumers',
        )
        for consumer in top_cpu_consumers:
            command = consumer['command']
            cpu_usage = consumer['cpu_usage']
            pid = consumer['pid']
            user = consumer['user']
            padding_width = 6
            icon = util.get_process_icon(user, click_to_kill)
            cpu_usage = f'{str(cpu_usage)}%'
            cmd = ['kill', f'-{util.get_signal_map()[signal]}', pid] if click_to_kill else []
            plugin.print_menu_item(
                f'--{icon}{cpu_usage.rjust(padding_width)} - {command}',
                cmd=cmd,
                emojize=True,
                length=command_length,
                symbolize=False,
                terminal=False,
                trim=False,
            )
    plugin.print_menu_separator()
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if click_to_kill else "--Enable"} "Click to Kill"',
        cmd=[plugin.plugin_name, '--click-to-kill'],
        refresh=True,
        terminal=False,
    )
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} "Debugging" menu',
        cmd=[plugin.plugin_name, '--debug'],
        refresh=True,
        terminal=False,
    )
    plugin.print_menu_item('--Kill Signal')
    for key, _ in util.get_signal_map().items():
        color = 'blue' if key == signal else 'black'
        plugin.print_menu_item(
            f'----{key}',
            cmd=[plugin.plugin_name, '--signal', key],
            color=color,
            refresh=True,
            terminal=False,
        )
    plugin.print_menu_item('--Maximum Number of Top Consumers')
    for number in range(1, 51):
        if number %5 == 0:
            color = 'blue' if number == max_consumers else 'black'
            plugin.print_menu_item(
                f'----{number}',
                cmd=[plugin.plugin_name, '--max-consumers', number],
                color=color,
                refresh=True,
                terminal=False,
            )
    if debug_enabled:
        plugin.display_debug_data()
    plugin.print_menu_item('Refresh', refresh=True)

if __name__ == '__main__':
    main()
