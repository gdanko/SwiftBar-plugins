#!/usr/bin/env python3

# <xbar.title>CPU Percent</xbar.title>
# <xbar.version>v0.5.4</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display CPU % for user, system, and idle</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-CpuPercent.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_CPU_USAGE_EXTENDED_DETAILS_ENABLED=true): Show extended information about the CPU and its cores</xbar.var>
# <xbar.var>string(VAR_CPU_USAGE_CLICK_TO_KILL=false): Will clicking a member of the top offender list attempt to kill it?</xbar.var>
# <xbar.var>string(VAR_CPU_USAGE_KILL_SIGNAL=SIGQUIT): The BSD kill signal to use when killing a process</xbar.var>
# <xbar.var>string(VAR_CPU_USAGE_MAX_CONSUMERS=30): Maximum number of offenders to display</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_CPU_USAGE_EXTENDED_DETAILS_ENABLED=true, VAR_CPU_USAGE_CLICK_TO_KILL=false, VAR_CPU_USAGE_KILL_SIGNAL=SIGQUIT, VAR_CPU_USAGE_MAX_CONSUMERS=30]</swiftbar.environment>

from collections import namedtuple, OrderedDict
from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import Any, Dict, List, NamedTuple
import pkg_resources
import re

class CpuTimes(NamedTuple):
    cpu: str
    cpu_type: str
    idle: float
    nice: float
    system: float
    user: float
    # iowait: float
    # irq: float
    # softirq: float
    # steal: float
    # guest: float
    # guestnice: float

def get_cpu_family_strings() -> Dict[int, str]:
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

def combine_stats(cpu_time_stats: List=None, cpu_type: str=None) -> CpuTimes:
    idle      = 0.0
    nice      = 0.0
    system    = 0.0
    user      = 0.0

    for cpu_time_stat in cpu_time_stats:
        idle   += cpu_time_stat.idle
        nice   += cpu_time_stat.nice
        system += cpu_time_stat.system
        user   += cpu_time_stat.user
    return CpuTimes(
        cpu=0,
        cpu_type=cpu_type,
        idle=(idle / len(cpu_time_stats)),
        nice=(nice / len(cpu_time_stats)),
        system=(system / len(cpu_time_stats)),
        user=(user / len(cpu_time_stats)),
    )

def get_top_cpu_usage() -> List[Dict[str, Any]]:
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

