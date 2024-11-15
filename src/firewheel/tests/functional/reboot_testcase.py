import shutil
import unittest
from datetime import datetime as dt
from subprocess import call

from firewheel.tests.functional import common
from firewheel.tests.functional.common import launch_mc
from firewheel.tests.functional.verifier import TestVerifier, results_path


class RebootTestCase(unittest.TestCase):
    """
    This class leverages the :ref:`tests.reboot_mc` model component to ensure
    that VMs correctly reboot when a VMR requests it.
    """

    def setUp(self):
        """
        Set up some default variables and ensure that the testbed is clear
        and ready for running the experiment.
        """
        self.launch_mc = launch_mc
        self.grpc_client = common.initialize_grpc_client()

        # Check that the experiment restarts correctly
        ret = common.firewheel_restart()
        self.assertEqual(ret, 0)

        # check that no experiment is launched.
        ret = common.get_experiment_launch(self.grpc_client)
        self.assertIsNone(ret)

        # No user input can be passed to this command.
        cmd = ["firewheel", "mm", "clear_cache", "vm_resources"]
        ret = call(cmd)  # nosec
        self.assertEqual(ret, 0)

    def tearDown(self):
        """
        Clean up after our experiment.
        """
        # Check that the experiment restarts correctly
        ret = common.firewheel_restart()
        self.assertEqual(ret, 0)

        # No user input can be passed to this command.
        cmd = ["firewheel", "mm", "clear_cache", "vm_resources"]
        ret = call(cmd)  # nosec
        self.assertEqual(ret, 0)

        # clean up any verifier logs
        shutil.rmtree(results_path, ignore_errors=True)

    def run_test(self, exp_cmd, timeout=600, result_check="pass"):
        """
        Prevent duplicate code by running the same part of the experiment.

        Args:
            exp_cmd (list): The list of command-line arguments to launch the
                            specific FIREWHEEL experiment.
            timeout (int): The timeout to determine if the experiment is configured.
            result_check (str): The result to look for in the status file.
        """
        # Launch the experiment
        # No user input can be passed to this command.
        ret = call(exp_cmd)  # nosec

        # Check that the experiment launches correctly
        self.assertEqual(ret, 0)

        # Wait for nodes to be configured
        not_configured_count = common.poll_not_configured(
            self.grpc_client, timeout=timeout
        )
        self.assertEqual(not_configured_count, 0)

        # Wait for experiment start time
        start_time = common.poll_start_time(self.grpc_client)
        self.assertIsNotNone(start_time)
        self.assertIsInstance(start_time, dt)

        # Collect data and check results
        ver = TestVerifier(result_check)
        test_results = ver.get_results()
        self.assertTrue(ver.str_compare_results(test_results))

    def test_reboot_flag_single(self):
        """
        This test case launches a number of VMs and reboots them
        based on dropping the reboot flag. Then it checks to ensure
        that the VMR is rerun as expected.

        This test reboots 1 VM.
        """
        num_vms = 1
        test = "flag"
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            f"tests.reboot:{test}",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_reboot_flag_multiple(self):
        """
        This test case launches a number of VMs and reboots them
        based on dropping the reboot flag. Then it checks to ensure
        that the VMR is rerun as expected.

        This test reboots 10 VMs.
        """
        num_vms = 10
        test = "flag"
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            f"tests.reboot:{test}",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_reboot_exit_code_single(self):
        """
        This test case launches a number of VMs and reboots them
        based on the reboot exit code. Then it checks to ensure
        that the VMR is rerun as expected.

        This test reboots 1 VM.
        """
        num_vms = 1
        test = "exit_code"
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            f"tests.reboot:{test}",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_reboot_exit_code_multiple(self):
        """
        This test case launches a number of VMs and reboots them
        based on the reboot exit code. Then it checks to ensure
        that the VMR is rerun as expected.

        This test reboots 10 VMs.
        """
        num_vms = 10
        test = "exit_code"
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            f"tests.reboot:{test}",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_multi_vmr_reboot(self):
        """
        This test case launches a single of VM and schedules
        two VMRs to run at the same time which request reboots.
        Then it checks to ensure that the VMR is rerun as expected.

        This test reboots 1 VM.
        """
        num_vms = 1
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            "tests.reboot:exit_code",
            "tests.reboot:flag",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd, result_check="passpass")

    def test_prior_schedule(self):
        """
        This test case launches a single of VM and schedules
        a regular VMR and then a reboot one to ensure schedule order is correct.
        Then it checks to ensure that the VMR is rerun as expected.

        This test reboots 1 VM.
        """
        num_vms = 1
        test = "exit_code"
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            f"tests.reboot:{test}:-11",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd, result_check="running\npass")

    def test_same_schedule(self):
        """
        This test case launches a single of VM and schedules
        a regular VMR and then a reboot one to ensure schedule order is correct.
        Then it checks to ensure that the VMR is rerun as expected.

        This test reboots 1 VM.
        """
        num_vms = 1
        test = "exit_code"
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            f"tests.reboot:{test}:-10",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd, result_check="running\npass")

    def test_after_schedule(self):
        """
        This test case launches a single of VM and schedules
        a regular VMR and then a reboot one to ensure schedule order is correct.
        Then it checks to ensure that the VMR is rerun as expected.

        This test reboots 1 VM.
        """
        num_vms = 1
        test = "exit_code"
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            f"tests.reboot:{test}:-9",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd, result_check="passrunning")
