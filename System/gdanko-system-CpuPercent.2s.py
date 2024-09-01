#!/usr/bin/env python3

# <xbar.title>CPU Percent</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display CPU % for user, system, and idle</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-CpuPercent.2s.py</xbar.abouturl>

from collections import namedtuple
from math import ceil
import subprocess
import time
from pprint import pprint

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_percent_stats_tuple(cpu='cpu-total', cpu_type=None, user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_percent = namedtuple('cpu_percent', 'cpu cpu_type user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_percent(cpu=cpu, cpu_type=cpu_type, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

def get_time_stats_tuple(cpu='cpu-total', cpu_type=None, user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_times = namedtuple('cpu_times', 'cpu cpu_type user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_times(cpu=cpu, cpu_type=cpu_type, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

def get_cpu_type():
    p = subprocess.Popen(
        ['/usr/sbin/sysctl', '-n', 'machdep.cpu.brand_string'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        return stdout.strip()
    else:
        return None

def cpu_time_deltas(t1, t2):
    return get_time_stats_tuple(
        user        = round(max(0, (t2.user - t1.user)), 2),
        system      = round(max(0, (t2.system - t1.system)), 2),
        idle        = round(max(0, (t2.idle - t1.idle)), 2),
        nice        = round(max(0, (t2.nice - t1.nice)), 2),
        iowait      = round(max(0, (t2.iowait - t1.iowait)), 2),
        irq         = round(max(0, (t2.irq - t1.irq)), 2),
        softirq     = round(max(0, (t2.softirq - t1.softirq)), 2),
        steal       = round(max(0, (t2.steal - t1.steal)), 2),
        guest       = round(max(0, (t2.guest - t1.guest)), 2),
        guestnice   = round(max(0, (t2.guestnice - t1.guestnice)), 2),
    )

def cpu_total_time(times_delta):
    return times_delta.user + times_delta.nice + times_delta.system + times_delta.idle

def calculate(t1, t2):
    times_delta = cpu_time_deltas(t1, t2)
    all_delta = cpu_total_time(times_delta)
    scale = 100.0 / max(1, all_delta)

    return get_percent_stats_tuple(
        cpu         = t1.cpu,
        cpu_type    = t1.cpu_type,
        user        = ceil(min(max(0.0, (times_delta.user * scale)), 100.0) * 100) / 100,
        system      = ceil(min(max(0.0, (times_delta.system * scale)), 100.0) * 100) / 100,
        idle        = ceil(min(max(0.0, (times_delta.idle * scale)), 100.0) * 100) / 100,
        nice        = ceil(min(max(0.0, (times_delta.nice * scale)), 100.0) * 100) / 100,
        iowait      = ceil(min(max(0.0, (times_delta.iowait * scale)), 100.0) * 100) / 100,
        irq         = ceil(min(max(0.0, (times_delta.irq * scale)), 100.0) * 100) / 100,
        softirq     = ceil(min(max(0.0, (times_delta.softirq * scale)), 100.0) * 100) / 100,
        steal       = ceil(min(max(0.0, (times_delta.steal * scale)), 100.0) * 100) / 100,
        guest       = ceil(min(max(0.0, (times_delta.guest * scale)), 100.0) * 100) / 100,
        guestnice   = ceil(min(max(0.0, (times_delta.guestnice * scale)), 100.0) * 100) / 100,
    )

def combine_stats(cpu_time_stats):
    idle      = 0.0
    nice      = 0.0
    system    = 0.0
    user      = 0.0

    for cpu_time_stat in cpu_time_stats:
        idle   += cpu_time_stat.idle
        nice   += cpu_time_stat.nice
        system += cpu_time_stat.system
        user   += cpu_time_stat.user
    return get_time_stats_tuple(idle=idle, nice=nice, system=system, user=user)

def gather_cpu_info():
    try:
        from psutil import cpu_times

        cpu_type = get_cpu_type()

        interval = 1.0
        blocking = False
        output_individual = []
        output_combined = []
        list_t1_individual = []
        list_t2_individual = []
        list_t1_combined = []
        list_t2_combined = []

        last_per_cpu_times = cpu_times(percpu=True)
        last_per_cpu_times2 = last_per_cpu_times

        if interval > 0.0:
            blocking = True

        if blocking:
            t1 = cpu_times(percpu=True)
            time.sleep(int(interval))
        else:
            t1 = last_per_cpu_times2
            if t1 is None:
                t1 = cpu_times(percpu=True)

        last_per_cpu_times2 = cpu_times(percpu=True)

        combined_t1 = combine_stats(t1)
        combined_t2 = combine_stats(last_per_cpu_times2)

        # Get the stats for the combined
        list_t1_combined.append(get_time_stats_tuple(cpu_type=cpu_type, user=combined_t1.user, system=combined_t1.system, nice=combined_t1.nice, idle=combined_t1.idle))
        list_t2_combined.append(get_time_stats_tuple(cpu_type=cpu_type, user=combined_t2.user, system=combined_t2.system, nice=combined_t2.nice, idle=combined_t2.idle))
        output_combined.append(calculate(list_t1_combined[0], list_t2_combined[0]))

        # Get the stats for the individual
        for i, cpu_instance in enumerate(t1):
            list_t1_individual.append(get_time_stats_tuple(cpu=i, cpu_type=cpu_type, user=cpu_instance.user, system=cpu_instance.system, nice=cpu_instance.nice, idle=cpu_instance.idle))
        for i, cpu_instance in enumerate(last_per_cpu_times2):
            list_t2_individual.append(get_time_stats_tuple(cpu=i, cpu_type=cpu_type, user=cpu_instance.user, system=cpu_instance.system, nice=cpu_instance.nice, idle=cpu_instance.idle))
        for i in range(len(t1)):
            output_individual.append(calculate(list_t1_individual[i], list_t2_individual[i]))

        return output_combined, output_individual, cpu_type

    except ModuleNotFoundError:
        print('Error: missing "psutil" library.')
        print('---')
        import sys
        import subprocess
        subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install psutil')
        print('Fix copied to clipboard. Paste on terminal and run.')

def main():
    output_combined, output_individual, cpu_type = gather_cpu_info()

    print(f'CPU: user {pad_float(output_combined[0].user)}%, sys {pad_float(output_combined[0].system)}%, idle {pad_float(output_combined[0].idle)}%')
    print('---')
    if cpu_type is not None:
        print(f'Processor: {cpu_type}')
    for cpu in output_individual:
        print(f'CPU {cpu.cpu}: user {cpu.user}%, sys {cpu.system}%, idle {cpu.idle}%')

if __name__ == '__main__':
    main()
