#!/usr/bin/env python3

# <xbar.title>Earthquakes</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show information about earthquakes nearby</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-other-Earthquakes.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_EARTHQUAKES_DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_EARTHQUAKES_LIMIT=20): The maximum number of quakes to display</xbar.var>
# <xbar.var>string(VAR_EARTHQUAKES_MIN_MAGNITUDE=0): The minimum magnitude for quakes</xbar.var>
# <xbar.var>string(VAR_EARTHQUAKES_RADIUS_MILES=50): Radius in miles</xbar.var>
# <xbar.var>string(VAR_EARTHQUAKES_RADIUS_UNIT=m): miles or kilometers</xbar.var>
# <swiftbar.environment>[VAR_EARTHQUAKES_DEBUG_ENABLED=false, VAR_EARTHQUAKES_LIMIT=20, VAR_EARTHQUAKES_MIN_MAGNITUDE=0, VAR_EARTHQUAKES_RADIUS_MILES=50, VAR_EARTHQUAKES_RADIUS_UNIT=m]</swiftbar.environment>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>false</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

from collections import namedtuple, OrderedDict
from swiftbar import images, request, util
from swiftbar.plugin import Plugin
from typing import Any, Dict
import argparse
import datetime
import re
import time
import os

def configure() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    parser.add_argument('--limit', help='The maximum number of quakes to display', required=False, type=int)
    parser.add_argument('--magnitude', help='The minimum magnitude', required=False, type=int)
    parser.add_argument('--radius', help='The maximum radios in miles', required=False, type=int)
    parser.add_argument('--unit', help='The unit to use', required=False)
    args = parser.parse_args()
    return args

def get_quake_data(radius: int=0, magnitude: int=0, unit: str='m', limit: int=0) -> Dict[str, Any]:
    location = []
    returncode, public_ip, stdrrr = util.execute_command('curl https://ifconfig.io')
    if returncode != 0 or not public_ip:
        return None, {}, 'Failed to determine my public IP'
    
    status_code, geodata, err = request.swiftbar_request(url=f'https://ipinfo.io/{public_ip}/json', return_type='json')
    if status_code != 200:
        return None, {}, 'Failed to geolocate'
    
    if 'loc' not in geodata:
        return None, {}, 'Failed to geolocate'
    
    if 'city' in geodata and 'region' in geodata and 'country' in geodata:
        location = [
            geodata['city'],
            geodata['region'],
            geodata['country']
        ]
    if 'postal' in geodata:
        location.append(geodata['postal'])
    
    now = int(time.time())
    local_8601_start_time = datetime.datetime.fromtimestamp(now - 86400).isoformat('T', 'seconds')
    local_8601_end_time = datetime.datetime.fromtimestamp(now).isoformat('T', 'seconds')

    # https://earthquake.usgs.gov/fdsnws/event/1/#parameters
    latitude, longitude = re.split(r'\s*,\s*', geodata['loc'])
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
    query = {
        'format': 'geojson',
        'starttime': local_8601_start_time,
        'endtime': local_8601_end_time,
        'latitude': latitude,
        'longitude': longitude,
        'limit': limit,
        'maxradiuskm': util.miles_to_kilometers(miles=radius) if unit == 'm' else radius,
        'minmagnitude': magnitude,
        'offset': 1,
        'orderby': 'time',
    }
    _, data, _ = request.swiftbar_request(url=url, query=query, return_type='json')
    return ', '.join(location) if len(location) >= 3 else None, data, None

