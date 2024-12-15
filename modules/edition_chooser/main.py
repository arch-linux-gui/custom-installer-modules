#!/usr/bin/env python3

"""
ALG Custom Install Module - Edition Chooser
This file is part of the ALG project and is
meant to be shipped with calamares.
"""

import os
import subprocess
import libcalamares

#NOTE: This module uses packagechooser as it's frontend. It also receives GS values from it.

# #TODO:
# 1) Based on packagechooser GS value, pass items to add/remove in packages_remover
# 2) Set env variables
# 3) Check config files based on chosen edition (get_edition_version()) - done
# 4) Set configs (set_system_theme())

def desktop_version():
    """
    Determines the current desktop environment.
    Returns 'kde', 'gnome', 'xfce', or None.
    """
    try:
        desktop_env = os.getenv('XDG_CURRENT_DESKTOP', '').lower()
        if desktop_env in ['kde', 'gnome', 'xfce']:
            return desktop_env
        libcalamares.utils.warning(f"Unsupported desktop environment: {desktop_env}")
        return None
    except Exception as e:
        libcalamares.utils.warning(f"Error determining desktop version: {e}")
        return None


def get_edition_version():
    """
    Determines if the system edition is 'pure' or 'themed'.
    Returns the edition type based on the current theme configuration.
    """
    desktop = desktop_version()
    
    try:
        if desktop == "kde":
            # Check KDE theme
            return _get_kde_edition()
        elif desktop == "gnome":
            # Check GNOME theme
            return _get_gnome_edition()
        elif desktop == "xfce":
            # Check XFCE theme
            return _get_xfce_edition()
        else:
            libcalamares.utils.warning(f"Unsupported desktop environment: {desktop}")
            return "pure"  # Default to pure edition
    except Exception as e:
        libcalamares.utils.warning(f"Error determining edition version: {e}")
        return "pure"  # Default to pure edition on error

def _get_kde_edition():
    """Helper function to determine KDE edition type."""
    try:
        # Check for breeze themes
        config_files = [
            os.path.expandvars("$HOME/.config/kdeglobals"),
            os.path.expandvars("$HOME/.kde4/share/config/kdeglobals"),
            "/etc/kde/kdeglobals"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    if "org.kde.breeze" in content:
                        return "pure"
                    elif "Qogir" in content:
                        return "themed"
        
        return "pure"  # Default if no specific theme is found
    except Exception as e:
        libcalamares.utils.warning(f"Error checking KDE theme: {e}")
        return "pure"

def _get_gnome_edition():
    """Helper function to determine GNOME edition type."""
    try:
        # Check shell theme
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.shell.extensions.user-theme", "name"],
            capture_output=True, text=True
        )
        
        if "Orchis" in result.stdout:
            return "themed"
        return "pure"
    except Exception as e:
        libcalamares.utils.warning(f"Error checking GNOME theme: {e}")
        return "pure"

def _get_xfce_edition():
    """Helper function to determine XFCE edition type."""
    try:
        result = subprocess.run(
            ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"],
            capture_output=True, text=True
        )
        
        if "Qogir" in result.stdout:
            return "themed"
        return "pure"
    except Exception as e:
        libcalamares.utils.warning(f"Error checking XFCE theme: {e}")
        return "pure"

def set_system_theme():
    pass
