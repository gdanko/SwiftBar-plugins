#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system memery usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_MEM_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>

import datetime
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

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_defaults():
    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    unit = os.getenv('VAR_MEM_USAGE_UNIT', 'Gi') 
    if not unit in valid_units:
        unit = 'Gi'
    return unit

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

def get_top_memory_usage():
    # This performs the equivalent of `ps -axm -o rss,comm | sort -rn -k 1 | head -n 10`
    command_length = 125
    number_of_offenders = 20
    memory_info = []
    cmd1 = ['/bin/ps', '-axm', '-o', 'rss,comm']
    cmd2 = ['sort', '-rn', '-k', '1']
    cmd3 = ['head', '-n', str(number_of_offenders)]

    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(cmd3, stdin=p2.stdout, stdout=subprocess.PIPE)
    output = p3.stdout.read().decode()
    lines = output.strip().split('\n')

    for line in lines:
        match = re.search(r'^(\d+)\s+(.*)$', line)
        if match:
            memory_usage = int(match.group(1)) * 1024
            command_name = match.group(2)
            if len(command_name) > command_length:
                command_name = command_name[0:command_length] + '...'

            memory_info.append({
                'command': command_name,
                'memory_usage': byte_converter(memory_usage, 'G'),
            })
    return memory_info

def main():
    get_top_memory_usage()
    unit = get_defaults()

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
        print(f'Top {len(memory_offenders)} Memory Consumers')
        for offender in memory_offenders:
            print(f'--{offender["command"]} - {offender["memory_usage"]}')

if __name__ == '__main__':
    main()
