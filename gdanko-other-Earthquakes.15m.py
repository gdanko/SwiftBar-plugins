#!/usr/bin/env python3

# <xbar.title>Earthquakes</xbar.title>
# <xbar.version>v0.3.4</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show information about earthquakes nearby</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-other-Earthquakes.15m.py</xbar.abouturl>
# <xbar.var>string(LIMIT=20): The maximum number of quakes to display</xbar.var>
# <xbar.var>string(MINIMUM_MAGNITUDE=0): The minimum magnitude for quakes</xbar.var>
# <xbar.var>string(MAXIMUM_RADIUS=50): Radius in miles</xbar.var>
# <xbar.var>string(RADIUS_UNIT=m): miles or kilometers</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[LIMIT=20, MINIMUM_MAGNITUDE=0, MAXIMUM_RADIUS=50, RADIUS_UNIT=m]</swiftbar.environment>

from collections import namedtuple, OrderedDict
from swiftbar import request, util
from swiftbar.plugin import Plugin
from typing import Any, Dict, Tuple, Union
import datetime
import re
import time

def get_quake_data(radius: int=0, magnitude: int=0, unit: str='m', limit: int=0) -> Tuple[Union[str, None], Dict[str, Any], Union[str, None]]:
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
    _, data, _ = request.swiftbar_request(host=host, path=path, query=query, return_type='json', encode_query=True)
    return ', '.join(location) if len(location) >= 3 else None, data, None

def main() -> None:
    plugin = Plugin()
    plugin.defaults_dict['LIMIT'] = {
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
    plugin.defaults_dict['MINIMUM_MAGNITUDE'] = {
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
    plugin.defaults_dict['MAXIMUM_RADIUS'] = {
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
    plugin.defaults_dict['UNIT'] = {
        'default_value': 'm',
        'valid_values': ['km', 'm'],
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--unit',
            'title': 'Unit',
        },
    }
    plugin.setup()

    time_format = '%a, %B %-d, %Y %H:%M:%S'
    location, quake_data, err = get_quake_data(
        radius=plugin.configuration['MAXIMUM_RADIUS'],
        magnitude=plugin.configuration['MINIMUM_MAGNITUDE'],
        unit=plugin.configuration['UNIT'],
        limit=plugin.configuration['LIMIT']
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
                
                if plugin.configuration['UNIT'] == 'm':
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
