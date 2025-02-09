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

## Making it All Work
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
* Plugins should be able to automatically generate the argparer from `plugin.defaults_dict`.
* Plugins should be able to automatically generate the settings menu from `plugin.defaults_dict`.
* Automatically generate a plugin configration file using default values for every plugin that can use one. Its location is based on `plugin.config_dir` and `plugin.plugin_name`. For example, if you're using SwiftBar and your plugin name is `fancy-plugin-DoSomething.10s.py` then your plugin configuration file's path will be `~/.config/SwiftBar/fancy-plugin-DoSomething.10s.py.vars.json`.
* All plugins have a `Settings` menu that can modify MOST of the settings. Obviously, things like API keys need to be manually configured by hand editing the JSON. If a specific setting displays a list of options, e.g., network interfaces, the currently selected option will have a checkmark next to it. The selected option used to be colored differently, but I opted to use a checkmark for the sake of accessibility.
* All plugins have a debugging menu that can be toggled via the plugin's `Settings` menu which shows the following:
    * OS version, e.g., `macOS 15.2 (Sequoia)`
    * Installed system memory
    * Debug flag enabled
    * Brew enabled (whether or not `${HOMEBREW_PREFIX}/bin` and `${HOMEBREW_PREFIX}/sbin` are included in the PATH)
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
    * Variables listed in `FOO = bar` format
    * Environment variables listed in `FOO = bar` format

## The `defaults_dict`
The defaults_dict is an instance of `collections.OrderedDict` that does a few things
* Create a set of defaults for all of the variables used by the plugin.
* Generate the `.vars.json` file if it doesn't exist.
* Find and set variables that are missing from the `.vars.json` file.
* Store data used for generating the plugin's `argparse.Namespace` object.
* Determine how to process changes made via the `Settings` menu.
* Render the `Settings` menu.

### Building a `defaults_dict`
Here are some sample defaults_dict entries
```python
plugin.defaults_dict['VAR_WEATHER_WAPI_DEBUG_ENABLED'] = {
    'default_value': False,
    'valid_values': [True, False],
    'type': bool,
    'setting_configuration': {
        'default': False,
        'flag': '--debug',
        'title': 'the "Debugging" menu',
    },
}
plugin.defaults_dict['VAR_DISK_USAGE_MOUNTPOINT'] = {
    'default_value': '/',
    'valid_values': valid_mountpoints,
     'type': str,
    'setting_configuration': {
        'default': None,
        'flag': '--mountpoint',
        'title': 'Mountpoint',
    },
}
plugin.defaults_dict['VAR_DISK_USAGE_UNIT'] = {
    'default_value': 'auto',
    'valid_values': util.valid_storage_units(),
    'type': str,
    'setting_configuration': {
        'default': None,
        'flag': '--unit',
        'title': 'Unit',
    },
}
plugin.defaults_dict['VAR_EARTHQUAKES_RADIUS_MILES'] = {
    'default_value': 100,
    'minmax': namedtuple('minmax', ['min', 'max'])(50, 500),
    'type': int,
    'setting_configuration': {
        'default': None,
        'flag': '--radius',
        'increment': 50,
        'title': 'Radius',
    },
}
```
Each entry is mapped to one of the xbar-style `<xbar.var></xbar.var>` variable/comment entries. I'll explain each of the fields an what it does.
* `default_value` - This is the default value for this variable. If, when parsing the configuration file, the variable is missing or invalid, this default entry will replace the existing value and the `.vars.json` file will be rewritten.
* `valid_values` - This is a list of valid values for the given field. As you can see in the `VAR_DISK_USAGE_UNIT` example, the list of valid values is returned from a function in `util`. When parsing the configuration file, if the value `VAR_DISK_USAGE_UNIT` is not included in `valid_values`, it will be replaced by the value defined by `default_value`.
* `minmax` - This is a type of value used when you want a list of numbers with a defined increment. If the value in the configuration is less than `min` or greater than `max`, it will be replaced by the value defined by `default_value`.
* `type` - This is the type of value the setting will use. For example, `VAR_WEATHER_WAPI_DEBUG_ENABLED` is a `bool` and `VAR_EARTHQUAKES_RADIUS_MILES` is an `int`.
* `settings` - This block is used for any variable that can be used as a setting. Its fields will be explained below.
    * `default` - This is the default value for the `agrparse.Namespace` object. It's used to determine if a setting has been changed via one of the argument flags.
    * `flag` - This is the flag name for `argparse` action. Also, when checking to see if flags were sent at plugin invocation, it's used to invoke the plugin with the flag in order to change the setting.
    * `increment` - If the setting block uses `minmax`, this is the increment for displaying the list. For example, in the above list, `VAR_EARTHQUAKES_RADIUS_MILES` has a `min` of 50 and a `max` of 500. With an `increment` of 50, the list will be rendered as 50, 100, 150.....500. If one is not specified, the default is 10. I will eventually programatically change the logic to adjust the default increment based on the the size of the span from `min` to `max`.
    * `title` - This is an important setting. This is the title of the `Settings` menu item. If the variable type is `bool`, the menu item will be either `Enable {title}` or `Disable {title}`, depending on the current state of the variable. For this reason, the title, in this example, is `the "Debugging" menu`. For every other type of setting, you can just put the name of the item, e.g., `Radius` or `Unit`.

