#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system memery usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_MEM_USAGE_CLICK_TO_KILL="false"): Will clicking a member of the top offender list attempt to kill it?</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_KILL_SIGNAL=<int>): The Darwin kill signal to use when killing a process</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_MAX_CONSUMERS=<int>): Maximum number of offenders to display</xbar.var>

from collections import namedtuple
from swiftbar import util
from swiftbar.plugin import Plugin
import argparse
import json
import os
import re
import time

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable', help='Disable "Click to Kill" functionality', required=False, default=False, action='store_true')
    parser.add_argument('--enable', help='Enable "Click to Kill" functionality', required=False, default=False, action='store_true')
    parser.add_argument('--max-consumers', help='Maximum number of memory consumers to display', required=False, default=0, type=int)
    parser.add_argument('--signal', help='The signal level to use when killing a process', required=False)
    args = parser.parse_args()
    return args

def get_memory_tuple(total=None, available=None, percent=None, used=None, free=None, active=None, inactive=None, wired=None):
    svmem = namedtuple('svmem', 'total available percent used free active inactive wired')
    return svmem(total=total, available=available, percent=percent, used=used, free=free, active=active, inactive=inactive, wired=wired)

def get_memory_pressure_value(pagesize, pattern, string):
    match = re.search(pattern, string)
    return int(match.group(1)) * pagesize if match else None

def get_memory_details():
    command = f'system_profiler SPMemoryDataType -json'
    retcode, stdout, _ = util.execute_command(command)
    if retcode == 0:
        try:
            json_data = json.loads(stdout)
            meminfo = json_data['SPMemoryDataType'][0]
            return meminfo['dimm_type'], meminfo['dimm_manufacturer'], None
        except Exception as e:
            return '', '', e
    else:
        return '', '', e

def virtual_memory():
    # https://github.com/giampaolo/psutil/blob/master/psutil/_psosx.py
    round_ = 1
    retcode, stdout, _ = util.execute_command('memory_pressure')
    if retcode == 0:
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

    return get_memory_tuple(
        total=memory_pressure_output['total'],
        available=memory_pressure_output['available'],
        percent=percent, used=memory_pressure_output['used'],
        free=memory_pressure_output['free'],
        active=memory_pressure_output['active'],
        inactive=memory_pressure_output['inactive'],
        wired=memory_pressure_output['wired']
    )    

def get_top_memory_usage():
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

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_MEM_USAGE_CLICK_TO_KILL': {
            'default_value': True,
            'valid_values': [True, False],
        },
        'VAR_MEM_USAGE_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_MEM_USAGE_KILL_SIGNAL': {
            'default_value': 'SIGQUIT',
            'valid_values': list(util.get_signal_map().keys()),
        },
        'VAR_MEM_USAGE_MAX_CONSUMERS': {
            'default_value': 30,
        }
    }

    args = configure()
    if args.enable:
        plugin.update_setting('VAR_MEM_USAGE_CLICK_TO_KILL', True)
    elif args.disable:
        plugin.update_setting('VAR_MEM_USAGE_CLICK_TO_KILL', False)
    elif args.signal:
        plugin.update_setting('VAR_MEM_USAGE_KILL_SIGNAL', args.signal)
    elif args.max_consumers > 0:
        plugin.update_setting('VAR_MEM_USAGE_MAX_CONSUMERS', args.max_consumers)
    
    plugin.read_config(defaults_dict)
    click_to_kill = plugin.configuration['VAR_MEM_USAGE_CLICK_TO_KILL']
    debug_enabled = plugin.configuration['VAR_MEM_USAGE_DEBUG_ENABLED']
    signal = plugin.configuration['VAR_MEM_USAGE_KILL_SIGNAL']
    max_consumers = plugin.configuration['VAR_MEM_USAGE_MAX_CONSUMERS']
    command_length = 125
    memory_type, memory_brand, err = get_memory_details()
    mem = virtual_memory()
    if mem:
        used = util.format_number(mem.used)
        total = util.format_number(mem.total)
        plugin.print_menu_item(f'Memory: {used} / {total}')
        plugin.print_menu_separator()
        plugin.print_menu_item(f'Updated {util.get_timestamp(int(time.time()))}')
        plugin.print_menu_separator()
        if not err:
            print(f'Memory: {memory_brand} {memory_type}')
        print(f'Total: {util.format_number(mem.total)}')
        print(f'Available: {util.format_number(mem.available)}')
        print(f'Used: {util.format_number(mem.used)}')
        print(f'Free: {util.format_number(mem.free)}')
        print(f'Active: {util.format_number(mem.active)}')
        print(f'Inactive: {util.format_number(mem.inactive)}')
        print(f'Wired: {util.format_number(mem.wired)}')

        top_memory_consumers = get_top_memory_usage()
        if len(top_memory_consumers) > 0:
            if len(top_memory_consumers) > max_consumers:
                top_memory_consumers = top_memory_consumers[0:max_consumers]
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
                icon = util.get_process_icon(user, click_to_kill)
                cmd = ['kill', f'-{util.get_signal_map()[signal]}', pid] if click_to_kill else []
                plugin.print_menu_item(
                    f'--{icon}{util.format_number(bytes).rjust(padding_width)} - {command}',
                    cmd=cmd,
                    emojize=True,
                    length=command_length,
                    symbolize=False,
                    terminal=False,
                    trim=False,
                )
            plugin.print_menu_item(f'--Total: {util.format_number(consumer_total)}')
        plugin.print_menu_separator()
        plugin.print_menu_item('Settings')
        plugin.print_menu_item(
            f'{"--Disable" if click_to_kill else "--Enable"} "Click to Kill"',
            cmd=[plugin.plugin_name, f'{"--disable" if click_to_kill else "--enable"}'],
            terminal=False,
            refresh=True,
        )
        plugin.print_menu_item('--Kill Signal')
        for key, _ in util.get_signal_map().items():
            color = 'blue' if key == signal else 'black'
            plugin.print_menu_item(
                f'----{key}',
                color=color,
                cmd=[plugin.plugin_name, '--signal', key],
                refresh=True,
                terminal=False,
            )
        plugin.print_menu_item('--Maximum Number of Top Consumers')
        for number in range(1, 51):
            if number %5 == 0:
                color = 'blue' if number == max_consumers else 'black'
                plugin.print_menu_item(
                    f'----{number}',
                    color=color,
                    cmd=[plugin.plugin_name, '--max-consumers', number],
                    refresh=True,
                    terminal=False,
                )
        if debug_enabled:
            plugin.display_debug_data()
    else:
        plugin.print_menu_item('Memory: Unknown')
        plugin.print_menu_separator()
        plugin.print_menu_item('Failed to parse vm_stat')

if __name__ == '__main__':
    main()
