import io
import os
import shlex
import socket
import tempfile
import unittest
from unittest.mock import patch, mock_open

from firewheel.cli import utils
from firewheel.cli.utils import HelperNotFoundError
from firewheel.cli.helper import Helper
from firewheel.cli.helper_group import HelperGroup


class CliUtilsTestCase(unittest.TestCase):
    def setUp(self):
        # Create a helper directory
        # pylint: disable=consider-using-with
        self.helper_root = tempfile.TemporaryDirectory()

        self.author = "Unittest"
        self.description = "Testing this case."

    def tearDown(self):
        # remove the temp directory
        self.helper_root.cleanup()

    def test_parse_to_helper_index(self):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create Helper dict
        index_helper_obj = Helper("index", index_path)
        helper_dict = {
            index_name: {
                helper_name: Helper(helper_name, index_path),
                "index": index_helper_obj,
            }
        }

        ret = utils.parse_to_helper(index_name, helper_dict)
        self.assertEqual(ret[0], index_helper_obj)

    @patch("builtins.input", side_effect=["yes"])
    def test_parse_to_helper_index_args(self, _mock_input):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create HelperGroup dict
        helper_group = HelperGroup(index_path)
        index_helper_obj = Helper("index", index_path)
        helpers = {
            helper_name: Helper(helper_name, index_path),
            "index": index_helper_obj,
        }
        helper_group.helpers = helpers
        helper_dict = {index_name: helper_group}

        func_args = f"{index_name} invalid"
        ret = utils.parse_to_helper(func_args, helper_dict)
        self.assertEqual(ret[0], index_helper_obj)

    @patch("builtins.input", side_effect=["no"])
    def test_parse_to_helper_index_args_no(self, _mock_input):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create HelperGroup dict
        helper_group = HelperGroup(index_path)
        index_helper_obj = Helper("index", index_path)
        helpers = {
            helper_name: Helper(helper_name, index_path),
            "index": index_helper_obj,
        }
        helper_group.helpers = helpers
        helper_dict = {index_name: helper_group}

        func_args = f"{index_name} invalid"
        with self.assertRaises(HelperNotFoundError):
            utils.parse_to_helper(func_args, helper_dict)

    @patch("builtins.input", side_effect=["yes"])
    def test_parse_to_helper_no_index_args(self, _mock_input):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f2 = "test2"

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create Helper dict
        helper_group = HelperGroup(index_path)
        helpers = {
            helper_name: Helper(helper_name, index_path),
        }
        helper_group.helpers = helpers
        helper_dict = {index_name: helper_group}
        func_args = f"{index_name} invalid"
        with self.assertRaises(HelperNotFoundError):
            utils.parse_to_helper(func_args, helper_dict)

    def test_parse_to_helper_args(self):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f2 = "test2"

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, helper_name), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create Helper dict
        valid_helper = Helper(helper_name, index_path)
        helper_dict = {helper_name: valid_helper}
        arg_list = ["arg1", "arg2"]
        func_args = f"{helper_name} {' '.join(arg_list)}"
        obj, args = utils.parse_to_helper(func_args, helper_dict)
        self.assertEqual(obj, valid_helper)
        self.assertEqual(args, arg_list)

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_process_helper_group_invalid(self, mock_stdout):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create Helper dict
        index_helper_obj = Helper("index", index_path)
        helper_dict = {
            index_name: {
                helper_name: Helper(helper_name, index_path),
                "index": index_helper_obj,
            }
        }

        invalid_path = os.path.join(index_path, "invalid")
        utils.process_helper_group(invalid_path, helper_dict)
        msg = "Helper path not found"
        self.assertIn(msg, mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_load_helper_invalid(self, mock_stdout):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "invalid"
        helper_regular = str(
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, helper_name), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create Helper dict
        index_helper_obj = Helper("index", index_path)
        helper_dict = {index_name: {"index": index_helper_obj}}

        utils.load_helper(os.path.join(index_path, helper_name), helper_dict)
        msg_1 = "Malformed section encountered"
        msg_2 = "Continuing without Helper"
        self.assertIn(msg_1, mock_stdout.getvalue())
        self.assertIn(msg_2, mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_load_helper_invalid_path(self, mock_stdout):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "invalid"

        # Create Helper dict
        index_helper_obj = Helper("index", index_path)
        helper_dict = {index_name: {"index": index_helper_obj}}

        utils.load_helper(os.path.join(index_path, helper_name), helper_dict)
        msg_1 = "Unexpected error while parsing Helper"
        msg_2 = "Continuing without Helper"
        self.assertIn(msg_1, mock_stdout.getvalue())
        self.assertIn(msg_2, mock_stdout.getvalue())


class CliUtilsSSHTestCase(unittest.TestCase):
    def setUp(self):
        self.author = "Unittest"
        self.description = "Testing this case."

        # Specify the local host (defined by `minimegaAPI.cluster_head_node`)
        self.local_hostname = f"{socket.gethostname()}"
        # SSH-specific case settings
        self.ssh = utils.SSHManager()
        self.remote_user = "test_user"
        self.remote_host = "hostname.test"
        self.remote_address = f"{self.remote_user}@{self.remote_host}"
        self.vm_ip = "ABC.DEF.GHI.JKL"
        self.ssh_default_options = [  # A flattened form of the options list
            "-o",
            "LogLevel=error",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            f"ProxyCommand ssh -o BatchMode=yes {self.local_hostname} -W %h:%p",
        ]

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SSHManager._get_remote_vm_ip")
    def test_call_ssh(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call
        mock_subprocess.return_value.returncode = 0

        # Test the call (no additional options or command specified)
        result = self.ssh(self.remote_address)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SSH command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "ssh",
                *self.ssh_default_options,
                f"{self.remote_user}@{self.vm_ip}",
            ],
            check=True,
            capture_output=False,
        )

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SSHManager._get_remote_vm_ip")
    def test_call_ssh_default_user(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call
        mock_subprocess.return_value.returncode = 0

        # Test the call (no additional options or command specified)
        result = self.ssh(self.remote_host)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SSH command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "ssh",
                *self.ssh_default_options,
                f"{self.vm_ip}",
            ],
            check=True,
            capture_output=False,
        )

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SSHManager._get_remote_vm_ip")
    def test_call_ssh_with_options(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call
        mock_subprocess.return_value.returncode = 0

        # Test the call (with additional options)
        test_options = [("-L", "localhost:5000:localhost:5000")]
        result = self.ssh(self.remote_address, options=test_options)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SSH command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "ssh",
                *self.ssh_default_options,
                *test_options[0],
                f"{self.remote_user}@{self.vm_ip}",
            ],
            check=True,
            capture_output=False,
        )

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SSHManager._get_remote_vm_ip")
    def test_call_ssh_with_command(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call
        mock_subprocess.return_value.returncode = 0

        # Test the call (with command specified)
        test_command = "ls -la"
        result = self.ssh(self.remote_address, command=test_command)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SSH command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "ssh",
                *self.ssh_default_options,
                f"{self.remote_user}@{self.vm_ip}",
                *shlex.split(test_command),
            ],
            check=True,
            capture_output=False,
        )