Note, you should follow this format when setting the `default` field in a `setting_configuration` block:
* `bool` = `False`
* `float` = `None`
* `int` = `None`
* `str` = `None`

## The `Plugin()` Class
The plugin class is used by all plugins to do things like define plugin settings, render the `Settings` menu, and more. In a very simple example, you can do something like this.
```
plugin = Plugin()
plugin.print_menu_title('Plugin Output')
plugin.render_footer()
```

### `Plugin()` Parameters
You can define a few things when you instantiate an instance of the class:
* `disable_brew` excludes `${HOMEBREW_PREFIX}/bin` and `${HOMEBREW_PREFIX}/sbin` from the PATH when you want to use built-in versions of certain binaries.
* `font_family` defines the default font family for the plugin's output. You can, of course, override this with the `font` parameter when using something like `plugin.print_menu_item()`.
* `font_size` defines the default font size for the plugin's output. You can, of course, override this with the `size` parameter when using something like `plugin.print_menu_item()`.

### Noteable `Plugin()` Methods
* `plugin._set_path()` - Executed at instantiation, this function sets the path based on whether or not homebrew is installed. If the `disable_brew` parameter is passed, homebrew paths are excluded automatically.
* `plugin._get_config_dir()` - Executed at instantiation, this function sets `plugin.invoked_by` by examining the parent pid of the executed plugin. It then uses that value to set the location of the configuration directory.
* `plugin._create_config_dir()` - Executed at instantiation, this function should only be when `plugin.invoked_by` is `SwiftBar`, since plugin `.var.json` files cannot live in the same directory as the plugins themselves.
* `plugin.setup()` - This has to be executed after adding any settings to `plugin.defaults_dict`. It executes the followin methods:
    * `plugin._read_config()` - This method is used to sanitize and populate `plugin.configuation` from the `.vars.json` file if it exists. If the file does not exist, one is created from the defaults. We call it here to get the values of any booleans so that if the plugin is executed with a flag like `--debug`, we can now compare the existing setting with the new setting and make the change to the `.vars.json` file as needed.
    * `plugin._generate_args()` - This method generates the `argparse.Namespace` object from `plugin.defaults_dict` and parse the command line arguments.
    * `plugin._update_json_from_args()` - This method parses `plugin.parser` and gathers the arguments sent to the script. For each argument that was passed, it compares the passed value with the existing value stored in `plugin.configuration`. If we find an instance where a change was made, we pass the variable name, e.g., `VAR_SWAP_USAGE_DEBUG_ENABLED` and the new value to `plugin.update_setting()`. This function reads the `.vars.json` file to a dictionary, updates the changed setting, and rewrites the file. After rewriting the file, `plugin.read_config()` is called to repopulate `plugin.configuration`.
