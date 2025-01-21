#!/usr/bin/env python3

# <xbar.title>Swap Usage</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system swap usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-SwapUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_SWAP_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>

from collections import namedtuple
import os
import plugin
import re
import time

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_swap_usage_tuple(total=0, used=0, free=0):
    swap_usage = namedtuple('swap_usage', 'total free used')
    return swap_usage(total=total, free=free, used=used)

def get_defaults():
    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    unit = os.getenv('VAR_SWAP_USAGE_UNIT', 'Gi') 
    if not unit in valid_units:
        unit = 'Gi'
    return unit

def get_swap_usage():
    command = 'sysctl -n vm.swapusage'
    stdout, _ = plugin.get_command_output(command)
    match = re.search(r'^total = (\d+\.\d+)M\s+used = (\d+\.\d+)M\s+free = (\d+\.\d+)M\s+', stdout)
    if match:
        total = int(float(match.group(1))) * 1024 * 1024
        used = int(float(match.group(2))) * 1024 * 1024
        free = int(float(match.group(3))) * 1024 * 1024
        return get_swap_usage_tuple(total=total, free=free, used=used)
    return None

def main():
        unit = get_defaults()
        mem = get_swap_usage()
        used = plugin.byte_converter(mem.used, unit)
        total = plugin.byte_converter(mem.total, unit)
        print(f'Swap: {used} / {total}')
        print('---')
        print(f'Updated {plugin.get_timestamp(int(time.time()))}')

if __name__ == '__main__':
    main()
