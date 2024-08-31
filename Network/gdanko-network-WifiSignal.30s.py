#!/usr/bin/env python3

# <xbar.title>WiFi Signal</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the current WiFi signal strength</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/master/Network/gdanko-network-WifiSignal.30s.py</xbar.abouturl>
# <xbar.var>string(VAR_WIFI_STATUS_INTERFACE="en0"): The network interface to measure.</xbar.var>

import json
import os
import re
import subprocess

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_defaults():
    interface = os.getenv('VAR_WIFI_STATUS_INTERFACE', 'en0') 
    return interface

def main():
    interface = get_defaults()

    p = subprocess.Popen(
        ['/usr/sbin/system_profiler', 'SPAirPortDataType', '-json', 'detailLevel', 'basic'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        try:
            my_interface = None
            profiler_data = json.loads(stdout)
            interfaces = profiler_data["SPAirPortDataType"][0]["spairport_airport_interfaces"]
            for iface in interfaces:
                if iface['_name'] == interface:
                    my_interface = iface
                    break
            if iface:
                spairport_signal_noise = my_interface['spairport_current_network_information']['spairport_signal_noise']
                ssid = iface['spairport_current_network_information']['_name']
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
                        elif rating >= -60:
                            rating = 'Good'
                        elif rating >= -70:
                            rating = 'Reliable'
                        elif rating >= -80:
                            rating = 'Bad'
                        elif rating >= -90:
                            rating = 'Unreliable'
                        else:
                            rating = 'Unknown'

                        print(f'WiFI: {ssid} - {rating}')
                        print('---')
                        print(f'Signal:   {signal} dBm ({rating})')
                        print(f'Noise:    {noise} dBm')
                        print(f'Quality:  {quality}% ({snr} dBm SNR)')
                else:
                    print('WiFi status: N/A')
                    print('---')
                    print('Failed to parse the system_profiler results')
            else:
                print('WiFi status: N/A')
                print('---')
                print(f'{interface} not found')
        except Exception as e:
            print(e)
            print('WiFi status: N/A')
            print('---')
            print('Failed to parse the JSOn from system_profiler')
    else:
        print('WiFi status: N/A')
        print('---')
        print(stderr)
    
if __name__ == '__main__':
    main()