* `plugin._write_config()` - This method rewrites the plugin's `.vars.json` file any time a setting is changed.
* `plugin._write_default_vars_file()` - This method writes the `.vars.json` file from the contents of `plugin.defaults_dict`. It's used when a plugin's `.vars.json` file cannot be found.
* `plugin._rewrite_vars_file()` - This method completely rewrites the plugin's `.vars.json` file from the contents of `self.configuration`.
* `plugin.sanitize_params()` - This method takes an arbitrary list of params and returns an instance of `ParamsXbar` or `ParamsSwiftBar`, depending on the value of `plugin.invoked_by`.
* `plugin.print_ordered_dict()` - This method accepts a `collections.OrderedDict` object and renders it cleanly. It allows you to pass the entire dict instead of passing individual lines.
* `plugin.print_menu_item()` - This method accepts any of the parameters acceptable by `self.invoked_by` and renders it.
* `plugin.print_menu_separator()` - This method prints `---` to separate menu items.
* `plugin.print_update_time()` - This method prints the last date and time the plugin was updated. It's used by `plugin.print_menu_title()`.
* `plugin._update_setting()` - This method is invoked by `plugin._update_json_from_args()`. When the user changes a setting, the plugin is invoked with a unique flag, which tells `Plugin()` that the setting needs to be updated in the `.var.json` file.
* `plugin.find_longest` - This method accepts either a list or a dictionary. It returns the length of the longest member of the list, or in the case of a dictionary, the length of the longest dictionary key. It's used to properly pad lists of strings for proper formatting.
* `plugin._render_settings_menu()` - This method is invoked by `plugin.render_footer()` and renders the contents of the `Settings` menu.
* `plugin._render_debugging_menu()` - This method is invoked by `plugin.render_footer()` and renders the contents of the `Debugging` menu.

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
        * Toggle the `Company Info` sub-menu
        * Toggle the `Company Officers` sub-menu
        * Toggle the `Key Stats` sub-menu
        * Toggle the `Ratios and Profitability` sub-menu
        * Toggle the `Events` sub-menu

### Network
* `gdanko-network-NetworkThroughput.2s.py`
    * Features
        * Display the TX/RX rate for the specified interface.
        * Display interface flags, hardware address, IPV4 address, IPV6 address, and public IP address (if applicable).
    * Settings
        * Toggle verbose mode, which shows information about errors and dropped packets
        * Select the interface to view
* `gdanko-network-WifiSignal.30s.py`
    * Features
        * Display the specified interface's connection strength to its configured SSID.
        * Display device name, channel number, WiFi mode, signal, noise, and signal quality.
    * Settings
        * Toggle display of extended WiFi information, e.g., Mode, Signal, Noise, and so on
        * Select the interface to view

### System
* `gdanko-stystem-BrewOutdated.30m.py`
    * Features
        * Display a list of outdated homebrew packages with an option to install one or all of them.
* `gdanko-system-CpuPercent.2s.py`
    * Features
        * Display average user, system, and idle times for the CPU.
        * Display user, system, and idle times for each individual core.
        * Display top CPU consumers with an option to attempt to kill those owned by you.
    * Settings
        * Toggle display of extended CPU information, e.g., CPU model, CPU frequency, and so on
        * Toggle "Click to Kill" functionality
        * Set the kill signal to use when attempting to kill a process
        * Set the maximum number of top CPU consumers to display
* `gdanko-system-DiskConsumers.5m.py`
    * Features
        * Display the largest disk consumers for one or more paths, with the ability to open the selected item.

* `gdanko-system-DiskUsage.2s.py`
    * Features
        * Display used/total disk space for the specified mountpoint.
        * Display the mountpoint, device name, filesystem type, and mount options as shown by `mount (8)`.
    * Settings
        * Toggle display of extended partition information, e.g., mountpoint, device name, and so on
        * Select the mountpoint to view
        * Select the unit for displaying the data, e.g., `M` or `Gi`
        * Select the output format, e.g., `Used / Total`, `% Used`, or `% Free`
* `gdanko-system-MemoryUsage.2s.py`
    * Features
        * Display used/total system memory.
        * Display memory manufacturer and type (if possible), total memory, available memory, used memory, free memory, active memory, inactive memory, wired memory, and speculative memory.
        * Display top memory consumers with an option to attempt to kill those owned by you.
    * Settings
        * Toggle display of extended memory information, e.g., memory manufacter, memory type, and so on
        * Toggle "Click to Kill" functionality
        * Set the kill signal to use when attempting to kill a process
        * Set the maximum number of top memory consumers to display
        * Select the unit for displaying the data, e.g., `M` or `Gi`
