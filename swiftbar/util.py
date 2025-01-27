from collections import namedtuple
import datetime
import dateutil
import getpass
import platform
import re
import signal
import subprocess
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

def get_macos_version():
    os_version = parse_version(platform.mac_ver()[0])
    macos_families = {
        '10.0': 'Cheetah',
        '10.1': 'Puma',
        '10.2': 'Jaguar',
        '10.3': 'Panther',
        '10.4': 'Tiger',
        '10.5': 'Leopard',
        '10.6': 'Snow Leopard',
        '10.7': 'Lion',
        '10.8': 'Mountain Lion',
        '10.9': 'Mavericks',
        '10.10': 'Yosemite',
        '10.11': 'El Capitan',
        '10.12': 'Sierra',
        '10.13': 'High Sierra',
        '10.14': 'Mojave',
        '10.15': 'Catalina',
        '11': 'Big Sur',
        '12': 'Monterey',
        '13': 'Ventura',
        '14': 'Sonoma',
        '15': 'Sequoia',
    }
    if os_version.part1 == 10:
        version_string = f'{os_version.part1}.{os_version.part2}'
    elif os_version.part1 > 10:
        version_string = f'{os_version.part1}'
    return f'macOS {macos_families[version_string]} {os_version.part1}.{os_version.part2}'

def execute_command(command, input=None):
    for command in re.split(r'\s*\|\s*', command):
        p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=input.encode('utf-8') if input else None)
        stdout = stdout.decode('utf-8').strip()
        stderr = stderr.decode('utf-8').strip()
        if stdout:
            input = stdout
    return p.returncode, stdout, stderr

def find_all_network_interfaces():
    returncode, stdout, _ = execute_command('ifconfig')
    if returncode == 0  and stdout:
        pattern = r'([a-z0-9]+):\s*flags='
        matches = re.findall(pattern, stdout)
        return sorted(matches) if (matches and type(matches) == list) else ['lo0']

def find_valid_network_interfaces():
    returncode, stdout, _ = execute_command('networksetup -listallhardwareports')
    if returncode == 0  and stdout:
        pattern = r'Hardware Port:.*\nDevice:\s+(.*)'
        matches = re.findall(pattern, stdout)
        return sorted(matches) if (matches and type(matches) == list) else ['en0']

def find_valid_wifi_interfaces():
    returncode, stdout, _ = execute_command('networksetup -listallhardwareports')
    if returncode == 0  and stdout:
        pattern = r'Hardware Port: Wi-Fi.*\nDevice:\s+(.*)'
        matches = re.findall(pattern, stdout)
        return sorted(matches) if (matches and type(matches) == list) else ['en0']

def find_valid_mountpoints():
    returncode, stdout, _ = execute_command('mount')
    if returncode == 0  and stdout:
        pattern = r'/dev/disk[s0-9]+ on\s+([^\)]+)\s+\('
        matches = re.findall(pattern, stdout)
        return sorted(matches) if (matches and type(matches) == list) else ['/']

def valid_storage_units() -> list[str]:
    return ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei', 'auto']

def valid_weather_units() -> list[str]:
    return ['C', 'F']

def parse_version(version_string: str=''):
    fields = [f'part{i + 1}' for i in range(len(version_string.split('.')))]
    version = namedtuple('version', fields)
    parts = map(int, version_string.split('.'))
    return version(*parts)

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
    returncode, stdout, _ = execute_command(command)
    return stdout if returncode == 0 else None

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
    terabytes = gigabytes * factor
    petabytes = terabytes * factor
    exabytes = petabytes * factor
    if size < exabytes:
        if size < petabytes:
            if size < terabytes:
                if size < gigabytes:
                    if size < megabytes:
                        if size < bytes:
                            return f'{size} B'
                        else:
                            return byte_converter(size, 'Ki')
                    else:
                        return byte_converter(size, 'Mi')
                else:
                    return byte_converter(size, 'Gi')
            else:
                return byte_converter(size, 'Ti')
        else:
            return byte_converter(size, 'Pi')
    else:
        return byte_converter(size, 'Ei')

def prettify_timestamp(timestamp, format):
    try:
        parsed = dateutil.parser.parse(timestamp)
        seconds = parsed.timestamp()
        new_timestamp = datetime.datetime.fromtimestamp(seconds)
        return new_timestamp.strftime(format)
    except Exception as e:
        return timestamp

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

def unix_to_human(timestamp, format: str='%Y-%m-%d'):
    return datetime.datetime.fromtimestamp(timestamp).strftime(format)

def float_to_pct(number):
    return f'{number:.2%}'

def miles_to_kilometers(miles: int=0) ->float:
    return miles * 1.609344

def kilometers_to_miles(kilometers: int=0) ->float:
    return kilometers * 0.6213712
