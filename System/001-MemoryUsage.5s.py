#!/usr/bin/env python3

# <xbar.title>Memory Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Shows the current system memory usage.</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/master/System/memusage.5s.py</xbar.abouturl>
# <xbar.var>string(VAR_MEM_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>

import os

def byte_converter(bytes, unit):
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{round(bytes / (divisor ** prefix_map[prefix]), 2)} {unit}{suffix}'

def main():
    try:
        from psutil import virtual_memory

        valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
        default_unit = 'Gi'
        unit = os.getenv('VAR_MEM_USAGE_UNIT', default_unit)
        
        if unit != '':
            if not unit in valid_units:
                unit = default_unit
        else:
            unit = default_unit

        mem = virtual_memory()
        used = byte_converter(mem.used, unit)
        total = byte_converter(mem.total, unit)
        print(f'Memory: {used} / {total}')

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
