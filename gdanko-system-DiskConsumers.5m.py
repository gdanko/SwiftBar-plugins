#!/usr/bin/env python3

# <xbar.title>Disk Consumers</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show files and directories using the most disk space for a given path</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-DiskConsumers.5m.py</xbar.abouturl>
# <xbar.var>string(VAR_DISK_CONSUMERS_PATHS="/"): A comma-delimited list of mount points</xbar.var>

import os
import plugin
import re
import sys
import time

def get_defaults(config_dir, plugin_name):
    vars_file = os.path.join(config_dir, plugin_name) + '.vars.json'
    default_values = {
        'VAR_DISK_CONSUMERS_PATHS': '~,~/Library',
    }
    defaults = plugin.read_config(vars_file, default_values)
    return re.split(r'\s*,\s*', defaults['VAR_DISK_CONSUMERS_PATHS'])

def get_consumers(path):
    consumers = []
    command = f'find {path} -depth 1 -exec du -sk {{}} \;'
    returncode, stdout, _ = plugin.execute_command(command)
    if stdout:
        lines = stdout.strip().split('\n')
        for line in lines:
            match = re.search(r'^(\d+)\s+(.*)$', line)
            if match:
                bytes = int(match.group(1)) * 1024
                path = match.group(2)
                if os.path.basename(path) not in ['.', '..']:
                    if bytes > 0:
                        consumers.append({'path': path.strip(), 'bytes': bytes})

    return sorted(consumers, key=lambda item: item['bytes'], reverse=True)

def main():
    start_time = plugin.unix_time_in_ms()
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    invoker, config_dir = plugin.get_config_dir()
    plugin_name = os.path.abspath(sys.argv[0])
    paths_list = get_defaults(config_dir, os.path.basename(plugin_name))
    font_name = 'Andale Mono'
    font_size = 13
    font_data = f'size="{font_size}" font="{font_name}"'

    print('Disk Consumption')
    print('---')
    if len(paths_list) > 0:
        for path in paths_list:
            print(os.path.expanduser(path))
            total = 0
            consumers = get_consumers(path)
            for consumer in consumers:
                bytes = consumer["bytes"]
                path = consumer["path"]
                total += bytes
                padding_width = 12
                icon = ':file_folder:' if os.path.isdir(path) else ':page_facing_up:'
                bits = [
                    f'--{icon}' + f'{plugin.format_number(bytes).rjust(padding_width)} - {path}',
                    f'bash=open param1=""{path}"" terminal=false',
                    font_data,
                    'trim=false',
                ]
                if invoker == 'SwiftBar':
                    bits.append('emojize=true symbolize=false')
                print(' | '.join(bits))
            print(f'--Total: {plugin.format_number(total)} | {font_data}')
    else:
        print('N/A')
    end_time = plugin.unix_time_in_ms()
    print(f'Data fetched at {plugin.get_timestamp(int(time.time()))} in {end_time - start_time}ms')
    print('Refresh data | refresh=true')

if __name__ == '__main__':
    main()
