#!/usr/bin/env python3

# <xbar.title>Network Throughput</xbar.title>
# <xbar.version>v0.6.0</xbar.version>
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
import os
import re
import time

class IoCounters(NamedTuple):
    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    collisions: int

class InterfaceData(NamedTuple):
    interface: str
    flags: str
    mac: str
    inet: str
    inet6: str

def get_data(interface: str=None) -> Union[IoCounters, None]:
    returncode, stdout, stderr = util.execute_command(f'netstat -bid {interface}')
    if returncode == 0 and stdout:
        match = re.search(f'^({interface}\s+.*)', stdout, re.MULTILINE)
        if match:
            bits = re.split('\s+', match.group(1))
            return IoCounters(
                interface    = interface,
                bytes_sent   = int(bits[9]),
                bytes_recv   = int(bits[6]),
                packets_sent = int(bits[7]),
                packets_recv = int(bits[4]),
                errin        = int(bits[5]),
                errout       = int(bits[8]),
                collisions   = int(bits[10]),
            )
        else:
            # We need to handle this here
            return None
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
    plugin.defaults_dict = OrderedDict()
    plugin.defaults_dict['VAR_NET_THROUGHPUT_DEBUG_ENABLED'] = {
        'default_value': False,
        'valid_values': [True, False],
        'setting_configuration': {
            'default': False,
            'flag': '--debug',
            'help': 'Toggle the Debugging menu',
            'title': 'the "Debugging" menu',
            'type': bool,
        },
    }
    plugin.defaults_dict['VAR_NET_THROUGHPUT_VERBOSE'] = {
        'default_value': False,
        'valid_values': [True, False],
        'setting_configuration': {
            'default': False,
            'flag': '--verbose',
            'help': 'Toggle verbose mode',
            'title': 'verbose mode',
            'type': bool,
        },
    }
    plugin.defaults_dict['VAR_NET_THROUGHPUT_INTERFACE'] = {
        'default_value': 'en0',
        'valid_values': util.find_valid_network_interfaces(),
        'setting_configuration': {
            'default': None,
            'flag': '--interface',
            'title': 'Interface',
            'help': 'Select the interface to view',
            'type': str,
        },
    }
    plugin.read_config()
    plugin.generate_args()
    if plugin.args.debug:
        plugin.update_setting('VAR_NET_THROUGHPUT_DEBUG_ENABLED', True if plugin.configuration['VAR_NET_THROUGHPUT_DEBUG_ENABLED'] == False else False)
    elif plugin.args.interface:
        plugin.update_setting('VAR_NET_THROUGHPUT_INTERFACE', plugin.args.interface)
    elif plugin.args.verbose:
        plugin.update_setting('VAR_NET_THROUGHPUT_VERBOSE', True if plugin.configuration['VAR_NET_THROUGHPUT_VERBOSE'] == False else False)

    plugin.read_config()
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
        collisions   = second_sample.collisions - first_sample.collisions,
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
        if network_throughput.errin is not None:
            interface_output['Inbound Errors/sec'] = network_throughput.errin
        if network_throughput.errout is not None:
            interface_output['Outbound Errors/sec'] = network_throughput.errout
        if network_throughput.collisions is not None:
            interface_output['Collisions/sec'] = network_throughput.collisions
        if second_sample.errin is not None:
            interface_output['Inbound Errors (total)'] = second_sample.errin
        if second_sample.errout is not None:
            interface_output['Outbound Errors (total)'] = second_sample.errout
        if second_sample.collisions is not None:
            interface_output['Collisions (total)'] = second_sample.collisions

    plugin.print_ordered_dict(interface_output, justify='left')
    plugin.print_menu_separator()
    if plugin.defaults_dict:
        plugin.display_settings_menu()

    if debug_enabled:
        plugin.display_debugging_menu()
    plugin.print_menu_item('Refresh', refresh=True)

if __name__ == '__main__':
    main()
