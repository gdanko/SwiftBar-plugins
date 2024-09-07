#!/usr/bin/env python3

# <xbar.title>Weather Wttr</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display the weather using wttr.in</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/Weather/gdanko-weather-WeatherWttr.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_WEATHER_WTTR_LOCATION="San Diego, CA, US"): The location to use</xbar.var>

import os
import sys
import subprocess

try:
    import requests
except ModuleNotFoundError:
    print('Error: missing "requests" library.')
    print('---')
    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install requests')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def get_defaults():
    location = os.getenv('VAR_WEATHER_OWM_LOCATION', 'San Diego, CA, US')
    return location

def main():
    location = get_defaults()

    url = f'https://wttr.in/{location}?format=%l %t'
    response = requests.get(url)
    if response.content != '':
        print(response.content.decode('utf-8').replace('"', ''))
    else:
        print('Failed to fetch the weather')
        print('---')
        print(f'{url} | href={url.replace(" ", "%20")} | color=blue')

if __name__ == '__main__':
    main()
