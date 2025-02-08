#!/usr/bin/env python3

# <xbar.title>Earthquakes</xbar.title>
# <xbar.version>v0.3.4</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show information about earthquakes nearby</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-other-Earthquakes.15m.py</xbar.abouturl>
# <xbar.var>string(DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_EARTHQUAKES_LIMIT=20): The maximum number of quakes to display</xbar.var>
# <xbar.var>string(VAR_EARTHQUAKES_MIN_MAGNITUDE=0): The minimum magnitude for quakes</xbar.var>
# <xbar.var>string(VAR_EARTHQUAKES_RADIUS_MILES=50): Radius in miles</xbar.var>
# <xbar.var>string(VAR_EARTHQUAKES_RADIUS_UNIT=m): miles or kilometers</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[DEBUG_ENABLED=false, VAR_EARTHQUAKES_LIMIT=20, VAR_EARTHQUAKES_MIN_MAGNITUDE=0, VAR_EARTHQUAKES_RADIUS_MILES=50, VAR_EARTHQUAKES_RADIUS_UNIT=m]</swiftbar.environment>

from collections import namedtuple, OrderedDict
from swiftbar import images, request, util
from swiftbar.plugin import Plugin
from typing import Any, Dict
import datetime
import re
import time

def get_quake_data(radius: int=0, magnitude: int=0, unit: str='m', limit: int=0) -> Dict[str, Any]:
    geodata = util.geolocate_me()
    if not geodata:
        return None, {}, 'Failed to geolocate'
    
    location = [
        geodata.City,
        geodata.Region,
        geodata.Country,
        geodata.Postal,
    ]
    
    now = int(time.time())
    local_8601_start_time = datetime.datetime.fromtimestamp(now - 86400).isoformat('T', 'seconds')
    local_8601_end_time = datetime.datetime.fromtimestamp(now).isoformat('T', 'seconds')

    # https://earthquake.usgs.gov/fdsnws/event/1/#parameters
    # latitude, longitude = re.split(r'\s*,\s*', geodata['loc'])
    host = 'earthquake.usgs.gov'
    path = '/fdsnws/event/1/query'
    query = {
        'format': 'geojson',
        'starttime': local_8601_start_time,
        'endtime': local_8601_end_time,
        'latitude': geodata.Latitude,
        'longitude': geodata.Longitude,
        'limit': limit,
        'maxradiuskm': util.miles_to_kilometers(miles=radius) if unit == 'm' else radius,
        'minmagnitude': magnitude,
        'offset': 1,
        'orderby': 'time',
    }
    response, data, _ = request.swiftbar_request(host=host, path=path, query=query, return_type='json', encode_query=True)
    return ', '.join(location) if len(location) >= 3 else None, data, None

def main() -> None:
    plugin = Plugin()
    plugin.defaults_dict = OrderedDict()
    plugin.defaults_dict['DEBUG_ENABLED'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--debug',
            'title': 'the "Debugging" menu',
        },
    }
    plugin.defaults_dict['VAR_EARTHQUAKES_LIMIT'] = {
        'default_value': 30,
        'minmax': namedtuple('minmax', ['min', 'max'])(5, 50),
        'type': int,
        'setting_configuration': {
            'default': None,
            'flag': '--limit',
            'increment': 5,
            'title': 'Limit',
        },
    }
    plugin.defaults_dict['VAR_EARTHQUAKES_MIN_MAGNITUDE'] = {
        'default_value': 0,
        'minmax': namedtuple('minmax', ['min', 'max'])(0, 20),
        'type': int,
        'setting_configuration': {
            'default': None,
            'flag': '--magnitude',
            'increment': 2,
            'title': 'Minimum Magnitude',
        },
    }
    plugin.defaults_dict['VAR_EARTHQUAKES_RADIUS_MILES'] = {
        'default_value': 100,
        'minmax': namedtuple('minmax', ['min', 'max'])(10, 500),
        'type': int,
        'setting_configuration': {
            'default': None,
            'flag': '--radius',
            'increment': 50,
            'title': 'Radius',
        },
    }
    plugin.defaults_dict['VAR_EARTHQUAKES_UNIT'] = {
        'default_value': 'm',
        'valid_values': ['km', 'm'],
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--unit',
            'title': 'Unit',
        },
    }

    plugin.read_config()
    plugin.generate_args()
    plugin.update_json_from_args()

    time_format = '%a, %B %-d, %Y %H:%M:%S'
    location, quake_data, err = get_quake_data(
        radius=plugin.configuration['VAR_EARTHQUAKES_RADIUS_MILES'],
        magnitude=plugin.configuration['VAR_EARTHQUAKES_MIN_MAGNITUDE'],
        unit=plugin.configuration['VAR_EARTHQUAKES_UNIT'],
        limit=plugin.configuration['VAR_EARTHQUAKES_LIMIT']
    )
    if quake_data:
        if 'features' in quake_data and type (quake_data['features']) == list:
            features = quake_data['features']
            plugin.print_menu_title(f'Earthquakes: {len(features)}')
            if location:
                plugin.print_menu_item(location)
                plugin.print_menu_separator()
            for feature in features:
                place = feature['properties']['place']
                
                if plugin.configuration['VAR_EARTHQUAKES_UNIT'] == 'm':
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
        plugin.print_menu_item(err)
    plugin.render_footer()
    
if __name__ == '__main__':
    main()