def main() -> None:
    os.environ['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin'
    plugin = Plugin()
    defaults_dict = {
        'VAR_EARTHQUAKES_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_EARTHQUAKES_LIMIT': {
            'default_value': 30,
            'minmax': namedtuple('minmax', ['min', 'max'])(5, 50),
        },
        'VAR_EARTHQUAKES_MIN_MAGNITUDE': {
            'default_value': 0,
            'minmax': namedtuple('minmax', ['min', 'max'])(0, 20)
        },
        'VAR_EARTHQUAKES_RADIUS_MILES': {
            'default_value': 100,
            'minmax': namedtuple('minmax', ['min', 'max'])(10, 500)
        },
        'VAR_EARTHQUAKES_UNIT': {
            'default_value': 'm',
            'valid_values': ['km', 'm'],
        }
    }

    plugin.read_config(defaults_dict)
    args = configure()
    if args.debug:
        plugin.update_setting('VAR_EARTHQUAKES_DEBUG_ENABLED', True if plugin.configuration['VAR_EARTHQUAKES_DEBUG_ENABLED'] == False else False)
    elif args.limit:
        plugin.update_setting('VAR_EARTHQUAKES_LIMIT', args.limit)
    elif args.magnitude:
        plugin.update_setting('VAR_EARTHQUAKES_MIN_MAGNITUDE', args.magnitude)
    elif args.radius:
        plugin.update_setting('VAR_EARTHQUAKES_RADIUS_MILES', args.radius)
    elif args.unit:
        plugin.update_setting('VAR_EARTHQUAKES_UNIT', args.unit)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_EARTHQUAKES_DEBUG_ENABLED']
    limit = plugin.configuration['VAR_EARTHQUAKES_LIMIT']
    magnitude = plugin.configuration['VAR_EARTHQUAKES_MIN_MAGNITUDE']
    radius = plugin.configuration['VAR_EARTHQUAKES_RADIUS_MILES']
    unit = plugin.configuration['VAR_EARTHQUAKES_UNIT']
    time_format = '%a, %B %-d, %Y %H:%M:%S'
    
    location, quake_data, err = get_quake_data(radius=radius, magnitude=magnitude, unit=unit, limit=limit)
    if quake_data:
        if 'features' in quake_data and type (quake_data['features']) == list:
            features = quake_data['features']
            plugin.print_menu_title(f'Earthquakes: {len(features)}')
            plugin.print_menu_separator()
            if location:
                plugin.print_menu_item(location)
                plugin.print_menu_separator()
            for feature in features:
                place = feature['properties']['place']
                
                if unit == 'm':
                    match = re.search(r'^(\d+) km', place)
                    if match:
                        km = int(match.group(1))
                    miles = util.kilometers_to_miles(kilometers=km)
                    place = place.replace(f'{km} km', f'{round(miles, 2)} m', 1)

                plugin.print_menu_item(place)
                quake_details = OrderedDict()
                plugin.print_menu_item(
                    f'--{feature["properties"]["url"]}',
                    color='blue',
                    href=feature['properties']['url']
                )
                quake_details['Magnitude'] = feature['properties']['mag']
                quake_details['Time'] = util.unix_to_human((int(feature['properties']['time'] / 1000)), format=time_format)
                quake_details['Updated'] = util.unix_to_human((int(feature['properties']['updated'] / 1000)), format=time_format)
                quake_details['Status'] = feature['properties']['status']
                plugin.print_ordered_dict(quake_details, justify='left', indent=2)
    elif err:
        plugin.print_menu_title('Earthquakes: Error')
        plugin.print_menu_separator()
        plugin.print_menu_item(err)
    plugin.print_menu_separator()
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} "Debugging" menu',
        cmd=[plugin.plugin_name, '--debug'],
        refresh=True,
        terminal=False,
    )
    plugin.print_menu_item(f'--Limit')
    for number in range(5, 55):
        if number % 5 == 0:
            color = 'blue' if number == limit else 'black'
            plugin.print_menu_item(
                f'----{number}',
                cmd=[plugin.plugin_name, '--limit', number],
                color=color,
                refresh=True,
                terminal=False,
            )
    plugin.print_menu_item('--Minimum Magnitude')
    for number in range(0, 22):
        if number % 2 == 0:
            color = 'blue' if number == magnitude else 'black'
            plugin.print_menu_item(
                f'----{number}',
                cmd=[plugin.plugin_name, '--magnitude', number],
                color=color,
                refresh=True,
                terminal=False,
            )
    plugin.print_menu_item(f'--Radius in {unit}')
    for number in range(1, 550):
        if number % 50 == 0:
            color = 'blue' if number == radius else 'black'
            plugin.print_menu_item(
                f'----{number}',
                cmd=[plugin.plugin_name, '--radius', number],
                color=color,
                refresh=True,
                terminal=False,
            )
    plugin.print_menu_item('--Unit')
    for valid_unit in ['km', 'm']:
        color = 'blue' if valid_unit == unit else 'black'
        plugin.print_menu_item(
            f'----{valid_unit}',
            cmd=[plugin.plugin_name, '--unit', valid_unit],
            color=color,
            refresh=True,
            terminal=False,
        )
    if debug_enabled:
            plugin.display_debugging_menu()
    plugin.print_menu_item('Refresh', refresh=True)
    
if __name__ == '__main__':
    main()
