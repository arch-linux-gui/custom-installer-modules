#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import os
import subprocess
from pathlib import Path
import sys

# Add the parent directory to sys.path to import the module
sys.path.append(str(Path(__file__).parent.parent))
from modules.editionchooser.main import (
    desktop_version,
    get_edition_version,
    _get_kde_edition,
    _get_gnome_edition,
    _get_xfce_edition,
    set_system_theme,
    run
)

class TestEditionChooser(unittest.TestCase):
    def setUp(self):
        # Mock libcalamares
        self.libcalamares_patcher = patch('modules.editionchooser.main.libcalamares')
        self.mock_libcalamares = self.libcalamares_patcher.start()
        
        # Create a mock for globalstorage
        self.mock_gs = MagicMock()
        self.mock_libcalamares.globalstorage = self.mock_gs

    def tearDown(self):
        self.libcalamares_patcher.stop()

    def test_desktop_version_kde(self):
        """Test KDE desktop detection"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'KDE'}):
            self.assertEqual(desktop_version(), 'kde')

    def test_desktop_version_gnome(self):
        """Test GNOME desktop detection"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'GNOME'}):
            self.assertEqual(desktop_version(), 'gnome')

    def test_desktop_version_xfce(self):
        """Test XFCE desktop detection"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'XFCE'}):
            self.assertEqual(desktop_version(), 'xfce')

    def test_desktop_version_unsupported(self):
        """Test unsupported desktop detection"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'UNKNOWN'}):
            self.assertIsNone(desktop_version())

    @patch('modules.editionchooser.main._get_kde_edition')
    def test_get_edition_version_kde(self, mock_kde_edition):
        """Test KDE edition detection"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'KDE'}):
            mock_kde_edition.return_value = 'pure'
            self.assertEqual(get_edition_version(), 'pure')
            mock_kde_edition.assert_called_once()

    def test_get_kde_edition_pure(self):
        """Test KDE pure edition detection"""
        mock_content = "[KDE]\nLookAndFeelPackage=org.kde.breeze.desktop"
        mock_open = unittest.mock.mock_open(read_data=mock_content)
        with patch('builtins.open', mock_open):
            with patch('os.path.exists', return_value=True):
                self.assertEqual(_get_kde_edition(), 'pure')

    def test_get_kde_edition_themed(self):
        """Test KDE themed edition detection"""
        mock_content = "[KDE]\nLookAndFeelPackage=Qogir-light"
        mock_open = unittest.mock.mock_open(read_data=mock_content)
        with patch('builtins.open', mock_open):
            with patch('os.path.exists', return_value=True):
                self.assertEqual(_get_kde_edition(), 'themed')

    @patch('subprocess.run')
    def test_get_gnome_edition_pure(self, mock_run):
        """Test GNOME pure edition detection"""
        mock_run.return_value.stdout = "'Adwaita'"
        self.assertEqual(_get_gnome_edition(), 'pure')

    @patch('subprocess.run')
    def test_get_gnome_edition_themed(self, mock_run):
        """Test GNOME themed edition detection"""
        mock_run.return_value.stdout = "'Orchis-Dark'"
        self.assertEqual(_get_gnome_edition(), 'themed')

    @patch('subprocess.run')
    def test_get_xfce_edition_pure(self, mock_run):
        """Test XFCE pure edition detection"""
        mock_run.return_value.stdout = "Adwaita"
        self.assertEqual(_get_xfce_edition(), 'pure')

    @patch('subprocess.run')
    def test_get_xfce_edition_themed(self, mock_run):
        """Test XFCE themed edition detection"""
        mock_run.return_value.stdout = "Qogir-Dark"
        self.assertEqual(_get_xfce_edition(), 'themed')

    @patch('subprocess.run')
    def test_set_kde_theme_pure(self, mock_run):
        """Test setting KDE pure theme"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'KDE', 'HOME': '/home/test'}):
            self.mock_gs.value.return_value = {'dark': False}
            set_system_theme()
            mock_run.assert_called()

    @patch('subprocess.run')
    def test_set_gnome_theme_pure(self, mock_run):
        """Test setting GNOME pure theme"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'GNOME'}):
            self.mock_gs.value.return_value = {'dark': False}
            set_system_theme()
            mock_run.assert_called()

    @patch('subprocess.run')
    def test_set_xfce_theme_pure(self, mock_run):
        """Test setting XFCE pure theme"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'XFCE'}):
            self.mock_gs.value.return_value = {'dark': False}
            set_system_theme()
            mock_run.assert_called()

    def test_run_successful(self):
        """Test successful run of the module"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'KDE'}):
            with patch('modules.editionchooser.main.set_system_theme'):
                result = run()
                self.assertIsNone(result)
                self.mock_gs.insert.assert_called()

    def test_run_desktop_detection_failure(self):
        """Test run with desktop detection failure"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'UNKNOWN'}):
            result, success = run()
            self.assertFalse(success)
            self.assertIn("Failed to determine desktop environment", result)

    def test_run_theme_setting_failure(self):
        """Test run with theme setting failure"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'KDE'}):
            with patch('modules.editionchooser.main.set_system_theme', 
                      side_effect=Exception("Theme setting failed")):
                result, success = run()
                self.assertFalse(success)
                self.assertIn("Failed to set system theme", result)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        self.libcalamares_patcher = patch('modules.editionchooser.main.libcalamares')
        self.mock_libcalamares = self.libcalamares_patcher.start()

    def tearDown(self):
        self.libcalamares_patcher.stop()

    def test_desktop_version_empty_env(self):
        """Test behavior with empty desktop environment variable"""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': ''}, clear=True):
            self.assertIsNone(desktop_version())

    def test_kde_edition_no_config_files(self):
        """Test KDE edition detection with no config files"""
        with patch('os.path.exists', return_value=False):
            self.assertEqual(_get_kde_edition(), 'pure')

    @patch('subprocess.run')
    def test_gnome_edition_command_failure(self, mock_run):
        """Test GNOME edition detection with command failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'gsettings')
        self.assertEqual(_get_gnome_edition(), 'pure')

    @patch('subprocess.run')
    def test_xfce_edition_command_failure(self, mock_run):
        """Test XFCE edition detection with command failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'xfconf-query')
        self.assertEqual(_get_xfce_edition(), 'pure')

if __name__ == '__main__':
    unittest.main()