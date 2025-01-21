#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system memery usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_MEM_USAGE_CLICK_TO_KILL="false"): Will clicking a member of the top offender list attempt to kill it?</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_KILL_SIGNAL=<int>): The Darwin kill signal to use when killing a process</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_MAX_CONSUMERS=<int>): Maximum number of offenders to display</xbar.var>

from pathlib import Path
import argparse
import datetime
import getpass
import json
import os
import plugin
import re
import subprocess
import sys
import time

try:
    from psutil import virtual_memory
except ModuleNotFoundError:
    print('Error: missing "psutil" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install psutil')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def get_command_output(command):
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    return stdout.strip().decode(), stderr.strip().decode()

def get_config_dir():
    ppid = os.getppid()
    stdout, stderr = get_command_output(f'/bin/ps -o command -p {ppid} | tail -n+2')
    if stderr:
        return None
    if stdout:
        if stdout == '/Applications/xbar.app/Contents/MacOS/xbar':
            return os.path.basename(stdout), os.path.dirname(os.path.abspath(sys.argv[0]))
        elif stdout == '/Applications/SwiftBar.app/Contents/MacOS/SwiftBar':
            return os.path.basename(stdout), os.path.join(Path.home(), '.config', 'SwiftBar')
    # return 'local', Path.home()
    return 'xbar', '/Users/gdanko/Library/Application Support/xbar/plugins'

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable', help='Disable "Click to Kill" functionality', required=False, default=False, action='store_true')
    parser.add_argument('--enable', help='Enable "Click to Kill" functionality', required=False, default=False, action='store_true')
    parser.add_argument('--max-consumers', help='Maximum number of memory consumers to display', required=False, default=0, type=int)
    parser.add_argument('--signal', help='The signal level to use when killing a process', required=False)
    args = parser.parse_args()
    return args

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def byte_converter(bytes, unit):
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{pad_float(bytes / (divisor ** prefix_map[prefix]))} {unit}{suffix}'

def read_config(vars_file, param, default):
    if os.path.exists(vars_file):
        try:
            with open(vars_file, 'r') as fh:
                contents = json.load(fh)
                if param in contents:
                    return contents[param]
                return default
        except:
            return default
    return default

def write_config(jsonfile, contents):
    with open(jsonfile, 'w') as fh:
        fh.write(json.dumps(contents, indent=4))

def update_setting(config_dir, plugin_name, key, value):
    vars_file = os.path.join(config_dir, plugin_name) + '.vars.json'
    if os.path.exists(vars_file):
        with open(vars_file, 'r') as fh:
            contents = json.load(fh)
            if key in contents:
                contents[key] = value
                write_config(vars_file, contents)

def get_defaults(config_dir, plugin_name):
    vars_file = os.path.join(config_dir, plugin_name) + '.vars.json'
    click_to_kill = read_config(vars_file, 'VAR_MEM_USAGE_CLICK_TO_KILL', 'true')
    click_to_kill = True if click_to_kill == 'true' else False
    signal = read_config(vars_file, 'VAR_MEM_USAGE_KILL_SIGNAL', 'SIGQUIT')
    max_consumers = int(read_config(vars_file, 'VAR_MEM_USAGE_MAX_CONSUMERS', 30))

    return click_to_kill, signal, max_consumers

def get_memory_details():
    command = f'system_profiler SPMemoryDataType -json'
    stdout, stderr = get_command_output(command)
    if stdout:
        try:
            json_data = json.loads(stdout)
            meminfo = json_data['SPMemoryDataType'][0]
            return meminfo['dimm_type'], meminfo['dimm_manufacturer'], None
        except Exception as e:
            return '', '', e
    else:
        return '', '', e

def get_top_memory_usage():
    memory_info = []
    command = f'/bin/ps -axm -o rss,pid,user,comm | tail -n+2'
    stdout, stderr = get_command_output(command)
    if stdout:
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

def get_icon(process_owner, click_to_kill):
    if click_to_kill:
        if process_owner == getpass.getuser():
            return ':skull:'
        else:
            return ':no_entry_sign:'
    else:
        return ''

