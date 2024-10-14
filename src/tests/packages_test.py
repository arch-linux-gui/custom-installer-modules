import unittest
from unittest.mock import patch, MagicMock
import libcalamares
import os

class TestCalamaresFunctions(unittest.TestCase):

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='vendor_id : GenuineIntel\n')
    def test_get_cpu_type_intel(self, mock_file):
        cpu_type = get_cpu_type()
        self.assertEqual(cpu_type, 'GenuineIntel')

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='vendor_id : AuthenticAMD\n')
    def test_get_cpu_type_amd(self, mock_file):
        cpu_type = get_cpu_type()
        self.assertEqual(cpu_type, 'AuthenticAMD')

    @patch('os.path.exists', return_value=True)
    @patch('misc.raised_privileges')
    @patch('os.remove')
    def test_remove_db_lock(self, mock_remove, mock_privileges, mock_exists):
        remove_db_lock('/fake/path')
        mock_remove.assert_called_once_with('/fake/path/var/lib/pacman/db.lck')

    @patch('libcalamares.utils.target_env_call')
    @patch('libcalamares.globalstorage.value', return_value='GenuineIntel')
    def test_remove_cpu_microcode_package_intel(self, mock_globalstorage, mock_target_env_call):
        remove_cpu_microcode_package()
        mock_target_env_call.assert_called_once_with(['pacman', '-Rns', '--noconfirm', 'amd-ucode'])

    @patch('libcalamares.utils.target_env_call')
    @patch('libcalamares.globalstorage.value', return_value='AuthenticAMD')
    def test_remove_cpu_microcode_package_amd(self, mock_globalstorage, mock_target_env_call):
        remove_cpu_microcode_package()
        mock_target_env_call.assert_called_once_with(['pacman', '-Rns', '--noconfirm', 'intel-ucode'])

    @patch('libcalamares.utils.target_env_call')
    @patch('libcalamares.globalstorage.value', return_value='unknown')
    def test_remove_cpu_microcode_package_unknown(self, mock_globalstorage, mock_target_env_call):
        remove_cpu_microcode_package()
        mock_target_env_call.assert_not_called()

    @patch('libcalamares.utils.target_env_call')
    @patch('libcalamares.globalstorage.value', return_value='bios')
    def test_remove_fw_packages_bios(self, mock_globalstorage, mock_target_env_call):
        remove_fw_packages()
        mock_target_env_call.assert_called_once_with(['pacman', '-Rns', '--noconfirm', 'efibootmgr', 'refind-efi'])

    @patch('libcalamares.utils.target_env_call')
    @patch('libcalamares.globalstorage.value', return_value='efi')
    def test_remove_fw_packages_efi(self, mock_globalstorage, mock_target_env_call):
        remove_fw_packages()
        mock_target_env_call.assert_not_called()

    @patch('libcalamares.globalstorage.value', return_value='NVIDIA Corporation Device [1234:5678]')
    @patch('libcalamares.utils.target_env_call')
    def test_remove_nvidia_packages_rtx(self, mock_target_env_call, mock_globalstorage):
        remove_nvidia_packages()
        # Assuming the NVIDIA RTX GPU is supported
        mock_target_env_call.assert_called_once_with(['pacman', '-S', '--noconfirm', 'nvidia-open'])

    @patch('libcalamares.globalstorage.value', return_value='NVIDIA Corporation Device [1234:5678]')
    @patch('libcalamares.utils.target_env_call')
    def test_remove_nvidia_packages_gtx(self, mock_target_env_call, mock_globalstorage):
        # Changing the mock return value to simulate a GTX GPU
        mock_globalstorage.return_value = 'GeForce GTX 1060'
        remove_nvidia_packages()
        mock_target_env_call.assert_called_once_with(['pacman', '-S', '--noconfirm', 'nvidia'])

    @patch('libcalamares.globalstorage.value', return_value='Some Other GPU')
    @patch('libcalamares.utils.target_env_call')
    def test_remove_nvidia_packages_none(self, mock_target_env_call, mock_globalstorage):
        remove_nvidia_packages()
        mock_target_env_call.assert_not_called()


if __name__ == '__main__':
    unittest.main()
