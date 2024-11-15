import shutil
import unittest
from datetime import datetime as dt
from subprocess import call

from firewheel.tests.functional import common
from firewheel.tests.functional.common import launch_mc
from firewheel.tests.functional.verifier import TestVerifier, results_path


class NetworkTestCase(unittest.TestCase):
    """
    This class creates a flat star topology to ensure 1) connectivity
    with all the nodes of the FIREWHEEL cluster 2) ensure connectivity of all the
    VMs within the experiment (assuming they should be connected) and 3)
    that all the NICs/networks expected in the experiment are created correctly.
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

    def tearDown(self):
        """
        Clean up after our experiment.
        """
        # Check that the experiment restarts correctly
        ret = common.firewheel_restart()
        self.assertEqual(ret, 0)

        # clean up any verifier logs
        shutil.rmtree(results_path, ignore_errors=True)

    def run_test(self, exp_cmd):
        """
        Helper method to run the test case.

        This launches the experiment, ensures everything configures, waits for
        a start time, collects data, and checks results.

        Args:
            exp_cmd (list): The command to launch the experiment.
        """
        # Launch the experiment
        # No user input can be passed to this command.
        ret = call(exp_cmd)  # nosec

        # Check that the experiment launches correctly
        self.assertEqual(ret, 0)

        # Wait for nodes to be configured
        not_configured_count = common.poll_not_configured(self.grpc_client, timeout=450)
        self.assertEqual(not_configured_count, 0)

        # Wait for experiment start time
        start_time = common.poll_start_time(self.grpc_client)
        self.assertIsNotNone(start_time)
        self.assertIsInstance(start_time, dt)

        # Collect data and check results
        ver = TestVerifier("pass")
        test_results = ver.get_results()
        self.assertTrue(ver.str_compare_results(test_results))

    def test_ping_all_10(self):
        """
        This test case launches a flat star topology and ensures
        that all the nodes are correctly configured. This tests
        basic connectivity and can be run whenever a new cluster
        is set up.

        This experiment connects 10 VMs.
        """
        target_vm_count = 10

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{target_vm_count}",
            "tests.connect_all",
            "tests.ping_all",
            f"{self.launch_mc}",
        ]

        self.run_test(exp_cmd)

    def test_ping_all_10_ipv6(self):
        """
        This test case launches a flat star topology and ensures
        that all the nodes are correctly configured with IPv6. This tests
        basic connectivity and can be run whenever a new cluster
        is set up.

        This experiment connects 10 VMs.
        """
        target_vm_count = 10

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{target_vm_count}",
            "tests.connect_all:1:true",
            "tests.ping_all",
            f"{self.launch_mc}",
        ]

        self.run_test(exp_cmd)

    def test_ping_all_200(self):
        """
        This test case launches a flat star topology and ensures
        that all the nodes are correctly configured. This tests
        basic connectivity and can be run whenever a new cluster
        is set up.

        This experiment connects 200 VMs.
        """
        target_vm_count = 200

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{target_vm_count}",
            "tests.connect_all",
            "tests.ping_all",
            f"{self.launch_mc}",
        ]

        self.run_test(exp_cmd)

    def test_ping_all_2vm_2net(self):
        """
        This test case launches a flat star topology and ensures
        that all the nodes are correctly configured. This tests
        basic connectivity and can be run whenever a new cluster
        is set up.

        This experiment connects 2 VMs and 2 networks.
        """
        target_vm_count = 2
        network_count = 2

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{target_vm_count}",
            f"tests.connect_all:{network_count}",
            "tests.ping_all",
            f"{self.launch_mc}",
        ]

        self.run_test(exp_cmd)

    def test_ping_all_2vm_150_net(self):
        """
        This test case launches a flat star topology and ensures
        that all the nodes are correctly configured. This tests
        basic connectivity and can be run whenever a new cluster
        is set up.

        This experiment connects 2 VMs and 150 networks.
        """
        target_vm_count = 2
        network_count = 150

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{target_vm_count}",
            f"tests.connect_all:{network_count}",
            "tests.ping_all",
            f"{self.launch_mc}",
        ]

        self.run_test(exp_cmd)

    def test_ping_all_10vm_150_net(self):
        """
        This test case launches a flat star topology and ensures
        that all the nodes are correctly configured. This tests
        basic connectivity and can be run whenever a new cluster
        is set up.

        This experiment connects 150 VMs and 150 networks.
        """
        network_count = 150
        target_vm_count = 10

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{target_vm_count}",
            f"tests.connect_all:{network_count}",
            "tests.ping_all",
            f"{self.launch_mc}",
        ]

        self.run_test(exp_cmd)