class CliUtilsParallelSSHTestCase(unittest.TestCase):
    def setUp(self):
        self.author = "Unittest"
        self.description = "Testing this case."

        # Specify the local host (defined by `minimegaAPI.cluster_head_node`)
        self.local_hostname = f"{socket.gethostname()}"
        # PSSH-specific case settings
        self.pssh = utils.ParallelSSHManager()
        self.remote_user = "test_user"
        self.remote_hosts = ["hostname0.test", "hostname1.test"]
        self.remote_addresses = [
            f"{self.remote_user}@{host}" for host in self.remote_hosts
        ]
        self.vm_ips = ["ABC.DEF.GHI.JKL", "MNO.PQR.STU.VWX"]
        self.pssh_default_options = [  # A flattened form of the options list
            "-O",
            "LogLevel=error",
            "-O",
            "UserKnownHostsFile=/dev/null",
            "-O",
            "StrictHostKeyChecking=no",
            "-O",
            f"ProxyCommand ssh -o BatchMode=yes {self.local_hostname} -W %h:%p",
        ]

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.ParallelSSHManager._get_remote_vm_ip")
    def test_call_pssh(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of remote VM IP addresses
        mock_ip_method.side_effect = self.vm_ips
        # Mock a successful PSSH call
        mock_subprocess.return_value.returncode = 0

        # Test the call
        test_command = "ls -la"
        test_options = [("-H", " ".join(self.remote_addresses)), ("-p", "10")]
        result = self.pssh(test_command, options=test_options)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the PSSH command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "parallel-ssh",
                *self.pssh_default_options,
                "-H",
                f"{self.remote_user}@{self.vm_ips[0]} {self.remote_user}@{self.vm_ips[1]}",
                "-p",
                "10",
                test_command,
            ],
            check=True,
            capture_output=False,
        )

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.ParallelSSHManager._get_remote_vm_ip")
    def test_call_pssh_multiple_options(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of remote VM IP addresses
        mock_ip_method.side_effect = self.vm_ips
        # Mock a successful PSSH call
        mock_subprocess.return_value.returncode = 0

        # Test the call
        test_command = "ls -la"
        test_options = [("-H", address) for address in self.remote_addresses]
        result = self.pssh(test_command, options=test_options)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SSH command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "parallel-ssh",
                *self.pssh_default_options,
                "-H",
                f"{self.remote_user}@{self.vm_ips[0]}",
                "-H",
                f"{self.remote_user}@{self.vm_ips[1]}",
                test_command,
            ],
            check=True,
            capture_output=False,
        )

    @patch("subprocess.run")
    def test_call_pssh_host_file(self, mock_subprocess):
        # Mock the acquisition of remote VM IP addresses
        mocked_vm_dict = {
            host: {"control_ip": ip} for host, ip in zip(self.remote_hosts, self.vm_ips)
        }
        # Mock a successful PSSH call
        mock_subprocess.return_value.returncode = 0

        mocked_open = mock_open(read_data="\n".join(self.remote_addresses))
        with patch(
            "firewheel.cli.utils.Path.open", mocked_open
        ) as mock_open_method, patch(
            "firewheel.cli.utils.minimegaAPI.mm_vms"
        ) as mock_vm_method, patch(
            "firewheel.cli.utils.Path.unlink"
        ) as mock_unlink_method:
            mock_write_method = mock_open_method.return_value.write
            mock_vm_method.return_value = mocked_vm_dict
            # Test the call (with a file of hosts provided)
            test_command = "ls -la"
            test_options = [("-h", "test_file.txt")]
            result = self.pssh(test_command, options=test_options)
            self.assertIs(result, mock_subprocess.return_value)
            # Check that the SSH command executed via subprocess was correct
            mock_subprocess.assert_called_with(
                [
                    "parallel-ssh",
                    *self.pssh_default_options,
                    "-h",
                    "test_file.tmp",
                    test_command,
                ],
                check=True,
                capture_output=False,
            )
            mock_write_method.assert_called_once_with(
                "\n".join(f"{self.remote_user}@{self.vm_ips[_]}" for _ in (0, 1))
            )
            mock_unlink_method.assert_called_once()

    def test_call_pssh_no_hosts(self):
        # Test the call with no hosts specified
        with self.assertRaises(ValueError):
            test_command = "ls -la"
            test_options = [("-p", "10")]
            self.pssh(test_command, options=test_options)


