#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.5.3</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system memery usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_MEM_USAGE_EXTENDED_DETAILS_ENABLED=true): Show extended information about the installed memory</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_CLICK_TO_KILL=false): Will clicking a member of the top offender list attempt to kill it?</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_KILL_SIGNAL=SIGQUIT): The BSD kill signal to use when killing a process</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_MAX_CONSUMERS=30): Maximum number of offenders to display</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_UNIT=auto): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei, auto]</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_MEM_USAGE_EXTENDED_DETAILS_ENABLED=true, VAR_MEM_USAGE_CLICK_TO_KILL=false, VAR_MEM_USAGE_KILL_SIGNAL=SIGQUIT, VAR_MEM_USAGE_MAX_CONSUMERS=30]</swiftbar.environment, VAR_MEM_USAGE_UNIT=auto>

from collections import namedtuple, OrderedDict
from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import Any, Dict, List, NamedTuple, Tuple, Union
import json
import re

class SystemMemory(NamedTuple):
    total: int
    available: int
    percent: float
    used: int
    free: int
    active: int
    inactive: int
    wired: int
    speculative: int

def get_memory_pressure_value(pagesize: int=0, pattern: str=None, string: str=None) -> Union[int, None]:
    match = re.search(pattern, string)
    return int(match.group(1)) * pagesize if match else None

def get_memory_details() -> Tuple[str, ...]:
    command = f'system_profiler SPMemoryDataType -json'
    returncode, stdout, _ = util.execute_command(command)
    if returncode == 0:
        try:
            json_data = json.loads(stdout)
            meminfo = json_data['SPMemoryDataType'][0]
            return meminfo['dimm_type'], meminfo['dimm_manufacturer'], None
        except Exception as e:
            return '', '', e
    else:
        return '', '', e

def virtual_memory() -> SystemMemory:
    # https://github.com/giampaolo/psutil/blob/master/psutil/_psosx.py
    round_ = 1
    returncode, stdout, _ = util.execute_command('memory_pressure')
    if returncode == 0:
        memory_pressure = stdout
    else:
        return None
    
    memory_pressure_output = {}
    memory_pressure_map = {
        'total': r'(\d+) pages with a page size of',
        'free': r'Pages free:\s+(\d+)',
        'active': r'Pages active:\s+(\d+)',
        'inactive': r'Pages inactive:\s+(\d+)',
        'wired': r'Pages wired down:\s+(\d+)',
        'speculative': r'Pages speculative:\s+(\d+)',
    }
    pagesize = get_memory_pressure_value(1, r'page size of\s+(\d+)', memory_pressure)
    if not pagesize:
        return None

    for key, pattern in memory_pressure_map.items():
        result = get_memory_pressure_value(pagesize, pattern, memory_pressure)
        if result:
            memory_pressure_output[key] = result
        else:
            return None
    
    memory_pressure_output['free'] -= memory_pressure_output['speculative']
    memory_pressure_output['available'] = memory_pressure_output['inactive'] + memory_pressure_output['free']
    memory_pressure_output['used'] = memory_pressure_output['active'] + memory_pressure_output['wired']

    try:
        percent =  (float(memory_pressure_output['used']) / memory_pressure_output['total']) * 100
    except ZeroDivisionError:
        percent = 0.0
    else:
        if round_ is not None:
            percent = round(percent, round_)

    return SystemMemory(
        total=memory_pressure_output['total'],
        available=memory_pressure_output['available'],
        percent=percent, used=memory_pressure_output['used'],
        free=memory_pressure_output['free'],
        active=memory_pressure_output['active'],
        inactive=memory_pressure_output['inactive'],
        wired=memory_pressure_output['wired'],
        speculative=memory_pressure_output['speculative'],
    )

def get_top_memory_usage() -> List[Dict[str, Any]]:
    memory_info = []
    command = f'ps -axm -o rss,pid,user,comm | tail -n+2'
    returncode, stdout, _ = util.execute_command(command)
    if returncode ==  0:
        lines = stdout.strip().split('\n')
        for line in lines:
            match = re.search(r'^(\d+)\s+(\d+)\s+([A-Za-z0-9\-\.\_]+)\s+(.*)$', line)
            if match:
                bytes = int(match.group(1)) * 1024
                pid = match.group(2)
                user = match.group(3)
                command_name = match.group(4)
                if bytes > 0:
                    memory_info.append({'command': command_name, 'bytes': bytes, 'pid': pid, 'user': user})

    return sorted(memory_info, key=lambda item: item['bytes'], reverse=True)