def format_number(size):
    factor = 1024
    bytes = factor
    megabytes = bytes * factor
    gigabytes = megabytes * factor
    if size < gigabytes:
        if size < megabytes:
            if size < bytes:
                return f'{size} B'
            else:
                return byte_converter(size, "Ki")
        else:
            return byte_converter(size, "Mi")
    else:
        return byte_converter(size, "Gi")

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    invoker, config_dir = get_config_dir()
    plugin_name = os.path.abspath(sys.argv[0])
    vars_file = os.path.join(config_dir, os.path.basename(plugin_name)) + '.vars.json'
    args = configure()
    if args.enable:
        update_setting(config_dir, os.path.basename(plugin_name), 'VAR_MEM_USAGE_CLICK_TO_KILL', 'true')
    elif args.disable:
        update_setting(config_dir, os.path.basename(plugin_name), 'VAR_MEM_USAGE_CLICK_TO_KILL', 'false')
    elif args.signal:
        update_setting(config_dir, os.path.basename(plugin_name), 'VAR_MEM_USAGE_KILL_SIGNAL', args.signal)
    elif args.max_consumers > 0:
        update_setting(config_dir, os.path.basename(plugin_name), 'VAR_MEM_USAGE_MAX_CONSUMERS', args.max_consumers)
    
    click_to_kill, signal, max_consumers = get_defaults(config_dir, os.path.basename(plugin_name))
    command_length = 125
    font_name = 'Andale Mono'
    font_size = 12
    font_data = f'size="{font_size}" font="{font_name}"'
    memory_type, memory_brand, err = get_memory_details()
    mem = virtual_memory()
    used = format_number(mem.used)
    total = format_number(mem.total)
    print(f'Memory: {used} / {total}')
    print('---')
    print(f'open {vars_file} | bash=open param1="{vars_file}"')
    print(f'Updated {get_timestamp(int(time.time()))}')
    print('---')
    if not err:
        print(f'Memory: {memory_brand} {memory_type}')
    print(f'Total: {format_number(mem.total)}')
    print(f'Available: {format_number(mem.available)}')
    print(f'Used: {format_number(mem.used)}')
    print(f'Free: {format_number(mem.free)}')
    print(f'Active: {format_number(mem.active)}')
    print(f'Inactive: {format_number(mem.inactive)}')
    print(f'Wired: {format_number(mem.wired)}')

    top_memory_consumers = get_top_memory_usage()
    if len(top_memory_consumers) > 0:
        if len(top_memory_consumers) > max_consumers:
            top_memory_consumers = top_memory_consumers[0:max_consumers]
        print(f'Top {len(top_memory_consumers)} Memory Consumers')
        consumer_total = 0
        for consumer in top_memory_consumers:
            command = consumer['command']
            bytes = consumer['bytes']
            pid = consumer['pid']
            user = consumer['user']
            consumer_total += bytes
            padding_width = 12
            icon = get_icon(user, click_to_kill)
            bits = [
                f'--{icon}{format_number(bytes).rjust(padding_width)} - {command}',
                f'bash=kill param1="{plugin.get_signal_map()[signal]}" param2="{pid}" terminal=false',
                font_data,
                'trim=false',
                f'length={command_length}',
            ]
            if invoker == 'SwiftBar':
                bits.append('emojize=true symbolize=false')
            print(' | '.join(bits))
        print(f'--Total: {format_number(consumer_total)} | {font_data}')
    print('---')
    print('Settings')
    print(f'{"--Disable" if click_to_kill else "--Enable"} "Click to Kill" | bash="{plugin_name}" param1="{"--disable" if click_to_kill else "--enable"}" terminal=false | refresh=true')
    print('--Kill Signal')
    for key, _ in plugin.get_signal_map().items():
        bits = [
            f'----{key}',
            f'bash="{plugin_name}" param1="--signal" param2="{key}" terminal=false',
            'refresh=true',
        ]
        if key == signal:
            bits.insert(1, 'color=blue')
        print(' | '.join(bits))
    print('--Maximum Number of Top Consumers')
    for number in range(1, 51):
        if number %5 == 0:
            bits = [
                f'----{number}',
                f'bash="{plugin_name}" param1="--max-consumers" param2="{number}" terminal=false',
                'refresh=true',
            ]
            if number == max_consumers:
                bits.insert(1, 'color=blue')
            print(' | '.join(bits))

if __name__ == '__main__':
    main()
