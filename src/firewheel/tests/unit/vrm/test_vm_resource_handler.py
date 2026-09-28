from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from firewheel.vm_resource_manager.vm_resource_handler import VMResourceHandler


@pytest.fixture
def mock_config():
    return {"vm_name": "test_name", "path": "test/path"}


@pytest.fixture
def vmr_handler_factory():
    with patch(
        "firewheel.vm_resource_manager.vm_resource_handler.time"
    ), patch(
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
        yield lambda config: VMResourceHandler(config)


@pytest.fixture
def vmr_handler(mock_config, vmr_handler_factory):
    return vmr_handler_factory(mock_config)


class TestVMRHandler:
    @patch.object(VMResourceHandler, "print_output", new=Mock())
    def test_run_vm_resource(self, vmr_handler):
        # Tests minimum viable behavior of `run_vm_resource method`.
        # Minimum viable behavior consists of the following:
        #   - no need to reboot
        #   - preloaded data (no need to create directories or write call args)
        #   - immediate success of `async_exec` when running the `call_args` script
        #   - no use of powershell
        vmr_handler.driver = Mock(name="driver")
        vmr_handler.driver.async_exec.return_value = Mock(spec=int)

        mock_call_args_filename = "test_filename.sh"
        mock_schedule_entry = Mock(name="schedule_entry")
        mock_schedule_entry.call_args_filename = mock_call_args_filename
        mock_schedule_entry.reboot = False
        mock_schedule_entry.executable = "Test/Executable.exe"

        vmr_handler.run_vm_resource(mock_schedule_entry)
        mock_pid = vmr_handler.driver.async_exec.return_value
        vmr_handler.driver.async_exec.assert_called_once_with(mock_call_args_filename)
        vmr_handler.driver.get_exitcode.assert_called_once_with(mock_pid)
        vmr_handler.print_output.assert_called_once_with(mock_schedule_entry, mock_pid)

    @patch.object(VMResourceHandler, "set_state", new=Mock())
    def test_check_for_reboot(self, vmr_handler):
        vmr_handler.driver = Mock(name="driver")
        file_exists_method = vmr_handler.driver.file_exists

        mock_reboot_filepath = Mock(name="reboot_filepath")

        need_reboot = vmr_handler.check_for_reboot(mock_reboot_filepath)
        assert need_reboot == file_exists_method.return_value
        file_exists_method.assert_called_once_with(mock_reboot_filepath)

    def test_check_for_reboot_with_reconnect(self, vmr_handler):
        vmr_handler.driver = Mock(name="driver")
        file_exists_method = vmr_handler.driver.file_exists
        file_exists_query_results = [None, None, None, True]
        file_exists_method.side_effect = file_exists_query_results

        mock_reboot_filepath = Mock(name="reboot_filepath")

        need_reboot = vmr_handler.check_for_reboot(mock_reboot_filepath)
        assert need_reboot == file_exists_query_results[-1]
        file_exists_method.assert_called_with(mock_reboot_filepath)
        assert file_exists_method.call_count == len(file_exists_query_results)

    @patch("firewheel.vm_resource_manager.vm_resource_handler.time.sleep", new=Mock())
    def test_transfer_data_skips_guest_path_traversal(self, vmr_handler, tmp_path):
        """Ensure guest-controlled filenames cannot escape the transfer directory."""
        vmr_handler.driver = Mock(name="driver")
        vmr_handler.log = Mock()
        vmr_handler.target_os = "Linux"

        destination = tmp_path / "dest"
        destination.mkdir()

        vmr_handler.driver.file_exists.return_value = True
        vmr_handler.driver.get_files.return_value = ["../../evil.txt"]

        def fake_read_file(_filename, local_destination, mode="rb"):
            local_destination = Path(local_destination)
            local_destination.parent.mkdir(parents=True, exist_ok=True)
            local_destination.write_text("malicious write")
            return True

        vmr_handler.driver.read_file.side_effect = fake_read_file

        vmr_handler._transfer_data(
            name="vm1",
            location="/guest/source",
            interval=None,
            destination=str(destination),
        )

        # On the original vulnerable code, this assertion should FAIL because
        # read_file() will be called with a path like:
        #   <dest>/vm1/../../evil.txt
        #
        # After the vmrm-01 fix, it should PASS because the unsafe path
        # should be rejected and skipped before read_file() is invoked.
        vmr_handler.driver.read_file.assert_not_called()

        # Also confirm nothing escaped to the tmp root.
        assert not (tmp_path / "evil.txt").exists()
        vmr_handler.log.error.assert_called()

    @patch("firewheel.vm_resource_manager.vm_resource_handler.time.sleep", new=Mock())
    def test_transfer_data_allows_contained_guest_path(self, vmr_handler, tmp_path):
        """Ensure normal guest filenames are transferred under the destination."""
        vmr_handler.driver = Mock(name="driver")
        vmr_handler.log = Mock()
        vmr_handler.target_os = "Linux"

        destination = tmp_path / "dest"
        destination.mkdir()

        vmr_handler.driver.file_exists.return_value = True
        vmr_handler.driver.get_files.return_value = ["logs/output.txt"]

        def fake_read_file(_filename, local_destination, mode="rb"):
            local_destination = Path(local_destination)
            local_destination.parent.mkdir(parents=True, exist_ok=True)
            local_destination.write_text("ok")
            return True

        vmr_handler.driver.read_file.side_effect = fake_read_file

        vmr_handler._transfer_data(
            name="vm1",
            location="/guest/source",
            interval=None,
            destination=str(destination),
        )

        expected = destination / "vm1" / "logs" / "output.txt"
        assert expected.exists()
        vmr_handler.driver.read_file.assert_called_once()

        called_filename, called_dest = vmr_handler.driver.read_file.call_args[0]
        assert called_filename == "logs/output.txt"
        assert Path(called_dest) == expected

    def test_init_rejects_unsafe_vm_name(self, mock_config, vmr_handler_factory):
        """Ensure unsafe VM names are rejected before path construction."""
        bad_config = dict(mock_config)
        bad_config["vm_name"] = "../evil"

        with pytest.raises(ValueError):
            vmr_handler_factory(bad_config)

    def test_init_allows_safe_vm_name(self, mock_config, vmr_handler_factory):
        """Ensure normal VM names are accepted."""
        good_config = dict(mock_config)
        good_config["vm_name"] = "vm-01.test_name"

        handler = vmr_handler_factory(good_config)

        assert handler.config["vm_name"] == "vm-01.test_name"