def main() -> None:
    plugin = Plugin(no_brew=True)
    plugin.defaults_dict['VAR_MEM_USAGE_EXTENDED_DETAILS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--extended-details',
            'title': 'extended memory details',
        },
    }
    plugin.defaults_dict['VAR_MEM_USAGE_TOP_CONSUMERS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--top-consumers',
            'title': 'the "Top Memory Consumers" menu',
        },
    }
    plugin.defaults_dict['VAR_MEM_USAGE_CLICK_TO_KILL'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--click-to-kill',
            'title': '"Click to Kill" functionality',
        },
    }
    plugin.defaults_dict['VAR_MEM_USAGE_KILL_SIGNAL'] = {
        'default_value': 'SIGQUIT',
        'valid_values': list(util.get_signal_map().keys()),
        'type': str,
        'setting_configuration': {
            'default': False,
            'flag': '--signal',
            'title': 'Kill Signal',
        },
    }
    plugin.defaults_dict['VAR_MEM_USAGE_MAX_CONSUMERS'] = {
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
    plugin.defaults_dict['VAR_MEM_USAGE_UNIT'] = {
        'default_value': 'auto',
        'valid_values': util.valid_storage_units(),
        'type': str,
        'setting_configuration': {
            'default': False,
            'flag': '--unit',
            'title': 'Unit',
        },
    }
    plugin.setup()

    if not plugin.configuration['VAR_MEM_USAGE_TOP_CONSUMERS_ENABLED']:
        del plugin.configuration['VAR_MEM_USAGE_CLICK_TO_KILL']
        del plugin.configuration['VAR_MEM_USAGE_KILL_SIGNAL']
        del plugin.configuration['VAR_MEM_USAGE_MAX_CONSUMERS'] 
    
    command_length = 125
    memory_type, memory_brand, err = get_memory_details()
    mem = virtual_memory()
    if mem:
        used = util.format_number(mem.used) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.used, plugin.configuration['VAR_MEM_USAGE_UNIT'])
        total = util.format_number(mem.total) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.total, plugin.configuration['VAR_MEM_USAGE_UNIT'])
        plugin.print_menu_title(f'Memory: {used} / {total}')
        if plugin.configuration['VAR_MEM_USAGE_EXTENDED_DETAILS_ENABLED']:
            memory_output = OrderedDict()
            if not err:
                memory_output['Memory'] = f'{memory_brand} {memory_type}'
            memory_output['Total'] = util.format_number(mem.total) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.total, plugin.configuration['VAR_MEM_USAGE_UNIT'])
            memory_output['Available'] = util.format_number(mem.available) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.available, plugin.configuration['VAR_MEM_USAGE_UNIT'])
            memory_output['Used'] = util.format_number(mem.used) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.used, plugin.configuration['VAR_MEM_USAGE_UNIT'])
            memory_output['Free'] = util.format_number(mem.free) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.free, plugin.configuration['VAR_MEM_USAGE_UNIT'])
            memory_output['Active'] = util.format_number(mem.active) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.active, plugin.configuration['VAR_MEM_USAGE_UNIT'])
            memory_output['Inactive'] = util.format_number(mem.inactive) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.inactive, plugin.configuration['VAR_MEM_USAGE_UNIT'])
            memory_output['Wired'] = util.format_number(mem.wired) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.wired, plugin.configuration['VAR_MEM_USAGE_UNIT'])
            memory_output['Speculative'] = util.format_number(mem.speculative) if plugin.configuration['VAR_MEM_USAGE_UNIT'] == 'auto' else util.byte_converter(mem.speculative, plugin.configuration['VAR_MEM_USAGE_UNIT'])
            plugin.print_ordered_dict(memory_output, justify='left')

        if plugin.configuration['VAR_MEM_USAGE_TOP_CONSUMERS_ENABLED']:
            top_memory_consumers = get_top_memory_usage()
            if len(top_memory_consumers) > 0:
                plugin.print_menu_separator()
                if len(top_memory_consumers) > plugin.configuration['VAR_MEM_USAGE_MAX_CONSUMERS']:
                    top_memory_consumers = top_memory_consumers[0:plugin.configuration['VAR_MEM_USAGE_MAX_CONSUMERS']]
                plugin.print_menu_item(
                    f'Top {len(top_memory_consumers)} Memory Consumers',
                )
                consumer_total = 0
                for consumer in top_memory_consumers:
                    command = consumer['command']
                    bytes = consumer['bytes']
                    pid = consumer['pid']
                    user = consumer['user']
                    consumer_total += bytes
                    padding_width = 12
                    icon = util.get_process_icon(user, plugin.configuration['VAR_MEM_USAGE_CLICK_TO_KILL'])
                    cmd = ['kill', f'-{util.get_signal_map()[plugin.configuration["VAR_MEM_USAGE_KILL_SIGNAL"]]}', pid] if plugin.configuration["VAR_MEM_USAGE_CLICK_TO_KILL"] else []
                    plugin.print_menu_item(
                        f'--{icon}{util.format_number(bytes).rjust(padding_width)} - {command}',
                        cmd=cmd,
                        emojize=True,
                        length=command_length,
                        refresh=True,
                        symbolize=False,
                        terminal=False,
                        trim=False,
                    )
                plugin.print_menu_item(f'--Total: {util.format_number(consumer_total)}')
    else:
        plugin.print_menu_item('Memory: Unknown')
        plugin.print_menu_separator()
        plugin.print_menu_item('Failed to parse vm_stat')
    plugin.render_footer()

if __name__ == '__main__':
    main()
