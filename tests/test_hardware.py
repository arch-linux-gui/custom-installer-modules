#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock, mock_open
import subprocess
from pathlib import Path
import sys

# Add the parent directory to sys.path to import the module
sys.path.append(str(Path(__file__).parent.parent))
from modules.hardware.main import (
    get_nvidia_gpu_info,
    get_gpu_driver_name,
    get_cpu_type,
    get_iso_bootmode,
    run
)

class TestHardwareDetection(unittest.TestCase):
    def setUp(self):
        # Mock libcalamares
        self.libcalamares_patcher = patch('modules.hardware.main.libcalamares')
        self.mock_libcalamares = self.libcalamares_patcher.start()
        
        # Create a mock for globalstorage
        self.mock_gs = MagicMock()
        self.mock_libcalamares.globalstorage = self.mock_gs

    def tearDown(self):
        self.libcalamares_patcher.stop()

    @patch('subprocess.run')
    def test_get_nvidia_gpu_info_with_gpu(self, mock_run):
        """Test NVIDIA GPU detection when GPU is present"""
        mock_run.return_value.stdout = (
            "01:00.0 VGA compatible controller: NVIDIA Corporation GA104 [GeForce RTX 3070] (rev a1)\n"
            "02:00.0 Audio device: NVIDIA Corporation Device 228b (rev a1)"
        )
        expected_result = ['NVIDIA Corporation GA104 [GeForce RTX 3070] (rev a1)']
        self.assertEqual(get_nvidia_gpu_info(), expected_result)

    @patch('subprocess.run')
    def test_get_nvidia_gpu_info_no_gpu(self, mock_run):
        """Test NVIDIA GPU detection when no GPU is present"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'lspci')
        self.assertEqual(get_nvidia_gpu_info(), [])

    @patch('subprocess.run')
    def test_get_nvidia_gpu_info_error(self, mock_run):
        """Test NVIDIA GPU detection with unexpected error"""
        mock_run.side_effect = Exception("Unexpected error")
        self.assertEqual(get_nvidia_gpu_info(), [])

    @patch('subprocess.run')
    def test_get_gpu_driver_name_with_driver(self, mock_run):
        """Test GPU driver detection when driver is present"""
        mock_run.return_value.stdout = (
            "00:02.0 VGA compatible controller: Intel Corporation UHD Graphics 630\n"
            "\tKernel driver in use: i915\n"
            "\tKernel modules: i915\n"
            "01:00.0 VGA compatible controller: NVIDIA Corporation GA104 [GeForce RTX 3070]\n"
            "\tKernel driver in use: nvidia\n"
            "\tKernel modules: nvidia"
        )
        expected_result = ['i915', 'nvidia']
        self.assertEqual(get_gpu_driver_name(), expected_result)

    @patch('subprocess.run')
    def test_get_gpu_driver_name_no_driver(self, mock_run):
        """Test GPU driver detection when no driver is present"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'lspci')
        self.assertEqual(get_gpu_driver_name(), [])

    def test_get_cpu_type_intel(self):
        """Test CPU type detection for Intel CPU"""
        mock_data = (
            "processor\t: 0\n"
            "vendor_id\t: GenuineIntel\n"
            "cpu family\t: 6"
        )
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.assertEqual(get_cpu_type(), 'GenuineIntel')

    def test_get_cpu_type_amd(self):
        """Test CPU type detection for AMD CPU"""
        mock_data = (
            "processor\t: 0\n"
            "vendor_id\t: AuthenticAMD\n"
            "cpu family\t: 25"
        )
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.assertEqual(get_cpu_type(), 'AuthenticAMD')

    def test_get_cpu_type_error(self):
        """Test CPU type detection with file error"""
        with patch('builtins.open', side_effect=IOError):
            self.assertEqual(get_cpu_type(), 'Unknown')

    def test_get_iso_bootmode_with_param(self):
        """Test ISO boot mode detection with parameter"""
        mock_data = "BOOT_IMAGE=/boot/vmlinuz-linux root=UUID=xxx ro driver=nonfree quiet splash"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.assertEqual(get_iso_bootmode("driver", "free"), "nonfree")

    def test_get_iso_bootmode_no_param(self):
        """Test ISO boot mode detection without parameter"""
        mock_data = "BOOT_IMAGE=/boot/vmlinuz-linux root=UUID=xxx ro quiet splash"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.assertEqual(get_iso_bootmode("driver", "free"), "free")

    def test_get_iso_bootmode_error(self):
        """Test ISO boot mode detection with file error"""
        with patch('builtins.open', side_effect=IOError):
            self.assertEqual(get_iso_bootmode("driver", "free"), "free")

