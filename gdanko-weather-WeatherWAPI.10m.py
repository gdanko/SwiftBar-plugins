#!/usr/bin/env python3

# <xbar.title>Weather WeatherAPI</xbar.title>
# <xbar.version>v0.5.2</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the weather using weatherapi.com</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-weather-WeatherWAPI.10m.py</xbar.abouturl>
# <xbar.var>string(API_KEY=): The OpenWeatherMap API key</xbar.var>
# <xbar.var>string(LOCATION="Los Angeles, CA, US"): The location to use</xbar.var>
# <xbar.var>string(SHOW_FORECAST=true): Show the forecast in the drop down menut</xbar.var>
# <xbar.var>string(UNITS=F): The unit to use: (C)elsius or (F)ahrenheit</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[API_KEY=, LOCATION="Los Angeles, CA, US", SHOW_FORECAST=true, UNITS=F]</swiftbar.environment>

from collections import OrderedDict
from swiftbar.plugin import Plugin
from swiftbar import request, util
from typing import Dict
import re

def get_uv_index(uv_index: float=0.0) -> str:
    uv_index = float(uv_index)
    if uv_index > 0 and uv_index < 6:
        return 'Moderate'
    elif uv_index >= 6 and uv_index < 8:
        return 'High'
    elif uv_index >= 8 and uv_index < 11:
        return 'Very High'
    elif uv_index > 11:
        return 'Extreme'

def process_description(desc: str=None) -> Dict[str, str]:
    output = {}
    entries = desc.split("\n\n")
    for x, item in enumerate(entries):
        entries[x] = entries[x].replace("\n", " ")

    for item in entries:
        pattern = re.compile(r"^\* ([A-Za-z\s]+)\.\.\.(.*)$")
        match = re.search(pattern, item)
        if match:
            output[match.group(1).title()] = match.group(2)
    return output

def pluralize(count: int=0, word: str=None) -> str:
    if count == 1:
        return word
    return f'{word}s'

