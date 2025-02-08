#!/usr/bin/env python3

# <xbar.title>WiFi Signal</xbar.title>
# <xbar.version>v0.5.2</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the current WiFi signal strength</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/master/gdanko-network-WifiSignal.30s.py</xbar.abouturl>
# <xbar.var>string(VAR_WIFI_STATUS_EXTENDED_DETAILS_ENABLED=true): Show extended information about the WiFi connection.</xbar.var>
# <xbar.var>string(VAR_WIFI_STATUS_INTERFACE=en0): The network interface to measure.</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_WIFI_STATUS_EXTENDED_DETAILS_ENABLED=true, VAR_WIFI_STATUS_INTERFACE=en0]</swiftbar.environment>

from collections import OrderedDict
from swiftbar import images, util
from swiftbar.plugin import Plugin
from typing import Any, Dict
import json
import re

def get_profiler_data(stdout: str=None) -> Dict[str, Any]:
    try:
        profiler_data = json.loads(stdout)
        return profiler_data, None
    except Exception as e:
        return None, f'Failed to parse the JSON from system_profiler: {e}'

def main() -> None:
    plugin = Plugin()
    plugin.defaults_dict['VAR_WIFI_STATUS_EXTENDED_DETAILS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--extended-details',
            'title': 'extended WiFi details',
        },
    }
    plugin.defaults_dict['VAR_WIFI_STATUS_INTERFACE'] = {
        'default_value': 'en0',
        'valid_values': util.find_valid_wifi_interfaces(),
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--interface',
            'title': 'Interface',
        },
    }
    plugin.setup()

    my_interface = None
    rating = 'Unknown'
    returncode, stdout, _ = util.execute_command('system_profiler SPAirPortDataType -json detailLevel basic')
    if returncode == 0 and stdout:
        profiler_data, err = get_profiler_data(stdout)
        if err:
            plugin.success = False
            plugin.error_messages.append(err)
        else:
            if 'SPAirPortDataType' in profiler_data:
                interfaces = profiler_data['SPAirPortDataType'][0]["spairport_airport_interfaces"]
                for iface in interfaces:
                    if iface['_name'] == plugin.configuration['VAR_WIFI_STATUS_INTERFACE']:
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

                                    wifi_output = OrderedDict()
                                    wifi_output['Device'] = plugin.configuration['VAR_WIFI_STATUS_INTERFACE']
                                    wifi_output['Channel'] = channel
                                    wifi_output['Mode'] = mode
                                    wifi_output['Signal'] = f'{signal} dBm ({rating})'
                                    wifi_output['Noise'] = f'{noise} dBm'
                                    wifi_output['Quality'] = f'{quality}% ({snr} dBm SNR)'
                            else:
                                plugin.success = False
                                plugin.error_messages.append('Failed to extract signal/noise data from the system_profiler results')
                        else:
                            plugin.success = False
                            plugin.error_messages.append('Failed to find signal/noise data in the system_profiler results')
                    else:
                        plugin.success = False
                        plugin.error_messages.append('Failed to find current network information data in the system_profiler results')
                else:
                    plugin.success = False
                    plugin.error_messages.append(f'Failed to find interface data for {plugin.configuration["VAR_WIFI_STATUS_INTERFACE"]} in the system_profiler results')
    else:
        plugin.success = False
        plugin.error_messages.append('Failed to parse the system_profiler results')

    if plugin.success:
        plugin.print_menu_title(f'WiFI: {ssid} - {rating}')
        if plugin.configuration['VAR_WIFI_STATUS_EXTENDED_DETAILS_ENABLED']:
            plugin.print_ordered_dict(wifi_output, justify='left')
    else:
        plugin.print_menu_title('WiFi status: N/A')
        for error_message in plugin.error_messages:
            plugin.print_menu_item(error_message)
    plugin.render_footer()

if __name__ == '__main__':
    main()
