# SwiftBar-plugins
A collection of plugins for [SwiftBar](https://github.com/swiftbar/SwiftBar) (also compatible with [xbar](https://github.com/matryer/xbar)).

## Prerequisites
1. Either [SwiftBar](https://github.com/swiftbar/SwiftBar) or [xbar](https://github.com/matryer/xbar)
2. Python >= 3.11

## Installation
1. Clone this repository
```
git clone https://github.com/gdanko/xbar-plugins.git
```
2. Symlink the desired plugins to your [plugins folder](https://github.com/swiftbar/SwiftBar#plugin-folder) for SwiftBar or `~/Library/Application Support/xbar/plugins` for xbar
```
ln -s /path/to/repo/plugin_name.py $PLUGINS_PATH/plugin_name.py
```

## Issues
<!-- SwiftBar doesn't know what to do with xbar's `<plugin_name>.vars.json` files. With xbar, both the plugin file and its associated JSON vars file both live in `~/Library/Application Support/xbar/plugins`. SwiftBar doesn't like this. It tries unsuccessfully to execute the JSON files as scripts. To get around this, we determine who the name of the calling process, which will be one of `/Applications/xbar.app/Contents/MacOS/xbar` or `/Applications/SwiftBar.app/Contents/MacOS/SwiftBar`. If the caller is xbar, we set the config path to `~/Library/Application Support/xbar/plugins`. If the caller is SwiftBar, we set the config path to `~/.config/SwiftBar`.

When a plugin is executed, it attempts to look for a `.vars.json` file to set its values. If one doesn't exist, it will use the default values specified in the plugin's code. This logic applies to both xbar and SwiftBar. This solution allows you to use a traditional xbar `.vars.json` with SwiftBar. The only caveat to this approach is that when you select the `Run in Terminal` option, the default values are used because of the way the plugin is being invoked. I am looking for a solution to this problem. -->
SwiftBar is a more modern implementation of xbar and it's implied that xbar plugins will just work. This is mostly true. I wanted to create a plugin class that would work with both applications, but I ran into a few issues.
1. There are some parameters that are unique to each application
    * SwiftBar
        * md
        * sfcolor
        * sfconfig
        * sfimage
        * sfsize
        * shortcut
        * tooltip
        * webview
        * webviewh
        * webvieww
    * xbar
        * disabled
        * key
        * shell

   I wanted to create a `typing.NamedTuple` class that would accommodate all of these, but if my plugin sent the `sfimage`, xbar would complain and the plugin's output would never be rendered. To work around this, I wrote a custom `TypedDict` class which does a few things:
    * It has 3 subclasses, `Params`, `ParamsXbar`, and `ParamsSwiftBar`. Anytime a plugin method that writes output is called, the `params` dictionary is sanitized. If the invoking application is SwiftBar, an instance of `ParamsSwiftBar` is created and all of the entries from the `Params` instance are inserted into the new `ParamsSwiftBar` object. To avoid any issues, we trap `KeyError` exceptions and just pass on them. The `TypeDict` class also has two options, `enforce_schema` and `enforce_typing`. When you create an instance of `TypedDict`, you pass it a schema in the form of a dict, it looks something like this:
    ```
    {
        'key1': int,
        'key2': bool,
        'key3': str,
        'key4': float,
    }
    ```

    If you create an instance of `Params` and try someting like `params['key'] = 'asdf'`, a `TypeError` exception will be thrown because `key1` is typed as an int. If you try something like `params['foo'] = 'bar'`, a `KeyError` exception will be thrown because `foo` is not a part of the schema. Disabling enforcement will allow these situations.
2. xbar stores its plugins in `~/Library/Application Support/xbar/plugins`. It also stores the JSON vars files in there. If your plugin's name is `my-great-plugin.15m.py` then any custom variables will live in a file named `my-great-plugin.15m.py.vars.json`. If you try something like this with SwiftBar, SwiftBar will try to execute the JSON files as plugins, and while you can add dot files to exclude these JSON files, I've come up with what I think is a more elegant cross-platform solution. If you're using SwiftBar, the plugin framework will create a directory for the JSON files in `~/.config/SwiftBar`. When a the `Plugin` class is instantiated, the `plugin._get_config_dir()` method is called and it does the following:
    * Determine the parent pid and use that to set the variable `plugin.invoked_by`.
    * Set the `plugin.config_dir` variable based on the value of `plugin.invoked_by`.
    * After `plugin._get_config_dir()` has completed, `plugin._create_config_dir()` is called to create the configuration directory if it doesn't exist. This should only ever happen with SwiftBar.

This combination of tweaks and workarounds allows both xbar and SwiftBar to execute plugins happily.

## Features
* Auto-detect whether or not you are using xbar or SwiftBar and configure the plugin path and configuration path accordingly.
* Automatically generate a plugin configration file using default values for every plugin that can use one. Its location is based on `plugin.config_dir` and `plugin.plugin_name`. For example, if you're using SwiftBar and your plugin name is `fancy-plugin-DoSomething.10s.py` then your plugin configuration file's path will be `~/.config/SwiftBar/fancy-plugin-DoSomething.10s.py.vars.json`.
* Most plugins have a `Settings` menu that can modify MOST of the settings. Obviously, things like API keys need to be manually configured by hand editing the JSON.
* Most plugins have a debugging menu that can be toggled via the plugin's `Settings` menu which shows the following:
    * OS version, e.g., `macOS 15.2 (Sequoia)`
    * Installed system memory
    * Python binary path
    * Python version
    * Plugins directory
    * Plugin path
    * Invoker (xbar or SwiftBar)
    * Invoker (full path)
    * Invoker pid
    * SwiftBar version (SwiftBar only)
    * Default font family
    * Default font size
    * Plugin configuration directory
    * Plugin JSON variables file path
    * Variables listed in `VAR_SOMETHING = value` format
    * Environment variables listed in `VAR_SOMETHING = value` format

## Plugins
* [Finance](#finance)
* [Network](#network)
* [System](#system)
* [Weather](#weather)
* [Other](#other)

### Finance
* `gdanko-finance-StockIndexes.15m.py`
    * Features
        * Show the last change for the Dow, Nasdaq, and S&P500 indices.
* `gdanko-finance-StockQuotes.15m.py`
    * Features
        * Show lots and lots of detail about one or more stock symbols.
    * Settings
        * Toggle the `Debugging` menu

### Network
* `gdanko-network-NetworkThroughput.2s.py`
    * Features
        * Display the TX/RX rate for the specified interface.
        * Display interface flags, hardware address, IPV4 address, IPV6 address, and public IP address (if applicable).
    * Settings
        * Toggle the `Debugging` menu
        * Toggle verbose mode, which shows information about errors and dropped packets
        * Select the interface to view
* `gdanko-network-WifiSignal.30s.py`
    * Features
        * Display the specified interface's connection strength to its configured SSID.
        * Display device name, channel number, WiFi mode, signal, noise, and signal quality.
    * Settings
        * Toggle the `Debugging` menu
        * Select the interface to view

### System
* `gdanko-stystem-BrewOutdated.30m.py`
    * Features
        * Display a list of outdated homebrew packages with an option to install one or all of them.
    * Settings
        * Toggle the `Debugging` menu
* `gdanko-system-CpuPercent.2s.py`
    * Features
        * Display average user, system, and idle times for the CPU.
        * Display user, system, and idle times for each individual core.
        * Display top CPU consumers with an option to attempt to kill those owned by you.
    * Settings
        * Toggle the `Debugging` menu
        * Toggle "Click to Kill" functionality
        * Set the kill signal to use when attempting to kill a process
        * Set the maximum number of top CPU consumers to display
* `gdanko-system-DiskConsumers.5m.py`
    * Features
        * Display the largest disk consumers for one or more paths, with the ability to open the selected item.
    * Settings
        * Toggle the `Debugging` menu
* `gdanko-system-DiskUsage.2s.py`
    * Features
        * Display used/total disk space for the specified mountpoint.
        * Display the mountpoint, device name, filesystem type, and mount options as shown by `mount (8)`.
    * Settings
        * Toggle the `Debugging` menu
        * Select the mountpoint to view
        * Select the unit for displaying the data, e.g., `M` or `Gi`
* `gdanko-system-MemoryUsage.2s.py`
    * Features
        * Display used/total system memory.
        * Display memory manufacturer and type (if possible), total memory, available memory, used memory, free memory, active memory, inactive memory, wired memory, and speculative memory.
        * Display top memory consumers with an option to attempt to kill those owned by you.
    * Settings
        * Toggle the `Debugging` menu
        * Toggle "Click to Kill" functionality
        * Set the kill signal to use when attempting to kill a process
        * Set the maximum number of top memory consumers to display
        * Select the unit for displaying the data, e.g., `M` or `Gi`
* `gdanko-system-SwapUsage.2s.py`
    * Features
        * Display used/total swap memory.
    * Settings
        * Toggle the `Debugging` menu
        * Select the unit for displaying the data, e.g., `M` or `Gi`
* `gdanko-system-SystemUpdates.15m.py`
    * Features
        * Display a list of available system updates and their version numbers, with an option to install them individually.
    * Settings
        * Toggle the `Debugging` menu
* `gdanko-system-Uptime.2s.py`
    * Features
        * Display system uptime.
        * Display last boot time.
    * Settings
        * Toggle the `Debugging` menu

### Weather
* `gdanko-weather-WeatherWAPI.10m.py`
    * Features
        * Display the current temperature for the specified location.
        * Display "feels like" temperaure, pressure, visibility, condition, dew point, humidity, precipitation, wind, wind chill, heat index, UV index.
        * Display up to an eight day forecast, showing low/high temperature, average temperature, average visibility, condition, average humidity, total precipitation, chance of rain, chance of snow, UV index, sunrise time, sunset time, moonrise time, moonset time, and moon phase.
    * Settings
        * Toggle the `Debugging` menu
        * Toggle displaying the `x Day Forecast` menu
        * Set the units in either `C` or `F`

### Other
* `gdanko-other-Earthquakes.15m.py`
    * Features
        * Location based on gelocation of your IP address.
        * Display a list of recent earthquakes based on your location.
        * Display the magnitude, time of occurence, updated time, status, as well as a clickable link for the quake's details page at usgs.gov.
    * Settings
        * Toggle the `Debugging` menu
        * Set the limit for the number of results to display
        * Set the minimum magnitude
        * Set the radius based on your location
        * Set the unit in either `km` or `m`

## How Do the Settings Toggles Work?
* Each plugin first determines the path to the config directory and the name of the plugin.
* When you change a setting, the plugin is invoked with a flag, e.g., `--max-consumers 5`. The Python `argparse` module is used to parse these flags. If a configured flag is set, the plugin calls `plugin.update_config()`, passing the config path, plugin name, variable name, and new value. `plugin.update_config()` determines the path to the JSON var file and updates the value accordingly. The settings toggles are all configured to refresh the plugin so once you make the change, everything is reloaded.