def main() -> None:
    plugin = Plugin(no_brew=True)
    plugin.defaults_dict['VAR_CPU_USAGE_EXTENDED_DETAILS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--extended-details',
            'title': 'extended memory details',
        },
    }
    plugin.defaults_dict['VAR_CPU_USAGE_TOP_CONSUMERS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--top-consumers',
            'title': 'the "Top CPU Consumers" menu',
        },
    }
    plugin.defaults_dict['VAR_CPU_USAGE_CLICK_TO_KILL'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--click-to-kill',
            'title': '"Click to Kill" functionality',
        },
    }
    plugin.defaults_dict['VAR_CPU_USAGE_KILL_SIGNAL'] = {
        'default_value': 'SIGQUIT',
        'valid_values': list(util.get_signal_map().keys()),
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--signal',
            'increment': 10,
            'title': 'Kill Signal',
        },
    }
    plugin.defaults_dict['VAR_CPU_USAGE_MAX_CONSUMERS'] = {
        'default_value': 30,
        'minmax': namedtuple('minmax', ['min', 'max'])(10, 100),
        'type': int,
        'setting_configuration': {
            'default': False,
            'flag': '--max-consumers',
            'title': 'Maximum Number of Consumers',
            'increment': 10,
        },
    }
    plugin.setup()

    if not plugin.configuration['VAR_CPU_USAGE_TOP_CONSUMERS_ENABLED']:
        del plugin.configuration['VAR_CPU_USAGE_CLICK_TO_KILL']
        del plugin.configuration['VAR_CPU_USAGE_KILL_SIGNAL']
        del plugin.configuration['VAR_CPU_USAGE_MAX_CONSUMERS'] 

    required = {'psutil'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed
    if len(missing) == 0:
        from psutil import cpu_freq, cpu_times_percent
        command_length = 125
        cpu_type = util.get_sysctl('machdep.cpu.brand_string')
        cpu_family = get_cpu_family_strings().get(int(util.get_sysctl('hw.cpufamily')), int(util.get_sysctl('hw.cpufamily')))
        max_cpu_freq = cpu_freq().max if cpu_freq().max is not None else None
        individual_cpu_pct = []
        combined_cpu_pct = []

        individual_cpu_percent = cpu_times_percent(interval=1.0, percpu=True)

        for i, cpu_instance in enumerate(individual_cpu_percent):
            individual_cpu_pct.append(CpuTimes(cpu=i, cpu_type=cpu_type, user=cpu_instance.user, system=cpu_instance.system, nice=cpu_instance.nice, idle=cpu_instance.idle))
        combined_cpu_pct.append(combine_stats(individual_cpu_pct, cpu_type))

        plugin.print_menu_title(f'CPU: user {util.pad_float(combined_cpu_pct[0].user)}%, sys {util.pad_float(combined_cpu_pct[0].system)}%, idle {util.pad_float(combined_cpu_pct[0].idle)}%')
        if plugin.configuration['VAR_CPU_USAGE_EXTENDED_DETAILS_ENABLED']:
            if cpu_type is not None:
                processor = cpu_type
                if cpu_family:
                    processor = processor + f' ({cpu_family})'
                if max_cpu_freq:
                    processor = processor + f' @ {util.pad_float(max_cpu_freq / 1000)} GHz'
                plugin.print_menu_item(f'Processor: {processor}')
                
            for cpu in individual_cpu_pct:
                plugin.print_menu_item(f'Core {str(cpu.cpu)}: user {cpu.user}%, sys {cpu.system}%, idle {cpu.idle}%')

        if 'VAR_CPU_USAGE_TOP_CONSUMERS_ENABLED' in plugin.configuration and plugin.configuration['VAR_CPU_USAGE_TOP_CONSUMERS_ENABLED']:
            top_cpu_consumers = get_top_cpu_usage()
            if len(top_cpu_consumers) > 0:
                plugin.print_menu_separator()
                if len(top_cpu_consumers) > plugin.configuration['VAR_CPU_USAGE_MAX_CONSUMERS']:
                    top_cpu_consumers = top_cpu_consumers[0:plugin.configuration['VAR_CPU_USAGE_MAX_CONSUMERS']]
                plugin.print_menu_item(
                    f'Top {len(top_cpu_consumers)} CPU Consumers',
                )
                for consumer in top_cpu_consumers:
                    command = consumer['command']
                    cpu_usage = consumer['cpu_usage']
                    pid = consumer['pid']
                    user = consumer['user']
                    padding_width = 6
                    icon = util.get_process_icon(user, plugin.configuration['VAR_CPU_USAGE_CLICK_TO_KILL'])
                    cpu_usage = f'{str(cpu_usage)}%'
                    cmd = ['kill', f'-{util.get_signal_map()[plugin.configuration["VAR_CPU_USAGE_KILL_SIGNAL"]]}', pid] if plugin.configuration['VAR_CPU_USAGE_CLICK_TO_KILL'] else []
                    plugin.print_menu_item(
                        f'--{icon}{cpu_usage.rjust(padding_width)} - {command}',
                        cmd=cmd,
                        emojize=True,
                        length=command_length,
                        symbolize=False,
                        terminal=False,
                        trim=False,
                    )
    else:
        plugin.print_menu_title('CPU: Error')
        plugin.print_menu_separator()
        plugin.print_menu_item(f'Please install the following packages via pip: {", ".join(missing)}')
    plugin.render_footer()

if __name__ == '__main__':
    main()
