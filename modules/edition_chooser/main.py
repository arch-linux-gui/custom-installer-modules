#!/usr/bin/env python3

import os
import subprocess
import libcalamares

#NOTE: This module uses packagechooser as it's frontend. It also receives GS values from it.

# #TODO:
# 1) Based on packagechooser GS value, pass items to add/remove in packages_remover
# 2) Set env variables
# 3) Copy/Delete config files based on chosen edition (get_edition_version())
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
    pass

def set_system_theme():
    pass
