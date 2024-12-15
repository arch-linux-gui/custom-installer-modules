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
# 2) Set env variables (desktop_version())- done
# 3) Check config files based on chosen edition (get_edition_version()) - done
# 4) Set configs (set_system_theme()) - done

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
    """
    Sets the system theme based on the chosen edition and desktop environment.
    Uses appropriate tools for each desktop environment.
    """
    desktop = desktop_version()
    edition = get_edition_version()
    theme_config = libcalamares.globalstorage.value("theme_config")
    
    if not theme_config:
        libcalamares.utils.warning("No theme configuration found in global storage")
        return
    
    try:
        if desktop == "kde":
            _set_kde_theme(edition, theme_config)
        elif desktop == "gnome":
            _set_gnome_theme(edition, theme_config)
        elif desktop == "xfce":
            _set_xfce_theme(edition, theme_config)
        else:
            libcalamares.utils.warning(f"Unsupported desktop environment: {desktop}")
    except Exception as e:
        libcalamares.utils.warning(f"Error setting system theme: {e}")

def _set_kde_theme(edition, theme_config):
    """Helper function to set KDE theme."""
    try:
        if edition == "pure":
            theme = "org.kde.breeze.desktop"
            if theme_config.get("dark", False):
                theme = "org.kde.breezedark.desktop"
            subprocess.run(["lookandfeeltool", "--apply", theme], check=True)
        else:
            style = "Qogirlight"
            window_decoration = "__aurorae__svg__Qogir-light-circle"
            if theme_config.get("dark", False):
                style = "Qogirdark"
                window_decoration = "__aurorae__svg__Qogir-dark-circle"
            
            home = os.getenv("HOME")
            cmd = f"plasma-apply-colorscheme {style} && kwriteconfig6 --file {home}/.config/kwinrc --group org.kde.kdecoration2 --key theme {window_decoration} && qdbus6 org.kde.KWin /KWin reconfigure"
            subprocess.run(["sh", "-c", cmd], check=True)
    except subprocess.CalledProcessError as e:
        libcalamares.utils.warning(f"Error setting KDE theme: {e}")

def _set_gnome_theme(edition, theme_config):
    """Helper function to set GNOME theme."""
    try:
        if edition == "pure":
            style = "prefer-dark" if theme_config.get("dark", False) else "prefer-light"
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", style], check=True)
        else:
            style = "prefer-dark" if theme_config.get("dark", False) else "prefer-light"
            shell = "Orchis-Red-Dark" if theme_config.get("dark", False) else "Orchis-Light"
            cmd = f"gsettings set org.gnome.desktop.interface color-scheme {style} && gsettings set org.gnome.shell.extensions.user-theme name {shell}"
            subprocess.run(["sh", "-c", cmd], check=True)
    except subprocess.CalledProcessError as e:
        libcalamares.utils.warning(f"Error setting GNOME theme: {e}")

def _set_xfce_theme(edition, theme_config):
    """Helper function to set XFCE theme."""
    try:
        if edition == "pure":
            style = "Adwaita-dark" if theme_config.get("dark", False) else "Adwaita"
        else:
            style = "Qogir-Dark" if theme_config.get("dark", False) else "Qogir-Light"
        
        cmd = f"xfconf-query -c xsettings -p /Net/ThemeName -s {style} && xfconf-query -c xfwm4 -p /general/theme -s {style}"
        subprocess.run(["sh", "-c", cmd], check=True)
    except subprocess.CalledProcessError as e:
        libcalamares.utils.warning(f"Error setting XFCE theme: {e}")

def run():
    """
    Main entry point for the edition chooser module.
    Sets up the system according to the chosen edition.
    """
    # Get current desktop environment
    desktop = desktop_version()
    if not desktop:
        return "Failed to determine desktop environment", False

    # Get edition type
    edition = get_edition_version()
    libcalamares.utils.debug(f"Detected desktop: {desktop}, edition: {edition}")

    # Store values in global storage for other modules
    libcalamares.globalstorage.insert("desktop_environment", desktop)
    libcalamares.globalstorage.insert("edition_type", edition)

    # Set system theme
    try:
        set_system_theme()
    except Exception as e:
        return f"Failed to set system theme: {e}", False

    return None