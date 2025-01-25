#!/usr/bin/env python3

# <xbar.title>Network Throughput</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show the current network throughput for a given interface</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/master/gdanko-network-NetworkThroughput.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_NET_THROUGHPUT_INTERFACE="en0"): The network interface to measure.</xbar.var>
# <xbar.var>string(VAR_NET_THROUGHPUT_VERBOSE="false"): Show more verbose detail.</xbar.var>

from collections import namedtuple, OrderedDict
from swiftbar import util
from swiftbar.plugin import Plugin
import argparse
import os
import re
import subprocess
import sys
import time

try:
    from psutil import net_io_counters
except ModuleNotFoundError:
    print('Error: missing "psutil" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install psutil')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    parser.add_argument('--verbose', help='Toggle verbose mode', required=False, default=False, action='store_true')
    parser.add_argument('--interface', help='The name of the interface to monitor', required=False)
    args = parser.parse_args()
    return args

def get_io_counter_tuple(interface=None, bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0, errin=0, errout=0, dropin=0, dropout=0):
    net_io = namedtuple('net_io', 'interface bytes_sent bytes_recv packets_sent packets_recv errin errout dropin dropout')
    return net_io(interface=interface, bytes_sent=bytes_sent, bytes_recv=bytes_recv, packets_sent=packets_sent, packets_recv=packets_recv, errin=errin, errout=errout, dropin=dropin, dropout=dropout)

def get_interface_data_tuple(interface=None, flags=None, mac=None, inet=None, inet6=None):
    interface_data = namedtuple('interface_data', 'interface flags mac inet inet6')
    return interface_data(interface=interface, flags=flags, mac=mac, inet=inet, inet6=inet6)

def get_data(interface=None):
    io_counters = net_io_counters(pernic=True)
    if interface in io_counters:
        return get_io_counter_tuple(
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

def get_interface_data(interface):
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
    return get_interface_data_tuple(interface=interface, flags=flags, mac=mac, inet=inet, inet6=inet6)

def get_public_ip():
    returncode, stdout, _ = util.execute_command('curl https://ifconfig.io')
    return stdout if stdout else None
 
def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_NET_THROUGHPUT_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_NET_THROUGHPUT_INTERFACE': {
            'default_value': 'en0',
            'valid_values': util.find_valid_interfaces(),
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

    network_throughput = get_io_counter_tuple(
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
    plugin.print_menu_separator()
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
        f'{"--Disable" if debug_enabled else "--Enable"} debug data',
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
    for ifname in util.find_valid_interfaces():
        color = 'blue' if ifname == interface else 'black'
        plugin.print_menu_item(
            f'----{ifname}',
            color=color,
            cmd=[plugin.plugin_name, '--interface', ifname],
            refresh=True,
            terminal=False,
        )
    if debug_enabled:
        plugin.display_debug_data()

if __name__ == '__main__':
    main()
