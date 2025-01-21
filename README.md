# xbar-plugins
A collection of plugins for [SwiftBar](https://github.com/swiftbar/SwiftBar) (also compatible with [xbar](https://github.com/matryer/xbar)).

## Prerequisites
1. Either [SwiftBar](https://github.com/swiftbar/SwiftBar) or [xbar](https://github.com/matryer/xbar)
2. Python >= 3.11

## Installation
1. Clone this repository
```
git clone https://github.com/gdanko/xbar-plugins.git
```
2. Symlink the desired plugins to your [plugins folder](https://github.com/swiftbar/SwiftBar#plugin-folder)
```
ln -s /path/to/repo/plugin_name.py $SWIFTBAR_PLUGINS_PATH/plugin_name.py
```

## How Do I Use the Plugins With SwiftBar?
SwiftBar doesn't know what to do with xbar's `<plugin_name>.vars.json` files. With xbar, both the plugin file and its associated JSON vars file both live in `~/Library/Application Support/xbar/plugins`. SwiftBar doesn't like this. It tries unsuccessfully to execute the JSON files as scripts. To get around this, we determine who the name of the calling process, which will be one of `/Applications/xbar.app/Contents/MacOS/xbar` or `/Applications/SwiftBar.app/Contents/MacOS/SwiftBar`. If the caller is xbar, we set the config path to `~/Library/Application Support/xbar/plugins`. If the caller is SwiftBar, we set the config path to `~/.config/SwiftBar`.

When a plugin is executed, it attempts to look for a `.vars.json` file to set its values. If one doesn't exist, it will use the default values specified in the plugin's code. This logic applies to both xbar and SwiftBar. This solution allows you to use a traditional xbar `.vars.json` with SwiftBar. The only caveat to this approach is that when you select the `Run in Terminal` option, the default values are used because of the way the plugin is being invoked. I am looking for a solution to this problem.

## Plugins

* [Network](#network)
* [System](#system)
* [Weather](#weather)

### Network
* gdanko-network-NetworkThroughput.2s.py - This plugin reads a configured interface name and displays received and transmitted data rates. When you click on the menu bar item you can then see:
    * Interface flags
    * Hardware address
    * IPV4 address
    * IPV6 address
    * Public IP address (if applicable)
* gdanko-network-WifiSignal.30s.py - This plugin reads a configured interface name and displays connection strengh for the connected SSID. When you click on the menu bar item you can then see:
    * Device
    * Channel
    * Mode, e.g., 802.11ac
    * Signal
    * Noise
    * Quality

### System
* gdanko-system-CpuPercent.2s.py - This plugin shows average user, system, and idle times for the CPU. When you click on the menu bar item you can then see:
    * CPU type
    * user, system, and idle times for each individual core
    * Top CPU consumers - Show the CPU % and process name for top CPU consumers. If "Click to Kill" is enabled, you can attempt to kill any process in the list if it's owned by you. The process icon will show you those you are able to kill.
    * Settings
        * Toggle "Click to Kill"
        * Select the signal to be used when attempting to kill a process
        * Configure how many "Top Consumers" to display in the list
* gdanko-system-DiskConsumers.5m.py - This plugin reads a configured list of paths and shows the top disk consumers under directory. When you click on the menu bar item you can then see:
    * An entry for each configured path. You can click on any of the items in the list to attempt to open it.
* gdanko-system-DiskUsage.2s.py - This plugin reads a configured list of mountpoints and shows used/total space for each. When you click on the menu bar item you can then see:
    * An entry for each configured mountpoint. Under each mountpoint you will see:
        * The mountpoint, e.g., /Volumes/Foo
        * The device name, e.g., /dev/disk1s1
        * The filesystem type, e.g., apfs
        * The mount options, e.g., apfs, local, nodev, nosuid, journaled
* gdanko-system-MemoryUsage.2s.py - This plugin shows used/total system memory. When you click on the menu bar item you can then see:
    * Memory type
    * Total memory
    * Available memory
    * Used memory
    * Free memory
    * Active memory
    * Inactive memory
    * Wired memory
    * Top Memory consumers - Show the memory usage and process name for top memory consumers. If "Click to Kill" is enabled, you can attempt to kill any process in the list if it's owned by you. The process icon will show you those you are able to kill.
    * Settings
        * Toggle "Click to Kill"
        * Select the signal to be used when attempting to kill a process
        * Configure how many "Top Consumers" to display in the list
* gdanko-system-SwapUsage.2s.py - This plugin shows used/total swap memory.
* gdanko-system-SystemUpdates.15m.py - This plugin shows the number of available system updates.
* gdanko-system-Uptime.2s.py - This plugin shows system uptimes. When you click on the menu bar item you can then see:
    * Last boot time

### Weather
* gdanko-weather-WeatherWAPI.10m.py - This plugin reads configuration for API key, location, unit (C/F), and verbose flag and shows the current weather for the specified location. When you click on the menu bar item you can then see:
    * Feels like temperature
    * Pressure
    * Visibility
    * Condition
    * Dew point
    * Humidity
    * Precipitation
    * Wind
    * Wind chill
    * Heat index
    * UV index
    * x Day Forecast - Show weather data for the next few days

## How Do the Settings Toggles Work?
* Each plugin first determines the path to the config directory and the name of the plugin.
* When you change a setting, the plugin is invoked with a flag, e.g., `--max-consumers 5`. The Python `argparse` module is used to parse these flags. If a configured flag is set, the plugin calls `plugin.update_config()`, passing the config path, plugin name, variable name, and new value. `plugin.update_config()` determines the path to the JSON var file and updates the value accordingly. The settings toggles are all configured to refresh the plugin so once you make the change, everything is reloaded.

