#!/usr/bin/env python3

# <xbar.title>Network Throughput</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show the current network throughput for a given interface</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/master/Network/gdanko-network-NetworkThroughput.2s.py</xbar.abouturl>
# <xbar.var>string(VAR_NET_THROUGHPUT_INTERFACE="en0"): The network interface to measure.</xbar.var>

from collections import namedtuple
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

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_defaults():
    interface = os.getenv('VAR_NET_THROUGHPUT_INTERFACE', 'en0') 
    return interface

def get_io_counter_tuple(interface=None, bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0, errin=0, errout=0, dropin=0, dropout=0):
    net_io = namedtuple('net_io', 'interface bytes_sent bytes_recv packets_sent packets_recv errin errout dropin dropout')
    return net_io(interface=interface, bytes_sent=bytes_sent, bytes_recv=bytes_recv, packets_sent=packets_sent, packets_recv=packets_recv, errin=errin, errout=errout, dropin=dropin, dropout=dropout)

def get_percent_stats_tuple(cpu='cpu-total', user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_percent = namedtuple('cpu_percent', 'cpu user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_percent(cpu=cpu, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

def get_interface_data_tuple(interface=None, flags=None, mac=None, inet=None, inet6=None):
    interface_data = namedtuple('interface_data', 'interface flags mac inet inet6')
    return interface_data(interface=interface, flags=flags, mac=mac, inet=inet, inet6=inet6)

def process_bytes(num):
    suffix = 'B'
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f'{round(num, 2)} {unit}{suffix}/s'
        num = num / 1024
    return f'{pad_float(num)} Yi{suffix}'

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

def external_command(command=[]):
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr

def get_interface_data(interface):
    flags, mac, inet, inet6 = None, None, None, None
    retcode, stdout, stderr = external_command(['/sbin/ifconfig', interface])
    if retcode == 0:
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
    retcode, stdout, stderr = external_command(['curl', 'https://ifconfig.io'])
    if retcode == 0:
        return stdout.strip()
    return None
 
def main():
    interface = get_defaults()
    interface_data = get_interface_data(interface)
    public_ip = get_public_ip()

    firstSample = get_data(interface=interface)
    time.sleep(1)
    secondSample = get_data(interface=interface)

    network_throughput = get_io_counter_tuple(
        interface    = interface,
        bytes_sent   = secondSample.bytes_sent - firstSample.bytes_sent,
        bytes_recv   = secondSample.bytes_recv - firstSample.bytes_recv,
        packets_sent = secondSample.packets_sent - firstSample.packets_sent,
        packets_recv = secondSample.packets_recv - firstSample.packets_recv,
        errin        = secondSample.errin - firstSample.errin,
        errout       = secondSample.errout - firstSample.errout,
        dropin       = secondSample.dropin - firstSample.dropin,
        dropout      = secondSample.dropout - firstSample.dropout,
    )
    print(f'{network_throughput.interface} {process_bytes(network_throughput.bytes_recv)} RX / {process_bytes(network_throughput.bytes_sent)} TX')
    print('---')
    if interface_data.flags:
        print(f'Flags: {interface_data.flags}')
    if interface_data.mac:
        print(f'Hardware Address: {interface_data.mac}')
    if interface_data.inet:
        print(f'IPv4 Address: {interface_data.inet}')
    if interface_data.mac:
        print(f'IPv6 Address: {interface_data.inet6}')
    if public_ip:
        print(f'Public Address: {public_ip}')


if __name__ == '__main__':
    main()
