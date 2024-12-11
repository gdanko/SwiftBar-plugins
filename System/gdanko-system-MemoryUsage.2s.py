#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system memery usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_MEM_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_KILL_PROCESS="false"): Will clicking a member of the top offender list attempt to kill it?</xbar.var>
# <xbar.var>string(VAR_MEM_USAGE_MAX_OFFENDERS=<int>): Maximum number of offenders to display</xbar.var>

import argparse
import datetime
import getpass
import json
import os
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

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument("--enable", help="Enable click to kill", required=False, default=False, type=bool)
    parser.add_argument("--disable", help="Disable click to kill", required=False, default=False, type=bool)
    parser.add_argument("--max-offenders", help="Maximum number of offenders to display", required=False, default=0, type=int)
    args = parser.parse_args()
    return args

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def read_config(param, default):
    plugin = os.path.abspath(sys.argv[0])
    jsonfile = f'{plugin}.vars.json'
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as fh:
            contents = json.load(fh)
            if param in contents:
                return contents[param]
    return default

def toggle_kill_process():
    plugin = os.path.abspath(sys.argv[0])
    jsonfile = f'{plugin}.vars.json'
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as fh:
            contents = json.load(fh)
            if 'VAR_MEM_USAGE_KILL_PROCESS' in contents:
                new_value = 'true' if contents['VAR_MEM_USAGE_KILL_PROCESS'] == 'false' else 'false'
                contents['VAR_MEM_USAGE_KILL_PROCESS'] = new_value
                with open(jsonfile, 'w') as fh:
                    fh.write(json.dumps(contents))

def update_max_offenders(max_offenders):
    plugin = os.path.abspath(sys.argv[0])
    jsonfile = f'{plugin}.vars.json'
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as fh:
            contents = json.load(fh)
            if 'VAR_MEM_USAGE_MAX_OFFENDERS' in contents:
                contents['VAR_MEM_USAGE_MAX_OFFENDERS'] = max_offenders
                with open(jsonfile, 'w') as fh:
                    fh.write(json.dumps(contents))    

def get_defaults():
    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    unit = os.getenv('VAR_MEM_USAGE_UNIT', 'Gi') 
    if not unit in valid_units:
        unit = 'Gi'

    kill_process = read_config('VAR_MEM_USAGE_KILL_PROCESS', "false")
    kill_process = True if kill_process == "true" else False
    max_offenders = read_config('VAR_MEM_USAGE_MAX_OFFENDERS', 30)

    return unit, kill_process, max_offenders

def get_memory_details():
    p = subprocess.Popen(
        ['/usr/sbin/system_profiler', 'SPMemoryDataType', '-json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        try:
            json_data = json.loads(stdout)
            meminfo = json_data['SPMemoryDataType'][0]
            return meminfo['dimm_type'], meminfo['dimm_manufacturer'], None
        except Exception as e:
            return '', '', e
    else:
        return '', '', stderr
  
def byte_converter(bytes, unit):
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{pad_float(bytes / (divisor ** prefix_map[prefix]))} {unit}{suffix}'

def get_command_output(command):
    commands = re.split(r'\s*\|\s*', command)
    previous = None
    output = None
    for i, command in enumerate(commands):
        cmd = re.split(r'\s+', command)
        if previous:
            p = subprocess.Popen(cmd, stdin=previous.stdout, stdout=subprocess.PIPE)
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        if i < len(commands) - 1:
            previous = p
        else:
            output = p.stdout.read().strip().decode()
    return output

def get_top_memory_usage():
    memory_info = []
    command = '/bin/ps -axm -o rss,pid,user,comm | /usr/bin/tail -n+2 | /usr/bin/sort -rn -k 1'
    output = get_command_output(command)
    if output:
        lines = output.strip().split('\n')
        for line in lines:
            match = re.search(r'^(\d+)\s+(\d+)\s+([A-Za-z0-9\-\.\_]+)\s+(.*)$', line)
            if match:
                memory_usage = int(match.group(1)) * 1024
                pid = match.group(2)
                user = match.group(3)
                command_name = match.group(4)
                if float(memory_usage) > 0.0:
                    memory_info.append({
                        'command': command_name,
                        'memory_usage': memory_usage,
                        'pid': pid,
                        'user': user,
                    })
        return memory_info

def get_disabled_flag(process_owner, kill_process):
    if kill_process:
        return 'false' if process_owner == getpass.getuser() else 'true'
    else:
        return 'true'

def main():
    args = configure()
    if args.enable or args.disable:
        toggle_kill_process()
    elif args.max_offenders > 0:
        update_max_offenders(args.max_offenders)
    unit, kill_process, max_offenders = get_defaults()
    command_length = 125
    font_size = 12
    plugin = os.path.abspath(sys.argv[0])
    memory_type, memory_brand, err = get_memory_details()

    mem = virtual_memory()
    used = byte_converter(mem.used, unit)
    total = byte_converter(mem.total, unit)
    print(f'Memory: {used} / {total}')
    print('---')
    print(f'Updated {get_timestamp(int(time.time()))}')
    print('---')
    if not err:
        print(f'Memory: {memory_brand} {memory_type}')
    print(f'Total: {byte_converter(mem.total, unit)}')
    print(f'Available: {byte_converter(mem.available, unit)}')
    print(f'Used: {byte_converter(mem.used, unit)}')
    print(f'Free: {byte_converter(mem.free, unit)}')
    print(f'Active: {byte_converter(mem.active, unit)}')
    print(f'Inactive: {byte_converter(mem.inactive, unit)}')
    print(f'Wired: {byte_converter(mem.wired, unit)}')

    memory_offenders = get_top_memory_usage()
    if len(memory_offenders) > 0:
        if len(memory_offenders) > max_offenders:
            memory_offenders = memory_offenders[0:max_offenders]
        print(f'Top {len(memory_offenders)} Memory Consumers')
        offender_total = 0
        for offender in memory_offenders:
            command = offender['command']
            memory_usage = offender['memory_usage']
            pid = offender['pid']
            user = offender['user']
            offender_total += memory_usage
            print(f'--{":skull: " if kill_process else ""}{byte_converter(memory_usage, "G")} - {command} | length={command_length} | size={font_size} | shell=/bin/sh | param1="-c" | param2="kill {pid}" | disabled={get_disabled_flag(user, kill_process)}')
        print(f'--Total: {byte_converter(offender_total, "G")}')
    print('---')
    print(f'{"Disable" if kill_process else "Enable"} "Click to Kill" | shell="{plugin}" | param1="{"--disable" if kill_process else "--enable"}" | terminal=false | refresh=true')
    print('Maximum Number of Top Consumers')
    for number in range(1, 51):
        if number %5 == 0:
            print(f'--{number} | shell="{plugin}" param1="--max-offenders" | param2={number} | terminal=false | refresh=true')
if __name__ == '__main__':
    main()
