#!/usr/bin/env python3

# <xbar.title>Disk Consumers</xbar.title>
# <xbar.version>v0.5.2</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show files and directories using the most disk space for a given path</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-DiskConsumers.5m.py</xbar.abouturl>
# <xbar.var>string(PATHS=/): A comma-delimited list of paths</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[PATHS=/]</swiftbar.environment>

from swiftbar import util
from swiftbar.plugin import Plugin
from typing import List, NamedTuple
import os
import re
import time

class DiskConsumer(NamedTuple):
    Path: str
    Bytes: int

def get_consumers(path: str=None) -> List[DiskConsumer]:
    consumers: List[DiskConsumer] = []
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
                        consumers.append(DiskConsumer(Path=path.strip(), Bytes=bytes))

    return sorted(consumers, key=lambda item: item.Bytes, reverse=True)

def main() -> None:
    start_time = util.unix_time_in_ms()
    plugin = Plugin(disable_brew=True)
    plugin.defaults_dict['PATHS'] = {
        'default_value': '~',
        'type': str,
    }
    plugin.setup()

    plugin.print_menu_title('Disk Consumption')
    if len(re.split(r'\s*,\s*', plugin.configuration['PATHS'])) > 0:
        for path in re.split(r'\s*,\s*', plugin.configuration['PATHS']):
            plugin.print_menu_item(os.path.expanduser(path))
            total = 0
            consumers = get_consumers(path)
            for consumer in consumers:
                total += consumer.Bytes
                padding_width = 12
                icon = ':file_folder:' if os.path.isdir(consumer.Path) else ':page_facing_up:'
                plugin.print_menu_item(
                    f'--{icon}' + f'{util.format_number(consumer.Bytes).rjust(padding_width)} - {consumer.Path}',
                    cmd=['open', f'"{consumer.Path}"'],
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
    plugin.render_footer()

if __name__ == '__main__':
    main()
