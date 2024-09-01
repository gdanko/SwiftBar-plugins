#!/usr/bin/env python3

# <xbar.title>Weather OpenWeatherMap</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the weather using openweathermap.org]</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/Weather/gdanko-weather-WeatherOWM.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_WEATHER_OWM_LOCATION="San Diego, CA, US"): The location to use</xbar.var>
# <xbar.var>string(VAR_WEATHER_OWM_API_KEY=""): The OpenWeatherMap API key</xbar.var>
# <xbar.var>string(VAR_WEATHER_OWM_UNITS="F"): The unit to use: (C)elsius or (F)ahrenheit</xbar.var>

import json
import os
import time
from pprint import pprint

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_defaults():
    location = os.getenv('VAR_WEATHER_OWM_LOCATION', 'San Diego, CA, US')
    api_key = os.getenv('VAR_WEATHER_OWM_API_KEY', '')
    valid_units = ['C', 'F']
    units = os.getenv('VAR_WEATHER_OWM_UNITS', 'F')
    if not units in valid_units:
        units = 'F'
    return location, api_key, units

def fetch_data(url=None):
    import requests

    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            return data, None
        except Exception as e:
            return None, e
    else:
        try:
            error_data = json.loads(response.content)
            error_message = error_data['message']
        except:
            error_message = 'no further detail'    
        return None, f'Non-200 status code {response.status_code}: {error_message}'

def main():
    try:
        import requests

        location, api_key, units = get_defaults()

        units_map = {
            'C': {
                'unit': 'metric',
                'speed': 'kmh',
            },
            'F': {
                'unit': 'imperial',
                'speed': 'mph',
            }
        }

        if api_key == '':
            print('Failed to fetch the weather')
            print('---')
            print('Missing API key')
        else:
            url = f'http://api.openweathermap.org/geo/1.0/direct?q={location}&appid={api_key}'
            location_data, err = fetch_data(url)
            if err:
                print('Failed to fetch the weather')
                print('---')
                print(f'Failed to fetch location data: {err}')
            else:
                lat = location_data[0]['lat']
                lon = location_data[0]['lon']
                url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units_map[units]["unit"]}'
                
                weather_data, err = fetch_data(url=url)
                if err:
                    print('Failed to fetch the weather')
                    print('---')
                    print(f'Failed to fetch weather data: {err}')
                else:
                    print(f'{location} {pad_float(weather_data["main"]["temp"])}°{units}')
                    print('---')
                    print(f'Low/High: {pad_float(weather_data["main"]["temp_min"])}°{units} / {pad_float(weather_data["main"]["temp_max"])}°{units}')
                    print(f'Feels Like: {pad_float(weather_data["main"]["feels_like"])}°{units}')
                    print(f'Humidity: {pad_float(weather_data["main"]["humidity"])}%')
                    print(f'Condition: {weather_data["weather"][0]["description"].title()}')
                    print(f'Wind: {weather_data["wind"]["deg"]}° @ {pad_float(weather_data["wind"]["speed"])} {units_map[units]["speed"]}')
                    # Forecast requires subscription???
                    # cnt = 4
                    # url = f'https://api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt={cnt}&appid={api_key}&units={units_map[units]["unit"]}'
                    # forecast_data, err = fetch_data(url=url)
                    # if err:
                    #     print('Failed to fetch the weather')
                    #     print('---')
                    #     print(f'Failed to fetch forecast data: {err}')
                    # else:
                    #     print('---')
                    #     print(f'{location} {pad_float(weather_data["main"]["temp"])}°{units}')
                    #     print('---')
                    #     print(f'Low/High: {pad_float(weather_data["main"]["temp_min"])}°{units} / {pad_float(weather_data["main"]["temp_max"])}°{units}')
                    #     print(f'Feels Like: {pad_float(weather_data["main"]["feels_like"])}°{units}')
                    #     print(f'Humidity: {pad_float(weather_data["main"]["humidity"])}%')
                    #     print(f'Condition: {weather_data["weather"][0]["description"].title()}')
                    #     print(f'Wind: {weather_data["wind"]["deg"]}° @ {pad_float(weather_data["wind"]["speed"])} {units_map[units]["speed"]}')

    except ModuleNotFoundError:
        print('Error: missing "requests" library.')
        print('---')
        import sys
        import subprocess
        subprocess.run('pbcopy', universal_newlines=True,
                       input=f'{sys.executable} -m pip install requests')
        print('Fix copied to clipboard. Paste on terminal and run.')

if __name__ == '__main__':
    main()