class TestHardwareDetectionRun(unittest.TestCase):
    """Test the main run function of the hardware detection module"""

    def setUp(self):
        self.libcalamares_patcher = patch('modules.hardware.main.libcalamares')
        self.mock_libcalamares = self.libcalamares_patcher.start()
        self.mock_gs = MagicMock()
        self.mock_libcalamares.globalstorage = self.mock_gs

    def tearDown(self):
        self.libcalamares_patcher.stop()

    @patch('modules.hardware.main.get_nvidia_gpu_info')
    @patch('modules.hardware.main.get_gpu_driver_name')
    @patch('modules.hardware.main.get_cpu_type')
    @patch('modules.hardware.main.get_iso_bootmode')
    def test_run_successful(self, mock_bootmode, mock_cpu, mock_gpu_driver, mock_nvidia):
        """Test successful run with all components"""
        # Setup mock returns
        mock_nvidia.return_value = ['NVIDIA GeForce RTX 3070']
        mock_gpu_driver.return_value = ['nvidia']
        mock_cpu.return_value = 'GenuineIntel'
        mock_bootmode.return_value = 'nonfree'

        # Run the function
        result = run()

        # Verify the result
        self.assertIsNone(result)

        # Verify global storage insertions
        self.mock_gs.insert.assert_any_call("nvidia_gpu_name", ['NVIDIA GeForce RTX 3070'])
        self.mock_gs.insert.assert_any_call("gpuDrivers", ['nvidia'])
        self.mock_gs.insert.assert_any_call("cpu_vendor", 'GenuineIntel')
        self.mock_gs.insert.assert_any_call("kernel_boot_mode", 'nonfree')

    @patch('modules.hardware.main.get_nvidia_gpu_info')
    @patch('modules.hardware.main.get_gpu_driver_name')
    @patch('modules.hardware.main.get_cpu_type')
    @patch('modules.hardware.main.get_iso_bootmode')
    def test_run_with_no_nvidia(self, mock_bootmode, mock_cpu, mock_gpu_driver, mock_nvidia):
        """Test run without NVIDIA GPU"""
        mock_nvidia.return_value = []
        mock_gpu_driver.return_value = ['i915']
        mock_cpu.return_value = 'GenuineIntel'
        mock_bootmode.return_value = 'free'

        result = run()

        self.assertIsNone(result)
        self.mock_gs.insert.assert_any_call("nvidia_gpu_name", [])
        self.mock_gs.insert.assert_any_call("gpuDrivers", ['i915'])

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        self.libcalamares_patcher = patch('modules.hardware.main.libcalamares')
        self.mock_libcalamares = self.libcalamares_patcher.start()

    def tearDown(self):
        self.libcalamares_patcher.stop()

    @patch('subprocess.run')
    def test_nvidia_gpu_info_malformed_output(self, mock_run):
        """Test NVIDIA GPU detection with malformed lspci output"""
        mock_run.return_value.stdout = "malformed:output:without:expected:format"
        self.assertEqual(get_nvidia_gpu_info(), [])

    @patch('subprocess.run')
    def test_gpu_driver_name_empty_output(self, mock_run):
        """Test GPU driver detection with empty output"""
        mock_run.return_value.stdout = ""
        self.assertEqual(get_gpu_driver_name(), [])

    def test_cpu_type_malformed_file(self):
        """Test CPU type detection with malformed cpuinfo file"""
        mock_data = "malformed\nfile\ncontent"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.assertEqual(get_cpu_type(), 'Unknown')

    def test_iso_bootmode_malformed_cmdline(self):
        """Test ISO boot mode detection with malformed cmdline"""
        mock_data = "malformed=content=with=multiple=equals"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            self.assertEqual(get_iso_bootmode("driver", "free"), "free")

if __name__ == '__main__':
    unittest.main()