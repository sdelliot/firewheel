from unittest.mock import Mock, patch

import pytest

from firewheel.vm_resource_manager.vm_resource_handler import VMResourceHandler


@pytest.fixture
def mock_config():
    return {"vm_name": "test_name", "path": "test/path"}


@pytest.fixture
def vmr_handler(mock_config):
    with patch("firewheel.vm_resource_manager.vm_resource_handler.time"), patch(
        "firewheel.vm_resource_manager.vm_resource_handler.os"
    ), patch("firewheel.vm_resource_manager.vm_resource_handler.Path.mkdir"), patch(
        "firewheel.vm_resource_manager.vm_resource_handler.UTCLog"
    ), patch(
        "firewheel.vm_resource_manager.vm_resource_handler.RepositoryDb"
    ), patch(
        "firewheel.vm_resource_manager.vm_resource_handler.VMMapping"
    ), patch(
        "firewheel.vm_resource_manager.vm_resource_handler.ScheduleDb"
    ), patch(
        "firewheel.vm_resource_manager.vm_resource_handler.ScheduleUpdater"
    ), patch(
        "firewheel.vm_resource_manager.vm_resource_handler.VmResourceStore"
    ), patch.object(
        VMResourceHandler, "import_driver"
    ), patch.object(
        VMResourceHandler, "set_state"
    ):
        yield VMResourceHandler(mock_config)


class TestVMRHandler:
    @patch.object(VMResourceHandler, "print_output", new=Mock())
    def test_run_vm_resource(self, vmr_handler):
        # Tests minimum viable behavior of `run_vm_resource method`.
        # Minimum viable behavior consists of the following:
        #   - no need to reboot
        #   - preloaded data (no need to create directories or write call args)
        #   - immediate success of `async_exec` when running the `call_args` script
        #   - no use of powershell
        # Mock driver and return values
        vmr_handler.driver = Mock(name="driver")
        vmr_handler.driver.async_exec.return_value = Mock(spec=int)
        # Mock the VM resource inputs
        mock_call_args_filename = "test_filename.sh"
        mock_schedule_entry = Mock(name="schedule_entry")
        mock_schedule_entry.call_args_filename = mock_call_args_filename
        mock_schedule_entry.reboot = False
        mock_schedule_entry.executable = "Test/Executable.exe"
        # Check that correct behavior occurred
        # (methods always succeed, so they are only ever called once)
        vmr_handler.run_vm_resource(mock_schedule_entry)
        mock_pid = vmr_handler.driver.async_exec.return_value
        vmr_handler.driver.async_exec.assert_called_once_with(mock_call_args_filename)
        vmr_handler.driver.get_exitcode.assert_called_once_with(mock_pid)
        vmr_handler.print_output.assert_called_once_with(mock_schedule_entry, mock_pid)

    @patch.object(VMResourceHandler, "set_state", new=Mock())
    def test_check_for_reboot(self, vmr_handler):
        # Mock driver and return values
        vmr_handler.driver = Mock(name="driver")
        file_exists_method = vmr_handler.driver.file_exists
        # Mock the VM resource inputs
        mock_reboot_filepath = Mock(name="reboot_filepath")
        # Check that correct behavior occurred
        need_reboot = vmr_handler.check_for_reboot(mock_reboot_filepath)
        assert need_reboot == file_exists_method.return_value
        file_exists_method.assert_called_once_with(mock_reboot_filepath)

    def test_check_for_reboot_with_reconnect(self, vmr_handler):
        # Mock driver and return values
        vmr_handler.driver = Mock(name="driver")
        file_exists_method = vmr_handler.driver.file_exists
        file_exists_query_results = [None, None, None, True]
        file_exists_method.side_effect = file_exists_query_results
        # Mock the VM resource inputs
        mock_reboot_filepath = Mock(name="reboot_filepath")
        # Check that correct behavior occurred
        need_reboot = vmr_handler.check_for_reboot(mock_reboot_filepath)
        assert need_reboot == file_exists_query_results[-1]
        file_exists_method.assert_called_with(mock_reboot_filepath)
        assert file_exists_method.call_count == len(file_exists_query_results)
