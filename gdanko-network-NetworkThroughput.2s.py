#!/usr/bin/env python3

# <xbar.title>Network Throughput</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show the current network throughput for a given interface</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/master/gdanko-network-NetworkThroughput.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_NET_THROUGHPUT_DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_NET_THROUGHPUT_INTERFACE=en0): The network interface to measure.</xbar.var>
# <xbar.var>string(VAR_NET_THROUGHPUT_VERBOSE=false): Show more verbose detail.</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_NET_THROUGHPUT_DEBUG_ENABLED=false, VAR_NET_THROUGHPUT_INTERFACE=en0, VAR_NET_THROUGHPUT_VERBOSE=false]</swiftbar.environment>

from collections import OrderedDict
from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import NamedTuple, Union
import argparse
import os
import re
import subprocess
import sys
import time

class IoCounters(NamedTuple):
    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int

class InterfaceData(NamedTuple):
    interface: str
    flags: str
    mac: str
    inet: str
    inet6: str

try:
    from psutil import net_io_counters
except ModuleNotFoundError:
    print('Error: missing "psutil" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install psutil')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def configure() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    parser.add_argument('--verbose', help='Toggle verbose mode', required=False, default=False, action='store_true')
    parser.add_argument('--interface', help='The name of the interface to monitor', required=False)
    args = parser.parse_args()
    return args

def get_data(interface: str=None) -> IoCounters:
    io_counters = net_io_counters(pernic=True)
    if interface in io_counters:
        return IoCounters(
            interface    = interface,
            bytes_sent   = io_counters[interface].bytes_sent,
            bytes_recv   = io_counters[interface].bytes_recv,
            packets_sent = io_counters[interface].packets_sent,
            packets_recv = io_counters[interface].packets_recv,
            errin        = io_counters[interface].errin,
            errout       = io_counters[interface].errout,
            dropin       = io_counters[interface].dropin,
            dropout      = io_counters[interface].dropout,
        )
    else:
        # DO SOMETHING HERE
        print('oops! interface not found!')
        exit(1)

def get_interface_data(interface: str=None) -> InterfaceData:
    flags, mac, inet, inet6 = None, None, None, None
    command = f'ifconfig {interface}'
    returncode, stdout, _ = util.execute_command(command)
    if stdout:
        match = re.findall(r'flags=\d+\<([A-Z0-9,]+)\>', stdout, re.MULTILINE)
        if match:
            flags = match[0]
        match = re.findall(r'^\s+ether ([a-z0-9:]+)$', stdout, re.MULTILINE)
        if match:
            mac = match[0]
        match = re.findall(r'inet\s+(\d+\.\d+\.\d+\.\d+)', stdout, re.MULTILINE)
        if match:
            inet = match[0]
        match = re.findall(r'inet6\s+([a-z0-9:]+)', stdout, re.MULTILINE)
        if match:
            inet6 = match[0]
    return InterfaceData(interface=interface, flags=flags, mac=mac, inet=inet, inet6=inet6)

def get_public_ip() -> Union[str, None]:
    returncode, stdout, _ = util.execute_command('curl https://ifconfig.io')
    return stdout if stdout else None
 
def main() -> None:
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_NET_THROUGHPUT_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_NET_THROUGHPUT_INTERFACE': {
            'default_value': 'en0',
            'valid_values': util.find_valid_network_interfaces(),
        },
        'VAR_NET_THROUGHPUT_VERBOSE': {
            'default_value': False,
            'valid_values': [True, False],
        },
    }
    plugin.read_config(defaults_dict)
    args = configure()
    if args.debug:
        plugin.update_setting('VAR_NET_THROUGHPUT_DEBUG_ENABLED', True if plugin.configuration['VAR_NET_THROUGHPUT_DEBUG_ENABLED'] == False else False)
    elif args.interface:
        plugin.update_setting('VAR_NET_THROUGHPUT_INTERFACE', args.interface)
    elif args.verbose:
        plugin.update_setting('VAR_NET_THROUGHPUT_VERBOSE', True if plugin.configuration['VAR_NET_THROUGHPUT_VERBOSE'] == False else False)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_NET_THROUGHPUT_DEBUG_ENABLED']
    interface = plugin.configuration['VAR_NET_THROUGHPUT_INTERFACE']
    vebose_enabled = plugin.configuration['VAR_NET_THROUGHPUT_VERBOSE']

    interface_data = get_interface_data(interface)
    public_ip = get_public_ip()

    first_sample = get_data(interface=interface)
    time.sleep(1)
    second_sample = get_data(interface=interface)

    network_throughput = IoCounters(
        interface    = interface,
        bytes_sent   = second_sample.bytes_sent - first_sample.bytes_sent,
        bytes_recv   = second_sample.bytes_recv - first_sample.bytes_recv,
        packets_sent = second_sample.packets_sent - first_sample.packets_sent,
        packets_recv = second_sample.packets_recv - first_sample.packets_recv,
        errin        = second_sample.errin - first_sample.errin,
        errout       = second_sample.errout - first_sample.errout,
        dropin       = second_sample.dropin - first_sample.dropin,
        dropout      = second_sample.dropout - first_sample.dropout,
    )
    plugin.print_menu_title(f'{network_throughput.interface} {util.process_bytes(network_throughput.bytes_recv)} RX / {util.process_bytes(network_throughput.bytes_sent)} TX')
    interface_output = OrderedDict()
    if interface_data.flags:
        interface_output['Flags'] = interface_data.flags
    if interface_data.mac:
        interface_output['Hardware Address'] = interface_data.mac
    if interface_data.inet:
        interface_output['IPv4 Address'] = interface_data.inet
    if interface_data.inet6:
        interface_output['IPv6 Address'] = interface_data.inet6
    if public_ip:
        interface_output['Public IP'] = public_ip
    if vebose_enabled:
        if network_throughput.dropin is not None:
            interface_output['Inbound Packets Dropped/sec'] = network_throughput.dropin
        if network_throughput.dropout is not None:
            interface_output['Outbound Packets Dropped/sec'] = network_throughput.dropout
        if network_throughput.errin is not None:
            interface_output['Inbound Errors/sec'] = network_throughput.errin
        if network_throughput.errout is not None:
            interface_output['Outbound Errors/sec'] = network_throughput.errout
        if second_sample.dropin is not None:
            interface_output['Inbound Packets Dropped (total)'] = second_sample.dropin
        if second_sample.dropout is not None:
            interface_output['Outbound Packets Dropped (total)'] = second_sample.dropout
        if second_sample.errin is not None:
            interface_output['Inbound Errors (total)'] = second_sample.errin
        if second_sample.errout is not None:
            interface_output['Outbound Errors (total)'] = second_sample.errout
    plugin.print_ordered_dict(interface_output, justify='left')
    plugin.print_menu_separator()
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} "Debugging" menu',
        cmd=[plugin.plugin_name, '--debug'],
        terminal=False,
        refresh=True,
    )
    plugin.print_menu_item(
        f'{"--Disable" if vebose_enabled else "--Enable"} verbose mode',
        cmd=[plugin.plugin_name, '--verbose'],
        terminal=False,
        refresh=True,
    )
    plugin.print_menu_item('--Interface')
    for ifname in util.find_valid_network_interfaces():
        color = 'blue' if ifname == interface else 'black'
        plugin.print_menu_item(
            f'----{ifname}',
            color=color,
            cmd=[plugin.plugin_name, '--interface', ifname],
            refresh=True,
            terminal=False,
        )
    if debug_enabled:
        plugin.display_debugging_menu()

if __name__ == '__main__':
    main()
