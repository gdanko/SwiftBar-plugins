from collections import OrderedDict
from pathlib import Path
from swiftbar import util
import json
import os
import sys
import typing

class Params(typing.TypedDict, total=False):
    # Text Formatting:
    ansi: bool
    color: str
    emojize: bool
    font: str
    length: int
    md: bool
    sfcolor: str
    sfsize: int
    size: int
    symbolize: bool
    trim: bool

    # Visuals:
    alternate: bool
    checked: bool
    dropdown: bool
    image: str
    sfimage: str
    templateImage: str
    tooltip: str

    # Actions:
    cmd: list
    refresh: bool
    href: str
    shortcut: str
    bash: str
    shell: str
    terminal: bool

class Writer(typing.Protocol):
    def write(self, _: str, /) -> int: ...

class Plugin:
    def __init__(self):
        self.config_dir = os.path.join(Path.home(), 'SwiftBar')
        self.invoked_by = None
        self.invoked_by_full = None

        self.get_config_dir()
        self.create_config_dir()

        self.font = 'AndaleMono'
        self.size = 13

        self.success = True
        self.error_messages = []

        self.configuration = {}
        self.plugin_name = os.path.abspath(sys.argv[0])
        self.plugin_basename = os.path.basename(self.plugin_name)
        self.vars_file = os.path.join(self.config_dir, self.plugin_basename) + '.vars.json'

    def get_config_dir(self):
        ppid = os.getppid()
        self.invoker_pid = ppid
        returncode, stdout, stderr = util.execute_command(f'/bin/ps -o command -p {ppid} | tail -n+2')
        if returncode != 0 or stderr:
            pass
        if stdout:
            self.invoked_by_full = stdout
            self.invoked_by = os.path.basename(stdout)
            if stdout == '/Applications/xbar.app/Contents/MacOS/xbar':
                self.config_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            elif stdout == '/Applications/SwiftBar.app/Contents/MacOS/SwiftBar':
                self.config_dir = os.path.join(Path.home(), '.config', 'SwiftBar')
            else:
                self.config_dir = os.path.join(Path.home(), 'SwiftBar')

    def create_config_dir(self):
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir)
            except:
                pass

    def _write_default_vars_file(self, defaults_dict):
        config_data = {}
        for key, value in defaults_dict.items():
            config_data[key] = value['default_value']
            self.configuration = config_data
        with open(self.vars_file, 'w') as fh:
            fh.write(json.dumps(config_data, indent=4))
    
    def _rewrite_vars_file(self):
        with open(self.vars_file, 'w') as fh:
            fh.write(json.dumps(self.configuration, indent=4))

    def read_config(self, defaults_dict):
        invalid_value_found = False
        if os.path.exists(self.vars_file):
            try:
                with open(self.vars_file, 'r') as fh:
                    contents = json.load(fh)
                    for key, value in defaults_dict.items():
                        if key in contents:
                            self.configuration[key] = value['default_value']
                            if 'valid_values' in value:
                                if contents[key] in value['valid_values']:
                                    self.configuration[key] = contents[key]
                                else:
                                    invalid_value_found = True
                            else:
                                self.configuration[key] = contents[key]
                if invalid_value_found:
                    self._rewrite_vars_file()
            except:
                self._write_default_vars_file(defaults_dict)
        else:
            self._write_default_vars_file(defaults_dict)
 
    def write_config(self, contents):
        with open(self.vars_file, 'w') as fh:
            fh.write(json.dumps(contents, indent=4))

    def update_setting(self, key, value):
        if os.path.exists(self.vars_file):
            with open(self.vars_file, 'r') as fh:
                contents = json.load(fh)
                if key in contents:
                    contents[key] = value
                    self.write_config(contents)

    def print_menu_title(self, text: str, *, out: Writer=sys.stdout, **params: Params) ->None:
        params_str = ' '.join(f'{k}={v}' for k, v in params.items())
        print(f'{text} | {params_str}', file=out)

    def print_ordered_dict(self, data: OrderedDict, justify: str='right', delimiter: str = '=', indent: int=0, *, out: Writer=sys.stdout, **params: Params) ->None:
        indent_str = indent * '-'
        longest = max(len(key) for key, _ in data.items())
        params['trim'] = False
        params_str = ' '.join(f'{k}={v}' for k, v in params.items())
        for k, v in data.items():
            if justify == 'left':
                self.print_menu_item(f'{indent_str}{k.ljust(longest)} {delimiter} {v} | {params_str}', **params)
            elif justify == 'right':
                self.print_menu_item(f'{indent_str}{k.rjust(longest)} {delimiter} {v} | {params_str}', **params)

    def print_menu_item(self, text: str, *, out: Writer=sys.stdout, **params: Params) ->None:
        # https://github.com/tmzane/swiftbar-plugins
        # If python >= 3.11, we can replace **params: Params with **params: typing.Unpack[Params]

        # Set default font if one isn't configured
        if not 'font' in params:
            params['font'] = self.font
        
        # Set default font size if one isn't configured
        if not 'size' in params:
            params['size'] = self.size

        if 'cmd' in params and type(params['cmd']) == list and len(params['cmd']) > 0:
            params['bash'] = params['cmd'][0]
            for i, arg in enumerate(params['cmd'][1:]):
                params[f'param{i}'] = arg
        if 'cmd' in params:
            params.pop('cmd')
        params_str = ' '.join(f'{k}={v}' for k, v in params.items())
        print(f'{text} | {params_str}', file=out)

    def print_menu_separator(self, *, out: Writer = sys.stdout) -> None:
        print('---', file=out)

    def display_debug_data(self):
        self.print_menu_item('Debugging')
        debug_data = OrderedDict()
        debug_data['--Plugin path'] = self.plugin_name
        debug_data['--Invoked by'] = f'{self.invoked_by_full} (PID {self.invoker_pid})'
        debug_data['--Default font family'] = self.font
        debug_data['--Default font size'] = self.size
        debug_data['--Configuration directory'] = self.config_dir
        debug_data['--Variables file'] = self.vars_file
        self.print_ordered_dict(debug_data, justify='left')
        self.print_menu_item('--Variables')
        variables = OrderedDict()
        for key, value in self.configuration.items():
            variables[key] = value
        self.print_ordered_dict(variables, justify='right', indent=4)
