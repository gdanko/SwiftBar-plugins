#!/usr/bin/env python3

# <xbar.title>Disk Consumers</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show files and directories using the most disk space for a given path</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-DiskConsumers.5m.py</xbar.abouturl>
# <xbar.var>string(VAR_DISK_CONSUMERS_PATHS="/"): A comma-delimited list of mount points</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

from swiftbar import util
from swiftbar.plugin import Plugin
import argparse
import os
import re
import time

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args

def get_consumers(path):
    consumers = []
    command = f'find {path} -depth 1 -exec du -sk {{}} \;'
    _, stdout, _ = util.execute_command(command)
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
    start_time = util.unix_time_in_ms()
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_DISK_CONSUMERS_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_DISK_CONSUMERS_PATHS': {
            'default_value': '~',
            'split_values': True,
        },
    }

    plugin.read_config(defaults_dict)
    args = configure()
    if args.debug:
        plugin.update_setting('VAR_DISK_CONSUMERS_DEBUG_ENABLED', True if plugin.configuration['VAR_DISK_CONSUMERS_DEBUG_ENABLED'] == False else False)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_DISK_CONSUMERS_DEBUG_ENABLED']
    paths_list = re.split(r'\s*,\s*', plugin.configuration['VAR_DISK_CONSUMERS_PATHS'])

    plugin.print_menu_title('Disk Consumption')
    plugin.print_menu_separator()
    if len(paths_list) > 0:
        for path in paths_list:
            plugin.print_menu_item(os.path.expanduser(path))
            total = 0
            consumers = get_consumers(path)
            for consumer in consumers:
                bytes = consumer["bytes"]
                path = consumer["path"]
                total += bytes
                padding_width = 12
                icon = ':file_folder:' if os.path.isdir(path) else ':page_facing_up:'
                plugin.print_menu_item(
                    f'--{icon}' + f'{util.format_number(bytes).rjust(padding_width)} - {path}',
                    cmd=['open', f'"{path}"'],
                    emojize=True,
                    symbolize=False,
                    terminal=False,
                    trim=False,
                )
            plugin.print_menu_item(f'--Total: {util.format_number(total)}')
    else:
        plugin.print_menu_item('N/A')
    end_time = util.unix_time_in_ms()
    plugin.print_menu_item(f'Data fetched at {util.get_timestamp(int(time.time()))} in {end_time - start_time}ms')
    plugin.print_menu_separator()
    plugin.print_menu_item('Refresh data', refresh=True)
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} "Debugging" menu',
        cmd=[plugin.plugin_name, '--debug'],
        terminal=False,
        refresh=True,
    )
    if debug_enabled:
        plugin.display_debug_data()

if __name__ == '__main__':
    main()
