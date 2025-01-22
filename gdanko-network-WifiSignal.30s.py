#!/usr/bin/env python3

# <xbar.title>WiFi Signal</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the current WiFi signal strength</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/master/Network/gdanko-network-WifiSignal.30s.py</xbar.abouturl>
# <xbar.var>string(VAR_WIFI_STATUS_INTERFACE="en0"): The network interface to measure.</xbar.var>

import json
import os
import plugin
import re
import sys
import time

def get_defaults(config_dir, plugin_name):
    vars_file = os.path.join(config_dir, plugin_name) + '.vars.json'
    default_values = {
        'VAR_WIFI_STATUS_INTERFACE': 'en0',
    }
    defaults = plugin.read_config(vars_file, default_values)
    return defaults['VAR_WIFI_STATUS_INTERFACE']

def get_profiler_data(stdout):
    try:
        profiler_data = json.loads(stdout)
        return profiler_data, None
    except Exception as e:
        return None, f'Failed to parse the JSON from system_profiler: {e}'

def main():
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    invoker, config_dir = plugin.get_config_dir()
    plugin_name = os.path.abspath(sys.argv[0])
    interface = get_defaults(config_dir, os.path.basename(plugin_name))
    stdout, _ = plugin.get_command_output('system_profiler SPAirPortDataType -json detailLevel basic')
    my_interface = None
    rating = 'Unknown'
    if stdout:
        profiler_data, err = get_profiler_data(stdout)
        if err is not None:
            print('WiFi status: N/A')
            print('---')
            print(err)
        else:
            if 'SPAirPortDataType' in profiler_data:
                interfaces = profiler_data['SPAirPortDataType'][0]["spairport_airport_interfaces"]
                for iface in interfaces:
                    if iface['_name'] == interface:
                        my_interface = iface
                        break
                if my_interface:
                    if 'spairport_current_network_information' in my_interface:
                        if 'spairport_signal_noise' in my_interface['spairport_current_network_information']:
                            spairport_signal_noise = my_interface['spairport_current_network_information']['spairport_signal_noise']
                            ssid = iface['spairport_current_network_information']['_name']
                            channel = iface['spairport_current_network_information']['spairport_network_channel']
                            mode = iface['spairport_current_network_information']['spairport_network_phymode']
                            pattern = re.compile(r'(-[\d]+)')
                            result = pattern.findall(spairport_signal_noise)
                            if result:
                                signal = int(result[0])
                                noise = int(result[1])
                                snr = signal - noise
                                quality = snr * 2
                                quality = quality if quality < 100 else 100
                                if signal:
                                    if signal >= -30:
                                        rating = 'Amazing'
                                    elif signal >= -50:
                                        rating = 'Excellent'
                                    elif signal >= -60:
                                        rating = 'Good'
                                    elif signal >= -70:
                                        rating = 'Reliable'
                                    elif signal >= -80:
                                        rating = 'Bad'
                                    elif signal >= -90:
                                        rating = 'Unreliable'
                                    else:
                                        rating = 'Unknown'
                                    print(f'WiFI: {ssid} - {rating}')
                                    print('---')
                                    print(f'Updated {plugin.get_timestamp(int(time.time()))}')
                                    print('---')
                                    print(f'Device: {interface}')
                                    print(f'Channel: {channel}')
                                    print(f'Mode: {mode}')
                                    print(f'Signal: {signal} dBm ({rating})')
                                    print(f'Noise: {noise} dBm')
                                    print(f'Quality: {quality}% ({snr} dBm SNR)')
                                    print('Refresh WiFi data | refresh=true')
                            else:
                                print('WiFi status: N/A')
                                print('---')
                                print('Failed to extract signal/noise data from the system_profiler results')  
                        else:
                            print('WiFi status: N/A')
                            print('---')
                            print('Failed to find signal/noise data in the system_profiler results')                           
                    else:
                        print('WiFi status: N/A')
                        print('---')
                        print('Failed to find current network information data in the system_profiler results')
            else:
                print('WiFi status: N/A')
                print('---')
                print('Failed to find interface data in the system_profiler results')
    else:
        print('WiFi status: N/A')
        print('---')
        print('Failed to parse the system_profiler results')

if __name__ == '__main__':
    main()
