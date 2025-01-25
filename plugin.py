from pathlib import Path
import datetime
import getpass
import json
import os
import re
import signal
import subprocess
import sys
import time
import typing

# class Params(typing.TypedDict, total=False):
#     """
#     A set of optional parameters for menu items.
#     See https://github.com/swiftbar/SwiftBar#parameters for descriptions.
#     """

#     # Text Formatting:
#     ansi: bool
#     color: str
#     emojize: bool
#     font: str
#     length: int
#     md: bool
#     sfcolor: str
#     sfsize: int
#     size: int
#     symbolize: bool
#     trim: bool

#     # Visuals:
#     alternate: bool
#     checked: bool
#     dropdown: bool
#     image: str
#     sfimage: str
#     templateImage: str
#     tooltip: str

#     # Actions:
#     cmd: list
#     refresh: bool
#     href: str
#     shortcut: str
#     bash: str
#     shell: str
#     terminal: bool

# class Writer(typing.Protocol):
#     """
#     Anything that supports write.
#     """

#     def write(self, _: str, /) -> int: ...

def get_signal_map():
    return {
        'SIHGUP': signal.SIGHUP,
        'SIGINT': signal.SIGINT,
        'SIGQUIT': signal.SIGQUIT,
        'SIGILL': signal.SIGILL,
        'SIGTRAP': signal.SIGTRAP,
        'SIGABRT': signal.SIGABRT,
        'SIGEMT': signal.SIGEMT,
        'SIGFPE': signal.SIGFPE,
        'SIGKILL': signal.SIGKILL,
        'SIGBUS': signal.SIGBUS,
        'SIGSEGV': signal.SIGSEGV,
        'SIGSYS': signal.SIGSYS,
        'SIGPIPE': signal.SIGPIPE,
        'SIGALRM': signal.SIGALRM,
        'SIGTERM': signal.SIGTERM,
        'SIGURG': signal.SIGURG,
        'SIGSTOP': signal.SIGSTOP,
        'SIGTSTP': signal.SIGTSTP,
        'SIGCONT': signal.SIGCONT,
        'SIGCHLD': signal.SIGCHLD,
        'SIGTTIN': signal.SIGTTIN,
        'SIGTTOU': signal.SIGTTOU,
        'SIGIO': signal.SIGIO,
        'SIGXCPU': signal.SIGXCPU,
        'SIGXFSZ': signal.SIGXFSZ,
        'SIGVTALRM': signal.SIGVTALRM,
        'SIGPROF': signal.SIGPROF,
        'SIGWINCH': signal.SIGWINCH,
        'SIGINFO': signal.SIGINFO,
        'SIGUSR1': signal.SIGUSR1,
        'SIGUSR2': signal.SIGUSR2,
    }

def execute_command(command, input=None):
    for command in re.split(r'\s*\|\s*', command):
        p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=input.encode('utf-8') if input else None)
        stdout = stdout.decode('utf-8').strip()
        stderr = stderr.decode('utf-8').strip()
        if stdout:
            input = stdout
    return p.returncode, stdout, stderr

def read_config(vars_file, default_values):
    if os.path.exists(vars_file):
        try:
            with open(vars_file, 'r') as fh:
                contents = json.load(fh)
                for key, _ in default_values.items():
                    if key in contents:
                        default_values[key] = contents[key]
            return default_values
        except:
            return default_values
    else:
        try:
            with open(vars_file, 'w') as fh:
                fh.write(json.dumps(default_values, indent=4))
        except:
            pass
        return default_values

def write_config(jsonfile, contents):
    with open(jsonfile, 'w') as fh:
        fh.write(json.dumps(contents, indent=4))

def update_setting(config_dir, plugin_name, key, value):
    vars_file = os.path.join(config_dir, plugin_name) + '.vars.json'
    if os.path.exists(vars_file):
        with open(vars_file, 'r') as fh:
            contents = json.load(fh)
            if key in contents:
                contents[key] = value
                write_config(vars_file, contents)

def get_config_dir():
    ppid = os.getppid()
    returncode, stdout, stderr = execute_command(f'/bin/ps -o command -p {ppid} | tail -n+2')
    if returncode != 0 or stderr:
        return None
    if stdout:
        if stdout == '/Applications/xbar.app/Contents/MacOS/xbar':
            config_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            return os.path.basename(stdout), config_dir
        elif stdout == '/Applications/SwiftBar.app/Contents/MacOS/SwiftBar':
            config_dir = os.path.join(Path.home(), '.config', 'SwiftBar')
            if not os.path.exists(config_dir):
                try:
                    os.makedirs(config_dir)
                except:
                    pass
            return os.path.basename(stdout), config_dir
    return 'local', Path.home()

def get_process_icon(process_owner, click_to_kill):
    if click_to_kill:
        if process_owner == getpass.getuser():
            return ':skull:'
        else:
            return ':no_entry_sign:'
    else:
        return ''

def get_sysctl(metric):
    command = f'sysctl -n {metric}'
    returncode, stdout, stderr = execute_command(command)
    return stdout

# Formatting functions
def byte_converter(bytes, unit):
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{pad_float(bytes / (divisor ** prefix_map[prefix]))} {unit}{suffix}'

def process_bytes(num):
    suffix = 'B'
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f'{round(num, 2)} {unit}{suffix}/s'
        num = num / 1024
    return f'{pad_float(num)} Yi{suffix}'

def format_number(size):
    factor = 1024
    bytes = factor
    megabytes = bytes * factor
    gigabytes = megabytes * factor
    if size < gigabytes:
        if size < megabytes:
            if size < bytes:
                return f'{size} B'
            else:
                return byte_converter(size, "Ki")
        else:
            return byte_converter(size, "Mi")
    else:
        return byte_converter(size, "Gi")

# Conversion functions
def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def unix_time_in_ms():
    return int(time.time() * 1000)

def to_dollar(number):
    return '${:,.2f}'.format(number)

def add_commas(number):
    return '{:,.0f}'.format(number)

def unix_to_human(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def float_to_pct(number):
    return f'{number:.2%}'

# def print_menu_title(title: str, *, out: Writer = sys.stdout, **params: Params) -> None:
#     """
#     Print a menu title.
#     """

#     params_str = ' '.join(f'{k}={v}' for k, v in params.items())
#     print(f'{title} | {params_str}', file=out)

# def print_menu_item(text: str, *, out: Writer=sys.stdout, **params: Params) ->None:
#     # https://github.com/tmzane/swiftbar-plugins
#     # If python >= 3.11, we can replace **params: Params with **params: typing.Unpack[Params]
#     """
#     Print a menu item.
#     """
#     if 'cmd' in params and type(params['cmd']) == list and len(params['cmd']) > 0:
#         params['bash'] = params['cmd'][0]
#         for i, arg in enumerate(params['cmd'][1:]):
#             params[f'param{i}'] = arg
#         params.pop('cmd')
#     params_str = ' '.join(f'{k}={v}' for k, v in params.items())
#     print(f'{text} | {params_str}', file=out)

# def print_menu_separator(*, out: Writer = sys.stdout) -> None:
#     """
#     Print a menu separator.
#     """

#     print('---', file=out)
