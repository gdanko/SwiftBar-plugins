#!/usr/bin/env python3

# <xbar.title>CPU Percent</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Display CPU % for user, system, and idle</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/System/gdanko-system-CpuPercent.5s.py</xbar.abouturl>

from collections import namedtuple
from math import ceil
import time

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_percent_stats_tuple(cpu='cpu-total', user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_percent = namedtuple('cpu_percent', 'cpu user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_percent(cpu=cpu, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

def get_time_stats_tuple(cpu='cpu-total', user=0.0, system=0.0, idle=0.0, nice=0.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guestnice=0.0):
    cpu_times = namedtuple('cpu_times', 'cpu user system idle nice iowait irq softirq steal guest guestnice')
    return cpu_times(cpu=cpu, user=user, system=system, idle=idle, nice=nice, iowait=iowait, irq=irq, softirq=softirq, steal=steal, guest=guest, guestnice=guestnice)

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

def main(percpu=False):
    try:
        from psutil import cpu_times

        percpu = False
        blocking = False
        interval = 1.0
        output = []
        list_t1 = []
        list_t2 = []

        last_cpu_times = cpu_times(percpu=False)
        last_per_cpu_times = cpu_times(percpu=True)
        last_per_cpu_times2 = last_cpu_times

        if interval > 0.0:
            blocking = True

        if not percpu:
            if blocking:
                t1 = cpu_times(percpu=False)
                time.sleep(int(interval))
            else:
                t1 = last_per_cpu_times2
                if t1 is None:
                    t1 = cpu_times(percpu=False)
            last_per_cpu_times2 = cpu_times(percpu=False)

            list_t1.append(get_time_stats_tuple(user=t1.user, system=t1.system, nice=t1.nice, idle=t1.idle))
            list_t2.append(get_time_stats_tuple(user=last_per_cpu_times2.user, system=last_per_cpu_times2.system, nice=last_per_cpu_times2.nice, idle=last_per_cpu_times2.idle))

            output.append(calculate(list_t1[0], list_t2[0]))
            print(f'CPU: user {pad_float(output[0].user)}%, sys {pad_float(output[0].system)}%, idle {pad_float(output[0].idle)}%')
        else:
            if blocking:
                t1 = cpu_times(percpu=True)
                time.sleep(int(interval))
            else:
                t1 = last_per_cpu_times2
                if t1 is None:
                    t1 = cpu_times(percpu=True)
            last_per_cpu_times2 = cpu_times(percpu=True)

            for i, cpu_instance in enumerate(t1):
                list_t1.append(get_time_stats_tuple(cpu=i, user=cpu_instance.user, system=cpu_instance.system, nice=cpu_instance.nice, idle=cpu_instance.idle))

            for i, cpu_instance in enumerate(last_per_cpu_times2):
                list_t2.append(get_time_stats_tuple(cpu=i, user=cpu_instance.user, system=cpu_instance.system, nice=cpu_instance.nice, idle=cpu_instance.idle))

            for i in range(len(t1)):
                output.append(calculate(list_t1[i], list_t2[i]))
    
    except ModuleNotFoundError:
        print('Error: missing "psutil" library.')
        print('---')
        import sys
        import subprocess
        subprocess.run('pbcopy', universal_newlines=True,
                       input=f'{sys.executable} -m pip install psutil')
        print('Fix copied to clipboard. Paste on terminal and run.')

if __name__ == '__main__':
    main()
