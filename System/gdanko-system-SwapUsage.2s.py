#!/usr/bin/env python3

# <xbar.title>Swap Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system swap usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-SwapUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_SWAP_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>

import datetime
import os
import time

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_defaults():
    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    unit = os.getenv('VAR_SWAP_USAGE_UNIT', 'Gi') 
    if not unit in valid_units:
        unit = 'Gi'
    return unit

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
        from psutil import swap_memory

        unit = get_defaults()

        mem = swap_memory()
        used = byte_converter(mem.used, unit)
        total = byte_converter(mem.total, unit)
        print(f'Memory: {used} / {total}')
        print(f'Updated {get_timestamp(int(time.time()))}')
        print('---')

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
