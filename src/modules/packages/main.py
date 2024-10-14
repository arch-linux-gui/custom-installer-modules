#!/usr/bin/env python3

import os
import subprocess
import libcalamares


# TODO:
# 1) refactor code - break up into functions - done
# 2) add functions for Packagechooser
# 3) add and sanitize variables for cpu_type and and write a function to remove specific microcode on the basis of cpu_type - done
# 4) add function to remove nvidia packages - port nvidia_removal from iso-profiles to here
# 5) remove packages from old packages module & rename currect packages to packages_alg
# 6) move get_cpu_type() to hardware module (needs testing, hence this function remains here until testing)

def get_cpu_type():
    # Get the CPU type (Intel or AMD).
    cpu_info = {}
    with open('/proc/cpuinfo', 'r') as cpuinfo_file:
        for line in cpuinfo_file:
            if line.startswith('vendor_id'):
                cpu_info['vendor'] = line.split(':')[1].strip()
                break
    return cpu_info.get('vendor', 'Unknown')

def remove_db_lock(install_path):
    # Remove database lock file if it exists.
    db_lock = os.path.join(install_path, "var/lib/pacman/db.lck")
    if os.path.exists(db_lock):
        with misc.raised_privileges():
            os.remove(db_lock)

def remove_cpu_microcode_package():
    # Remove microcode packages
    if 'GenuineIntel' in cpu_type:
        print("Intel CPU detected... removing AMD microcode")
        try:
            libcalamares.utils.target_env_call(['pacman', '-Rns', '--noconfirm', 'amd-ucode'])
        except Exception as e:
            print(f"Failed to remove AMD microcode: {e}")

    elif 'AuthenticAMD' in cpu_type:
        print("AMD CPU detected... removing Intel microcode")
        try:
            libcalamares.utils.target_env_call(['pacman', '-Rns', '--noconfirm', 'intel-ucode'])
        except Exception as e:
            print(f"Failed to remove Intel microcode: {e}")
    else:
        print("Unknown CPU type")

def remove_fw_packages():
    fw_type = libcalamares.globalstorage.value("firmwareType")
    if fw_type == 'bios':
        print('Removing EFI packages')
        libcalamares.utils.target_env_call(
            ['pacman', '-Rns', '--noconfirm', 'efibootmgr', 'refind-efi'])

def remove_livecd_packages():
    print("Removing live ISO packages")
    live_cd_packages = ["calamares",
                        "boost",
                        "solid",
                        "yaml-cpp",
                        "kpmcore",
                        "hwinfo",
                        "qt5-svg",
                        "polkit-qt5",
                        "plasma-framework",
                        "qt5-xmlpatterns",
                        "squashfs-tools",
                        "linux-atm",
                        "livecd-sounds",
                        "alg-theme-cala-config",
                        "mkinitcpio-archiso",
                        "arch-install-scripts",
                        "ckbcomp",
                        "mkinitcpio-openswap"]
    for pkg in live_cd_packages:
            try:
                libcalamares.utils.target_env_call(
                    ['pacman', '-Rns', '--noconfirm', '{!s}' .format(pkg)])
            except:
                print("Could not remove package " + pkg)

    print('Live CD packages removed')



# TODO: 4
# def remove_nvidia_packages():
#     supported_nvidia_gpus_rtx = (
#     "GeForce RTX 2060, "
#     "GeForce RTX 2060 Super, "
#     "GeForce RTX 2070, "
#     "GeForce RTX 2070 Super, "
#     "GeForce RTX 2080, "
#     "GeForce RTX 2080 Super, "
#     "GeForce RTX 2080 Ti, "
#     "GeForce GTX 1660, "
#     "GeForce GTX 1660 Ti, "
#     "GeForce GTX 1660 Super, "
#     "GeForce RTX 3060, "
#     "GeForce RTX 3060 Ti, "
#     "GeForce RTX 3070, "
#     "GeForce RTX 3070 Ti, "
#     "GeForce RTX 3080, "
#     "GeForce RTX 3080 Ti, "
#     "GeForce RTX 3090, "
#     "GeForce RTX 4060, "
#     "GeForce RTX 4060 Ti, "
#     "GeForce RTX 4070, "
#     "GeForce RTX 4070 Ti, "
#     "GeForce RTX 4080, "
#     "GeForce RTX 4090")
#
#     supported_nvidia_gpus_gtx = (
#     "GeForce GTX 750, "
#     "GeForce GTX 750 Ti, "
#     "GeForce GTX 760, "
#     "GeForce GTX 770, "
#     "GeForce GTX 780, "
#     "GeForce GTX 780 Ti, "
#     "GeForce GTX 850M, "
#     "GeForce GTX 860M, "
#     "GeForce GTX 870M, "
#     "GeForce GTX 880M, "
#     "GeForce GTX 950, "
#     "GeForce GTX 960, "
#     "GeForce GTX 970, "
#     "GeForce GTX 980, "
#     "GeForce GTX 980 Ti, "
#     "GeForce GTX 1050, "
#     "GeForce GTX 1050 Ti, "
#     "GeForce GTX 1060, "
#     "GeForce GTX 1070, "
#     "GeForce GTX 1070 Ti, "
#     "GeForce GTX 1080, "
#     "GeForce GTX 1080 Ti")
#
#     nvidia_gpu_info = libcalamares.globalstorage.value("nvidia_gpu_name")
#
#      if "NVIDIA" in nvidia_gpu_info and any(gpu in nvidia_gpu_info for gpu in supported_nvidia_gpus_rtx.split(", ")):
#         try:
#             libcalamares.utils.target_env_call(['pacman', '-S', '--noconfirm', 'nvidia-open'])
#             print("nvidia-open package installed successfully.")
#         except Exception as e:
#             libcalamares.utils.warning(f"Failed to install nvidia-open: {e}")
#
#     elif "NVIDIA" in nvidia_gpu_info and any(gpu in nvidia_gpu_info for gpu in supported_nvidia_gpus_gtx.split(", ")):
#         try:
#             libcalamares.utils.target_env_call(['pacman', '-S', '--noconfirm', 'nvidia'])
#             print("nvidia package installed successfully.")
#         except Exception as e:
#             libcalamares.utils.warning(f"Failed to install nvidia: {e}")
#     else:
#         print("No supported NVIDIA GPU detected. Skipping installation of NVIDIA drivers.")
