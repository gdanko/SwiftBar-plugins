from pathlib import Path
import datetime
import getpass
import json
import os
import signal
import subprocess
import sys
import time

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

def get_command_output(command):
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    return stdout.strip().decode(), stderr.strip().decode()

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
    stdout, stderr = get_command_output(f'/bin/ps -o command -p {ppid} | tail -n+2')
    if stderr:
        return None
    if stdout:
        if stdout == '/Applications/xbar.app/Contents/MacOS/xbar':
            config_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            return os.path.basename(stdout), config_path
        elif stdout == '/Applications/SwiftBar.app/Contents/MacOS/SwiftBar':
            config_path = os.path.join(Path.home(), '.config', 'SwiftBar')
            if not os.path.exists(config_path):
                try:
                    os.makedirs(config_path)
                except:
                    pass
            return os.path.basename(stdout), config_path
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
    stdout, stderr = get_command_output(command)
    return stdout

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
