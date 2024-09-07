#!/usr/bin/env python3

# <xbar.title>Weather OpenWeatherMap</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the weather using openweathermap.org</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/Weather/gdanko-weather-WeatherOWM.30m.py</xbar.abouturl>
# <xbar.var>string(VAR_WEATHER_OWM_LOCATION="San Diego, CA, US"): The location to use</xbar.var>
# <xbar.var>string(VAR_WEATHER_OWM_API_KEY=""): The OpenWeatherMap API key</xbar.var>
# <xbar.var>string(VAR_WEATHER_OWM_UNITS="F"): The unit to use: (C)elsius or (F)ahrenheit</xbar.var>

import datetime
import json
import os
import subprocess
import sys
import time

try:
    import requests
except ModuleNotFoundError:
    print('Error: missing "requests" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install requests')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def get_defaults():
    location = os.getenv('VAR_WEATHER_OWM_LOCATION', 'San Diego, CA, US')
    api_key = os.getenv('VAR_WEATHER_OWM_API_KEY', '')
    valid_units = ['C', 'F']
    units = os.getenv('VAR_WEATHER_OWM_UNITS', 'F')
    if not units in valid_units:
        units = 'F'
    return location, api_key, units

def fetch_data(url=None):
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

                print(f'{location} {round(weather_data["main"]["temp"])}°{units}')
                print('---')
                print(f'Updated {get_timestamp(int(time.time()))}')
                print('---')
                print(f'Low/High: {round(weather_data["main"]["temp_min"])}°{units} / {round(weather_data["main"]["temp_max"])}°{units}')
                print(f'Feels Like: {round(weather_data["main"]["feels_like"])}°{units}')
                print(f'Humidity: {round(weather_data["main"]["humidity"])}%')
                print(f'Condition: {weather_data["weather"][0]["description"].title()}')
                print(f'Wind: {weather_data["wind"]["deg"]}° @ {round(weather_data["wind"]["speed"])} {units_map[units]["speed"]}')
                print('Refresh weather data | refresh=true')
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
                #     print(f'{location} {round(weather_data["main"]["temp"])}°{units}')
                #     print('---')
                #     print(f'Low/High: {round(weather_data["main"]["temp_min"])}°{units} / {round(weather_data["main"]["temp_max"])}°{units}')
                #     print(f'Feels Like: {round(weather_data["main"]["feels_like"])}°{units}')
                #     print(f'Humidity: {round(weather_data["main"]["humidity"])}%')
                #     print(f'Condition: {weather_data["weather"][0]["description"].title()}')
                #     print(f'Wind: {weather_data["wind"]["deg"]}° @ {round(weather_data["wind"]["speed"])} {units_map[units]["speed"]}')



if __name__ == '__main__':
    main()
