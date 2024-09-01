#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system memery usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-MemoryUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_MEM_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>

import json
import os
import subprocess

def pad_float(number):
    return '{:.2f}'.format(float(number))

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

def main():
    try:
        from psutil import virtual_memory

        unit = get_defaults()

        memory_type, memory_brand, err = get_memory_details()

        mem = virtual_memory()
        used = byte_converter(mem.used, unit)
        total = byte_converter(mem.total, unit)
        print(f'Memory: {used} / {total}')
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

    except ModuleNotFoundError:
        print('Error: missing "psutil" library.')
        print('---')
        import sys
        import subprocess
        subprocess.run('pbcopy', universal_newlines=True,
                       input=f'{sys.executable} -m pip install psutil')
        print('Fix copied to clipboard. Paste on terminal and run.')

if __name__ == '__main__':
    main()
