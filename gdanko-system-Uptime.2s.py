#!/usr/bin/env python3

# <xbar.title>Uptime</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show system uptime</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-system-Uptime.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_SYSTEM_UPTIME_DEBUG_ENABLED=false"): Show debugging menu</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

from collections import namedtuple
from swiftbar import util
from swiftbar.plugin import Plugin
import argparse
import datetime
import re
import time

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args

def get_duration(seconds):
    try:
        seconds = int(seconds)
        days = int(seconds / 86400)
        hours = int(((seconds - (days * 86400)) / 3600))
        minutes = int(((seconds - days * 86400 - hours * 3600) / 60))
        secs = int((seconds - (days * 86400) - (hours * 3600) - (minutes * 60)))

        duration = namedtuple('duration', 'days hours minutes seconds')
        return duration(days=days, hours=hours, minutes=minutes, seconds=secs)
    except:
        return None

def get_boot_time():
    returncode, stdout, _ = util.execute_command('sysctl -n kern.boottime')
    if returncode != 0:
        return None
    pattern = re.compile(r'sec = ([0-9]{10,13})')
    match = re.search(pattern, stdout)
    if match:
        timestamp = int(match.group(1))
        return timestamp
    return None

def get_duration_tuple():
    boot_time = get_boot_time()
    if boot_time:
        return boot_time, get_duration(int(time.time()) - boot_time)
    else:
        return None, None

def main():
    plugin = Plugin()
    defaults_dict = {
        'VAR_SYSTEM_UPTIME_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
    }
    plugin.read_config(defaults_dict)
    args = configure()
    if args.debug:
        plugin.update_setting('VAR_SYSTEM_UPTIME_DEBUG_ENABLED', True if plugin.configuration['VAR_SYSTEM_UPTIME_DEBUG_ENABLED'] == False else False)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_SYSTEM_UPTIME_DEBUG_ENABLED']

    boot_time, duration_tuple = get_duration_tuple()
    if duration_tuple:
        uptime = []
        if duration_tuple.days > 0:
            uptime.append(f'{duration_tuple.days} {"day" if duration_tuple.days == 1 else "days"}')
        uptime.append(f'{str(duration_tuple.hours).zfill(2)}:{str(duration_tuple.minutes).zfill(2)}')
        plugin.print_menu_title(f'up {" ".join(uptime)}')
        plugin.print_menu_separator()
        plugin.print_menu_item(f'Last boot: {datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")}')
    else:
        plugin.print_menu_item('Uptime: N/A')
        plugin.print_menu_separator()
        plugin.print_menu_item('Failed to determine boot time')
    plugin.print_menu_separator()
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
