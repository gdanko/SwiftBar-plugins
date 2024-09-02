#!/usr/bin/env python3

# <xbar.title>Weather WeatherAPI</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the weather using weatherapi.com</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/Weather/gdanko-weather-WeatherWAPI.10m.py</xbar.abouturl>
# <xbar.var>string(VAR_WEATHER_WAPI_LOCATION="San Diego, CA, US"): The location to use</xbar.var>
# <xbar.var>string(VAR_WEATHER_WAPI_API_KEY=""): The OpenWeatherMap API key</xbar.var>
# <xbar.var>string(VAR_WEATHER_WAPI_UNITS="F"): The unit to use: (C)elsius or (F)ahrenheit</xbar.var>

import json
import os
import time
from pprint import pprint

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_defaults():
    location = os.getenv('VAR_WEATHER_WAPI_LOCATION', 'San Diego, CA, US')
    api_key = os.getenv('VAR_WEATHER_WAPI_API_KEY', '')
    valid_units = ['C', 'F']
    units = os.getenv('VAR_WEATHER_WAPI_UNITS', 'F')
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

def get_uv_index(uv_index):
    uv_index = float(uv_index)
    if uv_index > 0 and uv_index < 6:
        return 'Moderate'
    elif uv_index >= 6 and uv_index < 8:
        return 'High'
    elif uv_index >= 8 and uv_index < 11:
        return 'Very High'
    elif uv_index > 11:
        return 'Extreme'

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
            url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=yes'
            weather_data, err = fetch_data(url)
            if err:
                print('Failed to fetch the weather')
                print('---')
                print(f'Failed to fetch weather data: {err}')
            else:
                forecast_days = 8
                url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={forecast_days}&aqi=yes&alerts=yes'
                forecast_data, err = fetch_data(url=url)
                if err:
                    print('Failed to fetch the weather')
                    print('---')
                    print(f'Failed to fetch forecast data: {err}')
                else:
                    forecast = forecast_data['forecast']['forecastday']
                    today = forecast[0]

                    low_temp = today["day"]["mintemp_f"] if units == 'F' else today["day"]["mintemp_c"]
                    high_temp = today["day"]["maxtemp_f"] if units == 'F' else today["day"]["maxtemp_c"]
                    current_temp = weather_data["current"]["temp_f"] if units == 'F' else weather_data["current"]["temp_c"]
                    feels_like = weather_data["current"]["feelslike_f"] if units == 'F' else weather_data["current"]["feelslike_c"]
                    precipitation = f'{pad_float(weather_data["current"]["precip_in"])} in' if units == 'F' else f'{pad_float(weather_data["current"]["precip_in"])} mm'
                    visibility = f'{float(weather_data["current"]["vis_miles"])} miles' if units == 'F' else f'{float(weather_data["current"]["vis_km"])} km'
                    wind_speed = f'{pad_float(weather_data["current"]["wind_mph"])} mph' if units == 'F' else f'{pad_float(weather_data["current"]["wind_kph"])} kph'
                    wind_chill = weather_data["current"]["windchill_f"] if units == 'F' else weather_data["current"]["windchill_c"]
                    heat_index = weather_data["current"]["heatindex_f"] if units == 'F' else weather_data["current"]["heatindex_c"]
                    dew_point = weather_data["current"]["dewpoint_f"] if units == 'F' else weather_data["current"]["dewpoint_c"]
                    pressure = f'{pad_float(weather_data["current"]["pressure_in"])} in' if units == 'F' else f'{pad_float(weather_data["current"]["pressure_mb"])} mb'
                    print(f'{location} {pad_float(current_temp)}°{units}')
                    print('---')
                    print('Current Weather')
                    print(f'--Low / High: {pad_float(low_temp)}°{units} / {pad_float(high_temp)}°{units}')
                    print(f'--Feels Like: {pad_float(feels_like)}°{units}')
                    print(f'--Pressure: {pressure}')
                    print(f'--Visibility: {visibility}')
                    print(f'--Condition: {weather_data["current"]["condition"]["text"].title()}')
                    print(f'--Dew Point: {pad_float(dew_point)}°{units}')
                    print(f'--Humidity: {pad_float(weather_data["current"]["humidity"])}%')
                    print(f'--Precipitation: {precipitation}')
                    print(f'--Wind: {weather_data["current"]["wind_dir"]} {wind_speed}')
                    print(f'--Wind Chill: {pad_float(wind_chill)}°{units}')
                    print(f'--Heat Index: {pad_float(heat_index)}°{units}')
                    print(f'--UV Index: {get_uv_index(weather_data["current"]["uv"])} - {weather_data["current"]["uv"]}')
                    print(f'--Sunrise: {today["astro"]["sunrise"]}')
                    print(f'--Sunset: {today["astro"]["sunset"]}')
                    print(f'--Moonrise: {today["astro"]["moonrise"]}')
                    print(f'--Moonset: {today["astro"]["moonset"]}')
                    print(f'--Moon Phase: {today["astro"]["moon_phase"]}')
                    print(f'{len(forecast) - 1} Day Forecast')
                    for i in range(1, len(forecast)):
                        daily = forecast[i]
                        daily_low = daily["day"]["mintemp_f"] if units == 'F' else daily["day"]["mintemp_c"]
                        daily_high = daily["day"]["maxtemp_f"] if units == 'F' else daily["day"]["maxtemp_c"]
                        daily_average = daily["day"]["avgtemp_f"] if units == 'F' else daily["day"]["avgtemp_c"]
                        daily_will_it_rain = "Yes" if daily["day"]["daily_will_it_rain"] == 1 else "No"
                        daily_will_it_snow = "Yes" if daily["day"]["daily_will_it_snow"] == 1 else "No"
                        total_precipitation = f'{pad_float(daily["day"]["totalprecip_in"])} in' if units == 'F' else f'{pad_float(daily["day"]["totalprecip_mm"])} mm'
                        avg_visibility = f'{float(daily["day"]["avgvis_miles"])} miles' if units == 'F' else f'{float(daily["day"]["avgvis_km"])} km'
                        print(f'--{daily["date"]}')
                        print(f'----Low / High: {pad_float(daily_low)}°{units} / {pad_float(daily_high)}°{units}')
                        print(f'----Average Temperature: {pad_float(daily_average)}°{units}')
                        print(f'----Average Visibility: {avg_visibility}')
                        print(f'----Condition: {daily["day"]["condition"]["text"].title()}')
                        print(f'----Average Humidity: {pad_float(daily["day"]["avghumidity"])}%')
                        print(f'----Total Precipitation: {total_precipitation}')
                        print(f'----Rain: {daily_will_it_rain}')
                        if daily_will_it_rain == 'Yes':
                            print(f'----Chance of Rain: {daily["day"]["daily_chance_of_rain"]}%')
                        print(f'----Snow: {daily_will_it_snow}')
                        if daily_will_it_snow == 'Yes':
                            print(f'----Chance of Snow: {daily["day"]["daily_chance_of_snow"]}%')                        
                        print(f'----UV Index: {get_uv_index(daily["day"]["uv"])} - {daily["day"]["uv"]}')
                        print(f'----Sunrise: {daily["astro"]["sunrise"]}')
                        print(f'----Sunset: {daily["astro"]["sunset"]}')
                        print(f'----Moonrise: {daily["astro"]["moonrise"]}')
                        print(f'----Moonset: {daily["astro"]["moonset"]}')
                        print(f'----Moon Phase: {daily["astro"]["moon_phase"]}')

                    print('Refresh weather data | refresh=true')

    except ModuleNotFoundError:
        print('Error: missing "requests" library.')
        print('---')
        import sys
        import subprocess
        subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install requests')
        print('Fix copied to clipboard. Paste on terminal and run.')

if __name__ == '__main__':
    main()
