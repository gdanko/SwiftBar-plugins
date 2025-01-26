#!/usr/bin/env python3

# <xbar.title>Swap Usage</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system swap usage in the format used/total</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-SwapUsage.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_SWAP_USAGE_UNIT="Gi"): The unit to use. [K, Ki, M, Mi, G, Gi, T, Ti, P, Pi, E, Ei]</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

from collections import namedtuple
import os
import plugin
import re
import sys
import time

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_swap_usage_tuple(total=0, used=0, free=0):
    swap_usage = namedtuple('swap_usage', 'total free used')
    return swap_usage(total=total, free=free, used=used)

def get_defaults(config_dir, plugin_name):
    vars_file = os.path.join(config_dir, plugin_name) + '.vars.json'
    default_values = {
        'VAR_SWAP_USAGE_UNIT': 'Gi',
    }
    defaults = plugin.read_config(vars_file, default_values)
    valid_units = ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei']
    return defaults['VAR_SWAP_USAGE_UNIT'] if defaults['VAR_SWAP_USAGE_UNIT'] in valid_units else 'Gi'

def get_swap_usage():
    command = 'sysctl -n vm.swapusage'
    returncode, stdout, _ = plugin.execute_command(command)
    match = re.search(r'^total = (\d+\.\d+)M\s+used = (\d+\.\d+)M\s+free = (\d+\.\d+)M\s+', stdout)
    if match:
        total = int(float(match.group(1))) * 1024 * 1024
        used = int(float(match.group(2))) * 1024 * 1024
        free = int(float(match.group(3))) * 1024 * 1024
        return get_swap_usage_tuple(total=total, free=free, used=used)
    return None

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    invoker, config_dir = plugin.get_config_dir()
    plugin_name = os.path.abspath(sys.argv[0])
    unit = get_defaults(config_dir, os.path.basename(plugin_name))
    mem = get_swap_usage()
    used = plugin.byte_converter(mem.used, unit)
    total = plugin.byte_converter(mem.total, unit)
    print(f'Swap: {used} / {total}')
    print('---')
    print(f'Updated {plugin.get_timestamp(int(time.time()))}')

if __name__ == '__main__':
    main()
