#!/usr/bin/env python3

import os
import subprocess
import libcalamares

# This module is important to the custom codebase, because other modules depend on it to add or remove packages as required. Any atomic operation with pacman shall take place in this module only.


# TODO:
# 1) refactor code - break up into functions - done
# 2) add functions for Packagechooser - done
# 3) add and sanitize variables for cpu_type and and write a function to remove specific microcode on the basis of cpu_type - done
# 4) add function to remove nvidia packages - port nvidia_removal from iso-profiles to here
# 5) remove packages from old packages module & rename currect packages to packages_alg
# 6) move get_cpu_type() to hardware module (needs testing, hence this function remains here until testing) - done
# 7) implement old nvidia_package_removal as failsafe, based on grub boot mode
# 8) modify remove_livecd_packages() to accomodate themed/pure values from GS, and remove packages accordingly
# 9) add function to remove packages from edition_chooser module

def remove_db_lock(install_path):
    """Remove pacman database lock file if it exists."""
    db_lock = os.path.join(install_path, "var/lib/pacman/db.lck")
    if os.path.exists(db_lock):
        with libcalamares.utils.raised_privileges():
            os.remove(db_lock)

def remove_cpu_microcode_packages():
    """Remove CPU microcode packages based on CPU vendor."""
    cpu_vendor = libcalamares.globalstorage.value("cpu_vendor")
    
    if not cpu_vendor:
        libcalamares.utils.warning("CPU vendor information not found in global storage")
        return

    try:
        if 'GenuineIntel' in cpu_vendor:
            libcalamares.utils.target_env_call(['pacman', '-Rns', '--noconfirm', 'amd-ucode'])
        elif 'AuthenticAMD' in cpu_vendor:
            libcalamares.utils.target_env_call(['pacman', '-Rns', '--noconfirm', 'intel-ucode'])
        else:
            libcalamares.utils.debug(f"Unknown CPU vendor: {cpu_vendor}")
    except Exception as e:
        libcalamares.utils.warning(f"Failed to remove microcode package: {e}")

def remove_firmware_packages():
    """Remove firmware packages based on boot type."""
    fw_type = libcalamares.globalstorage.value("firmwareType")
    
    if fw_type == 'bios':
        try:
            libcalamares.utils.target_env_call(
                ['pacman', '-Rns', '--noconfirm', 'efibootmgr', 'refind-efi']
            )
        except Exception as e:
            libcalamares.utils.warning(f"Failed to remove EFI packages: {e}")

def remove_nvidia_drivers():
    """Remove NVIDIA drivers based on boot mode and GPU detection."""
    kernel_boot_mode = libcalamares.globalstorage.value("kernel_boot_mode")
    
    if not kernel_boot_mode:
        libcalamares.utils.warning("No kernel_boot_mode found in global storage")
        return

    if kernel_boot_mode == "free":
        try:
            libcalamares.utils.target_env_call(
                ["pacman", "-Rns", "--noconfirm", "nvidia", "nvidia-utils", "nvidia-settings"]
            )
            libcalamares.utils.debug("NVIDIA drivers removed successfully")
        except Exception as e:
            libcalamares.utils.warning(f"Failed to remove NVIDIA drivers: {e}")
    
    elif kernel_boot_mode == "nonfree":
        try:
            with open("/usr/lib/modprobe.d/nvidia-utils.conf", "w") as f:
                f.write("blacklist nouveau\n")
            libcalamares.utils.debug("Nouveau driver blacklisted for NVIDIA")
        except IOError as e:
            libcalamares.utils.warning(f"Failed to blacklist nouveau: {e}")

def remove_livecd_packages():
    """Remove packages that are only needed in the live environment."""
    # Preserve the existing package list
    live_cd_packages = [
        "calamares", "boost", "solid", "yaml-cpp", "kpmcore",
        "hwinfo", "qt5-svg", "polkit-qt5", "plasma-framework",
        "qt5-xmlpatterns", "squashfs-tools", "linux-atm",
        "livecd-sounds", "alg-theme-cala-config",
        "mkinitcpio-archiso", "arch-install-scripts",
        "ckbcomp", "mkinitcpio-openswap"
    ]

    for pkg in live_cd_packages:
        try:
            libcalamares.utils.target_env_call(['pacman', '-Rns', '--noconfirm', pkg])
        except Exception as e:
            libcalamares.utils.warning(f"Could not remove package {pkg}: {e}")

def handle_packagechooser_packages():
    """Handle packages selected via PackageChooser module."""
    selected_packages = libcalamares.globalstorage.value("packagechooser_packages")
    
    if not selected_packages:
        return
    
    try:
        # Install selected packages
        libcalamares.utils.target_env_call(
            ['pacman', '-S', '--noconfirm'] + selected_packages
        )
    except Exception as e:
        libcalamares.utils.warning(f"Failed to install selected packages: {e}")

def run():
    """
    Main entry point for the packages module.
    Handles all package-related operations based on global storage values.
    """
    # Get install path
    install_path = libcalamares.globalstorage.value("rootMountPoint")
    
    if not install_path:
        return "No install path specified", False

    # Remove pacman db lock if it exists
    remove_db_lock(install_path)

    # Perform all package operations
    remove_cpu_microcode_packages()
    remove_firmware_packages()
    remove_nvidia_drivers()
    remove_livecd_packages()
    handle_packagechooser_packages()

    return None

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
