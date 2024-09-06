#!/usr/bin/env python3

# from macholib import mach_o, MachO
# from pprint import pprint
# from macholib.mach_o import (CPU_TYPE_NAMES, MH_CIGAM_64, MH_MAGIC_64, get_cpu_subtype)
# from macholib.MachO import MachO
# import platform

import subprocess
from collections import namedtuple
from pprint import pprint
from psutil import cpu_freq

CPU_FAMILY_NAMES = {
    0xcee41549: 'PowerPC G3',
    0x77c184ae: 'PowerPC G4',
    0xed76d8aa: 'PowerPC G5',
    0xaa33392b: 'Intel 6_13',
    0x78ea4fbc: 'Intel Penryn',
    0x6b5a4cd2: 'Intel Nehalem',
    0x573b5eec: 'Intel Westmere',
    0x5490b78c: 'Intel Sandybridge',
    0x1f65e835: 'Intel Ivybridge',
    0x10b282dc: 'Intel Haswell',
    0x582ed09c: 'Intel Broadwell',
    0x37fc219f: 'Intel Skylake',
    0x0f817246: 'Intel Kabylake',
    0x38435547: 'Intel Icelake',
    0x1cf8a03e: 'Intel Cometlake',
    0xe73283ae: 'ARM9',
    0x8ff620d8: 'ARM11',
    0x53b005f5: 'ARM XScale',
    0xbd1b0ae9: 'ARM12',
    0x0cc90e64: 'ARM13',
    0x96077ef1: 'ARM14',
    0xa8511bca: 'ARM15',
    0x1e2d6381: 'ARM Swift',
    0x37a09642: 'ARM Cyclone',
    0x2c91a47e: 'ARM Typhoon',
    0x92fb37c8: 'ARM Twister',
    0x67ceee93: 'ARM Hurricane',
    0xe81e7ef6: 'ARM Monsoon Mistral',
    0x07d34b9f: 'ARM Vortex Tempest',
    0x462504d2: 'ARM Lightning Thunder',
    0x1b588bb3: 'ARM Firestorm Icestorm',
    0xda33d83d: 'ARM Blizzard Avalanche',
    0x8765edea: 'ARM Everest Sawtooth',
    0xfa33415e: 'ARM Ibiza',
    0x72015832: 'ARM Palma',
    0x2876f5b5: 'ARM Coll',
    0x5f4dea93: 'ARM Lobos',
}

def cpu_info():
    output = {}
    metrics = {
        'cores': 'machdep.cpu.core_count',
        'family': 'hw.cpufamily',
        'l1_data_cache_bytes': 'hw.l1dcachesize',
        'l1_instruction_cache_bytes': 'hw.l1icachesize',
        'l2_cache_bytes': 'hw.l2cachesize',
        'model': 'machdep.cpu.brand_string',
        'sub_family': 'hw.cpusubfamily',

    }
    for metric in metrics:
        p = subprocess.Popen(
            ['/usr/sbin/sysctl', '-n', metrics[metric]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, _ = p.communicate()
        
        if p.returncode == 0:
            stdout = stdout.strip()
            if metric == 'family':
                output[metric] = CPU_FAMILY_NAMES.get(int(stdout), int(stdout))
            elif metric in ['cores', 'l1_data_cache_bytes', 'l1_instruction_cache_bytes', 'l2_cache_bytes', 'sub_family'] :
                output[metric] = int(stdout)
            else:
                output[metric] = stdout
    output['current_frequency'] = cpu_freq().current if cpu_freq().current is not None else 0
    output['min_frequency'] = cpu_freq().min if cpu_freq().min is not None else 0
    output['max_frequency'] = cpu_freq().max if cpu_freq().max is not None else 0
    return output

foo = cpu_info()
pprint(foo)


# def get_bin_info1(platform_arch, bin_file, family):
#     m = MachO(bin_file)
#     for header in m.headers:
#         print(header.header.cputype)
#         if header.MH_MAGIC == MH_MAGIC_64 or header.MH_MAGIC == MH_CIGAM_64:
#             sz = '64-bit'
#         else:
#             sz = '32-bit'
#         arch = CPU_TYPE_NAMES2.get(header.header.cputype, header.header.cputype).lower()
#         subarch = get_cpu_subtype(header.header.cputype, header.header.cpusubtype)
#         cpu_family = CPU_FAMILY_NAMES.get(family, family)
#         if arch == platform_arch:
            
#             return {'endian': header.endian,
#                     'family': cpu_family,
#                     'bit': sz,
#                     'arch': arch,
#                     'subarch': subarch}
#     return None

# family = 458787763
# # hex_family = hex(family)
# # print(hex_family)
# # print(CPU_FAMILY_NAMES[hex_family])
# # exit()
# platform_arch = 'arm64'
# path = '/usr/bin/grep'
# bin_info = get_bin_info1(platform_arch, path, family)
# pprint(bin_info)
