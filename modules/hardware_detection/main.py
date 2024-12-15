#!/usr/bin/env python3

"""
ALG Custom Install Module - Hardware Detection
This file is part of the ALG project and is
meant to be shipped with calamares.
"""

import subprocess
import libcalamares

def get_nvidia_gpu_info():
    """
    Detects NVIDIA GPU and returns its information.
    Sets empty list if no NVIDIA GPU is found.
    """
    nvidia_gpu_info = []
    try:
        lspci_output = subprocess.run(
            "LANG=C lspci | grep -i nvidia",
            capture_output=True, shell=True, text=True, check=True
        )

        for line in lspci_output.stdout.split("\n"):
            if line.strip().startswith("01:00.0 VGA compatible controller"):
                nvidia_gpu_info.append(line.split(":")[1].strip())

        if not nvidia_gpu_info:
            libcalamares.utils.debug("No NVIDIA GPU information found.")

    except subprocess.CalledProcessError:
        libcalamares.utils.debug("No NVIDIA GPU detected")
    except Exception as e:
        libcalamares.utils.warning(f"An unexpected error occurred while detecting NVIDIA GPU: {e}")

    return nvidia_gpu_info

def get_gpu_driver_name():
    """
    Detects current GPU drivers in use.
    Returns a list of active GPU drivers.
    """
    gpu_drivers = []
    try:
        lspci_output = subprocess.run(
            "LANG=C lspci -k | grep -EA3 'VGA|3D|Display'",
            capture_output=True, shell=True, text=True
        )

        for line in lspci_output.stdout.split("\n"):
            if line.strip().startswith("Kernel driver in use:"):
                gpu_drivers.append(line.split(":")[1].strip())

    except subprocess.CalledProcessError as cpe:
        libcalamares.utils.warning(f"Failed to get GPU drivers with error: {cpe.output}")
    except Exception as e:
        libcalamares.utils.warning(f"Failed to parse GPU driver information: {e}")

    return gpu_drivers

def get_cpu_type():
    """
    Detects CPU vendor (Intel/AMD).
    Returns the CPU vendor ID string.
    """
    try:
        with open('/proc/cpuinfo', 'r') as cpuinfo_file:
            for line in cpuinfo_file:
                if line.startswith('vendor_id'):
                    return line.split(':')[1].strip()
    except Exception as e:
        libcalamares.utils.warning(f"Failed to detect CPU type: {e}")
        return "Unknown"
    
    return "Unknown"

def get_iso_bootmode(param, default=None):
    """
    Reads kernel boot parameters from /proc/cmdline
    Returns the value of the specified parameter or default if not found
    """
    try:
        with open("/proc/cmdline", "r") as kernel_boot_mode:
            for cmd_param in kernel_boot_mode.read().split():
                if cmd_param.startswith(f"{param}="):
                    return cmd_param.split("=")[1]
                elif cmd_param == param:
                    return param
    except Exception as e:
        libcalamares.utils.warning(f"Failed to read kernel boot mode: {e}")
        return default
    
    return default

def run():
    """
    Main entry point for the hardware detection module.
    Detects hardware configurations and stores them in global storage.
    """
    # Detect hardware information
    nvidia_info = get_nvidia_gpu_info()
    gpu_drivers = get_gpu_driver_name()
    cpu_type = get_cpu_type()
    kernel_boot_mode = get_iso_bootmode("driver", "free")  # default to free drivers

    # Store all hardware information in global storage
    gs = libcalamares.globalstorage
    gs.insert("nvidia_gpu_name", nvidia_info)
    gs.insert("gpuDrivers", gpu_drivers)
    gs.insert("kernel_boot_mode", kernel_boot_mode)
    gs.insert("cpu_vendor", cpu_type)

    # Log detected hardware information
    libcalamares.utils.debug(f"Detected CPU vendor: {cpu_type}")
    libcalamares.utils.debug(f"Detected GPU drivers: {gpu_drivers}")
    libcalamares.utils.debug(f"Detected NVIDIA GPU: {nvidia_info}")
    libcalamares.utils.debug(f"Kernel boot mode: {kernel_boot_mode}")

    return None