#!/usr/bin/env python3

import subprocess

import libcalamares

#TODO: Look for a way to only get nvidia gpu drivers

def get_nvidia_gpu_info():
    # Check for existance of an NVIDIA GPU
    try:
        lspci_output = subprocess.run("LANG=C lspci | grep -i nvidia",
                                      capture_output=True, shell=True, text=True, check=True)

        for line in lspci_output.stdout.split("\n"):
            if line.strip().startswith("01:00.0 VGA compatible controller"):
                nvidia_gpu_info.append(line.split(":")[1].strip())

        if not nvidia_gpu_info:
            libcalamares.utils.warning("No NVIDIA GPU information found.")

    except subprocess.CalledProcessError as cpe:
        libcalamares.utils.warning(f"Failed to get NVIDIA GPU information with error: {cpe.output}")
    except Exception as e:
        libcalamares.utils.warning(f"An unexpected error occurred: {e}")

    return nvidia_gpu_info


def get_gpu_driver_name():
    try:
        lspci_output = subprocess.run("LANG=C lspci -k | grep -EA3 'VGA|3D|Display'",
                                      capture_output=True, shell=True, text=True)

        for line in lspci_output.stdout.split("\n"):
            if line.strip().startswith("Kernel driver in use:"):
                gpu_drivers.append(line.split(":")[1].strip())

    except subprocess.CalledProcessError as cpe:
        libcalamares.utils.warning(f"Failed to get GPU drivers with error: {cpe.output}")
    except KeyError:
        libcalamares.utils.warning("Failed to parse GPU driver string")

def insert_value_in_cala_globalstorage():
    libcalamares.globalstorage.insert("nvidia_gpu_name", nvidia_gpu_info)
    libcalamares.globalstorage.insert("gpuDrivers", gpu_drivers)