def main() -> None:
    plugin = Plugin()
    plugin.defaults_dict['LOCATION'] = {
        'default_value': None,
        'type': str,
    }
    plugin.defaults_dict['API_KEY'] = {
        'default_value': None,
        'type': str,
    }
    plugin.defaults_dict['SHOW_FORECAST'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--forecast',
            'title': 'the "Forecast" menu',
        },
    }
    plugin.defaults_dict['UNIT'] = {
        'default_value': 'F',
        'valid_values': util.valid_weather_units(),
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--unit',
            'title': 'Unit',
        },
    }
    plugin.setup()

    location = None
    if plugin.configuration['LOCATION']:
        location = plugin.configuration['LOCATION']
    else:
        geodata = util.geolocate_me()
        if geodata:
            location = f'{geodata.City}, {geodata.Region}, {geodata.Country}'
        else:
            location = 'Los Angeles, California, US'

    alert_format = '%a, %B %-d, %Y %H:%M:%S'
    forecast_format = '%a, %B %-d, %Y'
    if plugin.configuration['API_KEY'] == '':
        plugin.error_messages.append('Missing API key')
    else:
        response, weather_data, err = request.swiftbar_request(
            host='api.weatherapi.com',
            path='/v1/current.json',
            query={'key': plugin.configuration['API_KEY'], 'q': location, 'aqi': 'yes'},
            return_type = 'json',
            encode_query=True,
        )
        if response.status != 200:
            error_message = f'A non-200 {response.status} response code was received'
            if weather_data:
                if 'error' in weather_data and 'message' in weather_data['error']:
                    error_message = weather_data['error']['message']
            plugin.error_messages.append(f'Failed to fetch weather data: {error_message}')

        response, forecast_data, err = request.swiftbar_request(
            host='api.weatherapi.com',
            path='/v1/forecast.json',
            query={'key': plugin.configuration['API_KEY'], 'q': location, 'days': 8, 'aqi': 'yes', 'alerts': 'yes'},
            return_type = 'json',
            encode_query=True,
        )
        if response.status != 200:
            error_message = f'A non-200 {response.status} response code was received'
            if forecast_data:
                if 'error' in forecast_data and 'message' in forecast_data['error']:
                    error_message = forecast_data['error']['message']
            plugin.error_messages.append(f'Failed to fetch forecast data: {error_message}')

    if len(plugin.error_messages) == 0:
        forecast = forecast_data['forecast']['forecastday']
        today = forecast[0]

        # low_temp = today["day"]["mintemp_f"] if unit == 'F' else today["day"]["mintemp_c"]
        # high_temp = today["day"]["maxtemp_f"] if unit == 'F' else today["day"]["maxtemp_c"]
        current_temp = weather_data["current"]["temp_f"] if plugin.configuration['UNIT'] == 'F' else weather_data["current"]["temp_c"]
        feels_like = weather_data["current"]["feelslike_f"] if plugin.configuration['UNIT'] == 'F' else weather_data["current"]["feelslike_c"]
        precipitation = f'{round(weather_data["current"]["precip_in"])} in' if plugin.configuration['UNIT'] == 'F' else f'{round(weather_data["current"]["precip_in"])} mm'
        visibility = f'{float(weather_data["current"]["vis_miles"])} miles' if plugin.configuration['UNIT'] == 'F' else f'{float(weather_data["current"]["vis_km"])} km'
        wind_speed = f'{round(weather_data["current"]["wind_mph"])} mph' if plugin.configuration['UNIT'] == 'F' else f'{round(weather_data["current"]["wind_kph"])} kph'
        wind_chill = weather_data["current"]["windchill_f"] if plugin.configuration['UNIT'] == 'F' else weather_data["current"]["windchill_c"]
        heat_index = weather_data["current"]["heatindex_f"] if plugin.configuration['UNIT'] == 'F' else weather_data["current"]["heatindex_c"]
        dew_point = weather_data["current"]["dewpoint_f"] if plugin.configuration['UNIT'] == 'F' else weather_data["current"]["dewpoint_c"]
        pressure = f'{round(weather_data["current"]["pressure_in"])} in' if plugin.configuration['UNIT'] == 'F' else f'{round(weather_data["current"]["pressure_mb"])} mb'

        plugin.print_menu_title(f'{location} {round(current_temp)}°{plugin.configuration["UNIT"]}')
        current = OrderedDict()
        # current['Low / High'] = f'{round(low_temp)}°{unit} / {round(high_temp)}°{unit}'
        current['Feels Like'] = f'{round(feels_like)}°{plugin.configuration["UNIT"]}'
        current['Pressure'] = pressure
        current['Visibility'] = visibility
        current['Condition'] = f'{weather_data["current"]["condition"]["text"].title()}'
        current['Dew Point'] = f'{round(dew_point)}°{plugin.configuration["UNIT"]}'
        current['Humidity'] = f'{round(weather_data["current"]["humidity"])}%'
        current['Precipitation'] = precipitation
        current['Wind'] = f'{weather_data["current"]["wind_dir"]} {wind_speed}'
        current['Wind Chill'] = f'{round(wind_chill)}°{plugin.configuration["UNIT"]}'
        current['Heat Index'] = f'{round(heat_index)}°{plugin.configuration["UNIT"]}'
        current['UV Index'] = f'{get_uv_index(weather_data["current"]["uv"])} - {weather_data["current"]["uv"]}'
        # current['Sunrise'] = f'{today["astro"]["sunrise"]}'
        # current['Sunset'] = f'{today["astro"]["sunset"]}'
        # current['Moonrise'] = f'{today["astro"]["moonrise"]}'
        # current['Moonset'] = f'{today["astro"]["moonset"]}'
        # current['Moon Phase'] = f'{today["astro"]["moon_phase"]}'
        plugin.print_ordered_dict(current, justify='left')

        if 'alerts' in forecast_data:
            if 'alert' in forecast_data['alerts']:
                if len(forecast_data['alerts']['alert']) > 0:
                    alerts = forecast_data['alerts']['alert']
                    plugin.print_menu_item(f'{len(alerts)} {pluralize(len(alerts), "Alert")}')
                    for alert in alerts:
                        desc = process_description(alert['desc'])
                        plugin.print_menu_item(f'--{alert["event"]}')
                        alert = OrderedDict()
                        alert['Category'] = alert['category']
                        alert['Effective'] = util.prettify_timestamp(alert['effective'], alert_format)
                        alert['Expires'] = util.prettify_timestamp(alert['expires'], alert_format)
                        for k, v in desc.items():
                            alert[k] = v
                        plugin.print_ordered_dict(alert, justify='left')
        
        if plugin.configuration['SHOW_FORECAST']:
            plugin.print_menu_item(f'{len(forecast)} Day Forecast')
            for daily in forecast:
                daily_low = daily['day']['mintemp_f'] if plugin.configuration["UNIT"] == 'F' else daily['day']['mintemp_c']
                daily_high = daily['day']['maxtemp_f'] if plugin.configuration["UNIT"] == 'F' else daily['day']['maxtemp_c']
                daily_average = daily['day']['avgtemp_f'] if plugin.configuration["UNIT"] == 'F' else daily['day']['avgtemp_c']
                daily_will_it_rain = 'Yes' if daily['day']['daily_will_it_rain'] == 1 else 'No'
                daily_will_it_snow = 'Yes' if daily['day']['daily_will_it_snow'] == 1 else 'No'
                total_precipitation = f'{round(daily["day"]["totalprecip_in"])} in' if plugin.configuration["UNIT"] == 'F' else f'{round(daily["day"]["totalprecip_mm"])} mm'
                avg_visibility = f'{float(daily["day"]["avgvis_miles"])} miles' if plugin.configuration["UNIT"] == 'F' else f'{float(daily["day"]["avgvis_km"])} km'

                plugin.print_menu_item(f'--{util.prettify_timestamp(daily["date"], forecast_format)}')
                daily_section = OrderedDict()
                daily_section['Low / High'] = f'{round(daily_low)}°{plugin.configuration["UNIT"]} / {round(daily_high)}°{plugin.configuration["UNIT"]}'
                daily_section['Average Temperature'] = f'{round(daily_average)}°{plugin.configuration["UNIT"]}'
                daily_section['Average Visibility'] = avg_visibility
                daily_section['Condition'] = f'{daily["day"]["condition"]["text"].title()}'
                daily_section['Average Humidity'] = f'{round(daily["day"]["avghumidity"])}%'
                daily_section['Total Precipitation'] = total_precipitation
                daily_section['Rain'] = daily_will_it_rain
                if daily_will_it_rain == 'Yes':
                    daily_section['Chance of Rain'] = f'{daily["day"]["daily_chance_of_rain"]}%'
                if daily_will_it_snow == 'Yes':
                    daily_section['Chance of Snow'] = f'{daily["day"]["daily_chance_of_snow"]}%'
                daily_section['UV Index'] = f'{get_uv_index(daily["day"]["uv"])} - {daily["day"]["uv"]}'
                daily_section['Sunrise'] = daily['astro']['sunrise']
                daily_section['Sunset'] = daily['astro']['sunset']
                daily_section['Moonrise'] = daily['astro']['moonrise']
                daily_section['Moonset'] = daily['astro']['moonset']
                daily_section['Moon Phase'] = daily['astro']['moon_phase']
                plugin.print_ordered_dict(daily_section, justify='left', indent=4)
    else:
        plugin.print_menu_title('Failed to fetch the weather')
        for error_message in plugin.error_messages:
            plugin.print_menu_item(error_message)
    plugin.render_footer()

if __name__ == '__main__':
    main()
