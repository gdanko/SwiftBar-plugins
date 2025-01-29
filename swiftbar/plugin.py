from collections import OrderedDict
from pathlib import Path
from swiftbar import util
from swiftbar.params import Params, ParamsXbar, ParamsSwiftBar
from typing import Any, Dict, List, Union
import json
import os
import shutil
import sys
import time
import typing

class Writer(typing.Protocol):
    def write(self, _: str, /) -> int: ...

class Plugin:
    def __init__(self) -> None:
        self.config_dir = os.path.join(Path.home(), 'SwiftBar')
        self.invoked_by = None
        self.invoked_by_full = None

        self._get_config_dir()
        self._create_config_dir()

        self.font = 'AndaleMono'
        self.size = 13

        self.success = True
        self.error_messages = []

        self.configuration = {}
        self.plugin_name = os.path.abspath(sys.argv[0])
        self.plugin_basename = os.path.basename(self.plugin_name)
        self.vars_file = os.path.join(self.config_dir, self.plugin_basename) + '.vars.json'

    def _get_config_dir(self) -> None:
        """
        Determine the location of the configuration directory based on self.invoked_by, gotten from the parent PID.
        """
        ppid = os.getppid()
        self.invoker_pid = ppid
        returncode, stdout, stderr = util.execute_command(f'/bin/ps -o command -p {ppid} | tail -n+2')
        if returncode != 0 or stderr:
            pass
        if stdout:
            self.invoked_by_full = stdout
            self.invoked_by = os.path.basename(self.invoked_by_full)
            if stdout == '/Applications/xbar.app/Contents/MacOS/xbar':
                self.config_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            elif stdout == '/Applications/SwiftBar.app/Contents/MacOS/SwiftBar':
                self.config_dir = os.path.join(Path.home(), '.config', 'SwiftBar')
            else:
                self.config_dir = os.path.join(Path.home(), 'SwiftBar')

    def _create_config_dir(self) -> None:
        """
        Create the configuration directory if it doesn't exist.
        """
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir)
            except:
                pass

    def write_config(self, contents: dict=None) -> None:
        # Let's make sure this is not duplicated
        """
        Write the JSON variables file.
        """
        with open(self.vars_file, 'w') as fh:
            fh.write(json.dumps(contents, indent=4))

    def _write_default_vars_file(self, defaults_dict: Dict[str, Any]=None) -> None:
        """
        Write a new JSON variables file from the contents of the defaults_dict sent by the plugin.
        """
        config_data = {}
        for key, value in defaults_dict.items():
            config_data[key] = value['default_value']
            self.configuration = config_data
        with open(self.vars_file, 'w') as fh:
            fh.write(json.dumps(config_data, indent=4))
    
    def _rewrite_vars_file(self) -> None:
        """
        Rewrite the JSON variables file from the contents of self.coniguration.
        """
        with open(self.vars_file, 'w') as fh:
            fh.write(json.dumps(self.configuration, indent=4))

    def read_config(self, defaults_dict: Dict[str, Any]=None) -> None:
        """
        Read and validate the defaults_dict sent by the plugin
        """
        if os.path.exists(self.vars_file):
            with open(self.vars_file, 'r') as fh:
                contents = json.load(fh)
                for key, value in defaults_dict.items():
                    if key in contents:
                        if 'valid_values' in value:
                            if contents[key] in value['valid_values']:
                                self.configuration[key] = contents[key]
                            else:
                                self.configuration[key] = defaults_dict[key]['default_value']
                        elif 'minmax' in value:
                            if contents[key] >= value['minmax'].min and contents[key] <= value['minmax'].max:
                                self.configuration[key] = contents[key]
                            else:
                                self.configuration[key] = defaults_dict[key]['default_value']
                        else:
                            self.configuration[key] = contents[key]
                    else:
                        self.configuration[key] = defaults_dict[key]['default_value']
                if contents != self.configuration:
                    self._rewrite_vars_file()
        else:
            self._write_default_vars_file(defaults_dict)
        
        for key, value in self.configuration.items():
            value = 'true' if value == True else 'false'
            os.environ[key] = value

    # def process_input(data: Union[List[int], Dict[str, int]]) -> None:
    def update_setting(self, key: str=None, value: Any=None) -> None:
        """
        Update a given setting for a plugin and rewrite the JSON variables file.
        """
        if os.path.exists(self.vars_file):
            with open(self.vars_file, 'r') as fh:
                contents = json.load(fh)
                if key in contents:
                    contents[key] = value
                    self.write_config(contents)

    def find_longest(self, input: Union[List[str], Dict[str, Any]]=None) ->int:
        """
        Find the longest item in a list or the longest key in a dict. Used for formatting lists.
        """
        if type(input) == list:
            return max(len(key) for key in input)
        elif type(input) == dict or type(input) == OrderedDict:
            return max(len(key) for key in input.keys())

    def sanitize_params(self, **params: Params) -> Union[ParamsXbar, ParamsSwiftBar]:
        """
        Create a new params object based on the value of self.invoked_by. Both xbar and SwiftBar have some unique
        parameters and this will allow the work to be handled behind the scenes.
        """
        sanitized = ParamsXbar() if self.invoked_by == 'xbar' else ParamsSwiftBar()
        for k, v in params.items():
            try:
                sanitized[k] = v
            except KeyError as e:
                pass
        return sanitized

    def print_menu_title(self, text: str, *, out: Writer=sys.stdout, **params: Params) -> None:
        """
        Print the plugin title in the menu bar.
        """
        params = self.sanitize_params(**params)
        params_str = ' '.join(f'{k}={v}' for k, v in params.items())
        print(f'{text} | {params_str}', file=out)
        self.print_update_time()

    def print_ordered_dict(self, data: OrderedDict, justify: str='right', delimiter: str = '', indent: int=0, *, out: Writer=sys.stdout, **params: Params) -> None:
        """
        Render an instance of collections.OrderedDict().
        """
        indent_str = indent * '-'
        longest = self.find_longest(data)
        params['trim'] = False
        params_str = ' '.join(f'{k}={v}' for k, v in params.items())
        for k, v in data.items():
            if justify == 'left':
                self.print_menu_item(f'{indent_str}{k.ljust(longest)} {delimiter} {v} | {params_str}', **params)
            elif justify == 'right':
                self.print_menu_item(f'{indent_str}{k.rjust(longest)} {delimiter} {v} | {params_str}', **params)

    def print_menu_item(self, text: str, *, out: Writer=sys.stdout, **params: Params) -> None:
        """
        Generic wrapper to print all non-title menu items.
        """
        # https://github.com/tmzane/swiftbar-plugins
        params = self.sanitize_params(**params)

        # Set default font if one isn't configured
        if not 'font' in params:
            params['font'] = self.font
        
        # Set default font size if one isn't configured
        if not 'size' in params:
            params['size'] = self.size

        if 'cmd' in params and type(params['cmd']) == list and len(params['cmd']) > 0:
            params['bash'] = f'"{params["cmd"][0]}"'
            for i, arg in enumerate(params['cmd'][1:]):
                params[f'param{i + 1}'] = f'"{arg}"'
            if 'cmd' in params:
                params.pop('cmd')

        params_str = ' '.join(f'{k}={v}' for k, v in params.items())
        print(f'{text} | {params_str}', file=out)

    def print_menu_separator(self, *, out: Writer = sys.stdout) -> None:
        """
        Print a menu separator.
        """
        print('---', file=out)
    
    def print_update_time(self, *, out: Writer = sys.stdout) -> None:
        """
        Print the updated time in human format.
        """
        self.print_menu_separator()
        self.print_menu_item(f'Updated {util.get_timestamp(int(time.time()))}')
        self.print_menu_separator()

    def display_debugging_menu(self):
        """
        Create a menu item to display plugin debug information.
        """
        pv = sys.version_info
        os_version = util.get_macos_version()
        total_mem = util.get_sysctl('hw.memsize')

        self.print_menu_item('Debugging')
        debug_data = OrderedDict()
        if os_version:
            debug_data['OS version'] = os_version
        if total_mem:
            debug_data['Memory'] = util.format_number(int(total_mem))
        debug_data['Python'] = shutil.which('python3')
        debug_data['Python version'] = f'{pv.major}.{pv.minor}.{pv.micro}-{pv.releaselevel}'
        debug_data['Plugins directory'] = os.path.dirname(self.plugin_name)
        debug_data['Plugin path'] = self.plugin_name
        debug_data['Invoked by'] = self.invoked_by
        debug_data['Invoked by (full path)'] = self.invoked_by_full
        debug_data[f'{self.invoked_by} pid'] = self.invoker_pid
        if self.invoked_by == 'SwiftBar':
            debug_data['SwiftBar version'] = f'{os.environ.get("SWIFTBAR_VERSION")} build {os.environ.get("SWIFTBAR_BUILD")}'
        debug_data['Default font family'] = self.font
        debug_data['Default font size'] = self.size
        debug_data['Configuration directory'] = self.config_dir
        debug_data['Variables file'] = self.vars_file
        self.print_ordered_dict(debug_data, justify='left', indent=2)
        self.print_menu_item('--Variables')
        variables = OrderedDict()
        for key, value in self.configuration.items():
            variables[key] = value
        self.print_ordered_dict(variables, justify='right', indent=4, delimiter = '=')
        self.print_menu_item('--Environment Variables')
        environment_variables = OrderedDict()
        for key in sorted(os.environ.keys()):
            environment_variables[key] = os.environ.get(key)
        self.print_ordered_dict(environment_variables, justify='right', indent=4, delimiter = '=', length=125)