* `gdanko-system-SwapUsage.2s.py`
    * Features
        * Display used/total swap memory.
    * Settings
        * Select the unit for displaying the data, e.g., `M` or `Gi`
* `gdanko-system-SystemUpdates.15m.py`
    * Features
        * Display a list of available system updates and their version numbers, with an option to install them individually.
* `gdanko-system-Uptime.2s.py`
    * Features
        * Display system uptime.
        * Display last boot time.

### Weather
* `gdanko-weather-WeatherWAPI.10m.py`
    * Features
        * Display the current temperature for the specified location.
        * Display "feels like" temperaure, pressure, visibility, condition, dew point, humidity, precipitation, wind, wind chill, heat index, UV index.
        * Display up to an eight day forecast, showing low/high temperature, average temperature, average visibility, condition, average humidity, total precipitation, chance of rain, chance of snow, UV index, sunrise time, sunset time, moonrise time, moonset time, and moon phase.
    * Settings
        * Toggle displaying the `x Day Forecast` menu
        * Set the units in either `C` or `F`

### Other
* `gdanko-other-Earthquakes.15m.py`
    * Features
        * Location based on gelocation of your IP address.
        * Display a list of recent earthquakes based on your location.
        * Display the magnitude, time of occurence, updated time, status, as well as a clickable link for the quake's details page at usgs.gov.
    * Settings
        * Set the limit for the number of results to display
        * Set the minimum magnitude
        * Set the maximum radius based on your location
        * Set the unit in either `km` or `m`

## How Do the Settings Toggles Work?
* Each plugin first determines the path to the config directory and the name of the plugin.
* When you change a setting, the plugin is invoked with a flag, e.g., `--max-consumers 5`. The Python `argparse` module is used to parse these flags. If a configured flag is set, the plugin calls `plugin.update_config()`, passing the config path, plugin name, variable name, and new value. `plugin.update_config()` determines the path to the JSON var file and updates the value accordingly. The settings toggles are all configured to refresh the plugin so once you make the change, everything is reloaded.

## General Overview of How a Plugin Works
First let's look at the code for a simple plugin that pulls information about system swap usage
```python
def main() -> None:
    plugin = Plugin(disable_brew=True)
    plugin.defaults_dict['VAR_SWAP_USAGE_UNIT'] = {
        'default_value': 'auto',
        'valid_values': util.valid_storage_units(),
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--unit',
            'title': 'Unit',
        },
    }
    plugin.setup()

    swap = get_swap_usage()
    if swap:
        used = util.format_number(swap.used) if plugin.configuration['VAR_SWAP_USAGE_UNIT'] == 'auto' else util.byte_converter(swap.used, plugin.configuration['VAR_SWAP_USAGE_UNIT'])
        total = util.format_number(swap.total) if plugin.configuration['VAR_SWAP_USAGE_UNIT'] == 'auto' else util.byte_converter(swap.total, plugin.configuration['VAR_SWAP_USAGE_UNIT'])
        plugin.print_menu_title(f'Swap: {used} / {total}')
    else:
        plugin.print_menu_title('Swap: Failed')
        plugin.print_menu_item('Failed to gather swap information')
    plugin.render_footer()
```

Now we'll explain what is happening.
* We create an instance of the `Plugin()` class, passing the `disable_brew` flag. This flag tells the plugin not to include `${HOMEBREW_PREFIX}/bin` or `${HOMEBREW_PREFIX}/sbin` in the path since we want to use the OS versions of certain binaries.
* We can now add additional variables to `plugin.defaults_dict`. If you have not read the section about this dictionary, please do so now.
* After adding variable definitions, we make a call to `plugin.setup()`. This is documented in the `Plugin()` section.
* Once all of that stuff is done, we call `get_swap_usage()` to gather the data. If the data is retrieved successfully we render the output happily, otherwise we display an error.
* The last call is to `plugin.render_footer()`. This function does three things:
    * It renders the "Debugging" menu if debugging is enabled.
    * It renders the "Settings" menu if `plugin.defaults_dict` exists.
    * It displays a "Refresh" menu item.
