#!/usr/bin/env python3

import os
import subprocess
import libcalamares


# TODO:
# 1) refactor code - break up into functions
# 2) add functions for Packagechooser
# 3) add and sanitize variables for cpu_type and and write a function to remove specific microcode on the basis of cpu_type

def get_cpu_type():
    """Get the CPU type (Intel or AMD)."""
    cpu_info = {}
    with open('/proc/cpuinfo', 'r') as cpuinfo_file:
        for line in cpuinfo_file:
            if line.startswith('vendor_id'):
                cpu_info['vendor'] = line.split(':')[1].strip()
                break
    return cpu_info.get('vendor', 'Unknown')


def run():
    cpu_type = get_cpu_type()
    if 'GenuineIntel' in cpu_type:
        print("Intel CPU detected... removing amd microcode")
        libcalamares.utils.target_env_call(['pacman', '-Rns', '--noconfirm', 'amd-ucode'])

    elif 'AuthenticAMD' in cpu_type:
        print("AMD CPU detected... removing intel microcode")
        libcalamares.utils.target_env_call(['pacman', '-Rns', '--noconfirm', 'intel-ucode'])
    else:
        print("Unknown CPU type")

