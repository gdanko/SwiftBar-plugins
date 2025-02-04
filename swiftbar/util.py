from collections import namedtuple
from pprint import pprint as pp
from typing import Any, Dict, List, Optional, Union
import datetime
import dateutil
import getpass
import platform
import re
import shutil
import signal
import subprocess
import time

def get_signal_map() -> Dict[str, signal.Signals]:
    """
    Return a dict containing all valid signals.
    """
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

def get_macos_version() -> str:
    """
    Determine the current OS version and return it as the full OS string.
    """
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

def pprint(input: Any=None):
    pp(input)
    print()

def execute_command(command: str=None, input: Optional[Any]=None):
    """
    Execute a system command, returning exit code, stdout, and stderr.
    """
    for command in re.split(r'\s*\|\s*', command):
        p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=input.encode('utf-8') if input else None)
        stdout = stdout.decode('utf-8').strip()
        stderr = stderr.decode('utf-8').strip()
        if stdout:
            input = stdout
    return p.returncode, stdout, stderr

def brew_package_installed(package: str=None) -> bool:
    returncode, stdout, stderr = execute_command(f'brew list {package}')
    return True if returncode == 0 else False

def binary_exists(binary: str=None) -> bool:
    return shutil.which(binary) is not None

def find_all_network_interfaces() -> List[str]:
    """
    Find and return a list of all interfaces using ifconfig.
    """
    returncode, stdout, _ = execute_command('ifconfig')
    if returncode == 0  and stdout:
        pattern = r'([a-z0-9]+):\s*flags='
        matches = re.findall(pattern, stdout)
        return sorted(matches) if (matches and type(matches) == list) else ['lo0']

def find_valid_network_interfaces() -> str:
    """
    Find and return a list of all valid interfaces using networksetup.
    """
    returncode, stdout, _ = execute_command('networksetup -listallhardwareports')
    if returncode == 0  and stdout:
        pattern = r'Hardware Port:.*\nDevice:\s+(.*)'
        matches = re.findall(pattern, stdout)
        return sorted(matches) if (matches and type(matches) == list) else ['en0']

def find_valid_wifi_interfaces() -> List[str]:
    """
    Find and return a list of all wireless interfaces using networksetup.
    """
    returncode, stdout, _ = execute_command('networksetup -listallhardwareports')
    if returncode == 0  and stdout:
        pattern = r'Hardware Port: Wi-Fi.*\nDevice:\s+(.*)'
        matches = re.findall(pattern, stdout)
        return sorted(matches) if (matches and type(matches) == list) else ['en0']

def find_valid_mountpoints() -> List[str]:
    """
    Find and return a list of all mounted filesystems.
    """
    returncode, stdout, _ = execute_command('mount')
    if returncode == 0  and stdout:
        pattern = r'/dev/disk[s0-9]+ on\s+([^\)]+)\s+\('
        matches = re.findall(pattern, stdout)
        return sorted(matches) if (matches and type(matches) == list) else ['/']

def valid_storage_units() -> List[str]:
    """
    Return a list of valid units of storage.
    """
    return ['K', 'Ki', 'M', 'Mi', 'G', 'Gi', 'T', 'Ti', 'P', 'Pi', 'E', 'Ei', 'Z', 'Zi', 'auto']

def valid_weather_units() -> List[str]:
    return ['C', 'F']

def parse_version(version_string: str=None):
    """
    Parse a version string and return a namedtuple containing all of the bits.
    """
    fields = [f'part{i + 1}' for i in range(len(version_string.split('.')))]
    version = namedtuple('version', fields)
    parts = map(int, version_string.split('.'))
    return version(*parts)

def get_process_icon(process_owner: str=None, click_to_kill: bool=False) -> str:
    """
    Return a skull icon if a process can be kill or a no entry sign icon if it cannot.
    """
    if click_to_kill:
        if process_owner == getpass.getuser():
            return ':skull:'
        else:
            return ':no_entry_sign:'
    else:
        return ''

def get_sysctl(metric: str=None) -> Union[str, None]:
    """
    Execute sysctl via execute_command() and return the results or None.
    """
    command = f'sysctl -n {metric}'
    returncode, stdout, _ = execute_command(command)
    return stdout if returncode == 0 else None

def byte_converter(bytes: int=0, unit: str=None) -> str:
    """
    Convert bytes to the given unit.
    """
    suffix = 'B'
    prefix = unit[0]
    divisor = 1000

    if len(unit) == 2 and unit.endswith('i'):
        divisor = 1024

    prefix_map = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
    return f'{pad_float(bytes / (divisor ** prefix_map[prefix]))} {unit}{suffix}'

def process_bytes(num: int=0) -> str:
    """
    Process the rate of data, e.g., MiB/s.
    """
    suffix = 'B'
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f'{round(num, 2)} {unit}{suffix}/s'
        num = num / 1024
    return f'{pad_float(num)} Yi{suffix}'

def format_number(num: int=0) -> str:
    """
    Take a number of bytes and automatically convert to the most logical unit.
    """
    suffix = 'B'
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f'{round(num, 2)} {unit}{suffix}'
        num = num / 1024
    return f'{pad_float(num)} Yi{suffix}'

def prettify_timestamp(timestamp: str=None, format:str='%Y-%m-%d %H:%M:%S'):
    """
    Parse a data-based timestamp and convert it to the specified format.
    """
    try:
        parsed = dateutil.parser.parse(timestamp)
        seconds = parsed.timestamp()
        new_timestamp = datetime.datetime.fromtimestamp(seconds)
        return new_timestamp.strftime(format)
    except Exception as e:
        print(e)
        return timestamp
    
def get_timestamp(timestamp: int=0, format: Optional[str]='%Y-%m-%d %k:%M:%S')-> str:
    """
    Take a Unix timestamp and convert it to the specified format.
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime(format)

def unix_to_human(timestamp, format: Optional[str]='%Y-%m-%d') -> str:
    """
    Take a Unix timestamp and convert it to the specified format.
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime(format)

def unix_time_in_ms() -> int:
    """
    Return the Unix timestamp in millesconds.
    """
    return int(time.time() * 1000)

def pad_float(number: int=0) -> str:
    """
    Pad a float to two decimal places.
    """
    return '{:.2f}'.format(float(number))

def to_dollar(number: int=0) -> str:
    """
    Convert the specified integer as a dollar based format, e.g., $2,000.
    """
    return '${:,.2f}'.format(number)

def add_commas(number: int=0) -> str:
    """
    Add commas to integers.
    """
    return '{:,.0f}'.format(number)

def float_to_pct(number: int=0) -> str:
    """
    Convert a floating point number to its percent equivalent.
    """
    return f'{number:.2%}'

def miles_to_kilometers(miles: int=0) -> float:
    """
    Convert miles to kilometers.
    """
    return miles * 1.609344

def kilometers_to_miles(kilometers: int=0) -> float:
    """
    Convert kilometers to miles.
    """
    return kilometers * 0.6213712

def numerize(number: int=0) -> str:
    """
    Convert something like 1000000000 to 1B.
    """
    abs_number = abs(number)
    if abs_number >= 1000000000000:
        return f'{abs_number / 1000000000000:.1f}T'
    elif abs_number >= 1000000000:
        return f'{abs_number / 1000000000:.1f}B'
    elif abs_number >= 1000000:
        return f'{abs_number / 1000000:.1f}M'
    elif abs_number >= 1000:
        return f'{abs_number / 1000:.1f}K'
    elif abs_number < 0 and abs_number > -10000:
        return f'{abs_number / -1000:.1f}K'
    else:
        return str(number)

    return f'-{formatted}' if n < 0 else formatted