class CliUtilsSCPTestCase(unittest.TestCase):
    def setUp(self):
        self.author = "Unittest"
        self.description = "Testing this case."

        # Specify the local host (defined by `minimegaAPI.cluster_head_node`)
        self.local_hostname = f"{socket.gethostname()}"
        # SCP-specific case settings
        self.scp = utils.SCPManager()
        self.remote_user = "test_user"
        self.remote_host = "hostname.test"
        self.remote_address = f"{self.remote_user}@{self.remote_host}"
        self.vm_ip = "ABC.DEF.GHI.JKL"
        self.scp_default_options = [  # A flattened form of the options list
            "-o",
            "LogLevel=error",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            f"ProxyCommand ssh -o BatchMode=yes {self.local_hostname} -W %h:%p",
            "-r",
        ]

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SCPManager._get_remote_vm_ip")
    def test_call_scp_push(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call (raises `SystemExit` with exit code 0)
        mock_subprocess.return_value.returncode = 0

        # Test pushing a file (no additional options specified)
        local_source = "/test/local/location/file.test"
        remote_file = "/test/remote/location"
        remote_target = f"{self.remote_address}:{remote_file}"
        result = self.scp(remote_target, local_source)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SCP command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "scp",
                *self.scp_default_options,
                local_source,
                f"{self.remote_user}@{self.vm_ip}:{remote_file}",
            ],
            check=True,
            capture_output=False,
        )

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SCPManager._get_remote_vm_ip")
    def test_call_scp_push_multiple(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call (raises `SystemExit` with exit code 0)
        mock_subprocess.return_value.returncode = 0

        # Test pushing multiple files (no additional options specified)
        local_sources = [
            "/test/local/location/file1.test",
            "/test/local/location/file2.test",
        ]
        remote_file = "/test/remote/location"
        remote_target = f"{self.remote_address}:{remote_file}"
        result = self.scp(remote_target, *local_sources)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SCP command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "scp",
                *self.scp_default_options,
                *local_sources,
                f"{self.remote_user}@{self.vm_ip}:{remote_file}",
            ],
            check=True,
            capture_output=False,
        )

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SCPManager._get_remote_vm_ip")
    def test_call_scp_pull(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call (raises `SystemExit` with exit code 0)
        mock_subprocess.return_value.returncode = 0

        # Test pulling a file (no additional options specified)
        local_target = "/test/local/location/"
        remote_file = "/test/remote/location/file.test"
        remote_source = f"{self.remote_address}:{remote_file}"
        result = self.scp(local_target, remote_source)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SCP command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "scp",
                *self.scp_default_options,
                f"{self.remote_user}@{self.vm_ip}:{remote_file}",
                local_target,
            ],
            check=True,
            capture_output=False,
        )

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SCPManager._get_remote_vm_ip")
    def test_call_scp_pull_multiple(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call (raises `SystemExit` with exit code 0)
        mock_subprocess.return_value.returncode = 0

        # Test pulling multiple files (no additional options specified)
        local_target = "/test/local/location/"
        remote_files = [
            "/test/remote/location/file1.test",
            "/test/remote/location/file2.test",
        ]
        remote_sources = [f"{self.remote_user}@{self.vm_ip}:{_}" for _ in remote_files]
        result = self.scp(local_target, *remote_sources)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SCP command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "scp",
                *self.scp_default_options,
                *remote_sources,
                local_target,
            ],
            check=True,
            capture_output=False,
        )

    def test_scp_invalid_no_source_files(self):
        # Test the call with no source files specified
        with self.assertRaises(ValueError):
            self.scp("test_target")

    def test_scp_invalid_no_remote(self):
        # Test the call with no remote system specified
        with self.assertRaises(SystemExit) as context:
            self.scp("test_target", "test_source")
            self.assertEqual(context.exception.code, 1)

    @patch("subprocess.run")
    @patch("firewheel.cli.utils.SCPManager._get_remote_vm_ip")
    def test_scp_pull_with_options(self, mock_ip_method, mock_subprocess):
        # Mock the acquisition of a remote VM IP address
        mock_ip_method.return_value = self.vm_ip
        # Mock a successful SSH call (raises `SystemExit` with exit code 0)
        mock_subprocess.return_value.returncode = 0

        # Test pulling a file (with additional options)
        local_target = "/test/local/location/"
        remote_file = "/test/remote/location/file.test"
        remote_source = f"{self.remote_address}:{remote_file}"
        test_options = [("-f", "alt_ssh_config")]
        result = self.scp(local_target, remote_source, options=test_options)
        self.assertIs(result, mock_subprocess.return_value)
        # Check that the SCP command executed via subprocess was correct
        mock_subprocess.assert_called_with(
            [
                "scp",
                *self.scp_default_options,
                *test_options[0],
                f"{self.remote_user}@{self.vm_ip}:{remote_file}",
                local_target,
            ],
            check=True,
            capture_output=False,
        )
