import shutil
import unittest
from datetime import datetime as dt
from subprocess import call

from firewheel.tests.functional import common
from firewheel.tests.functional.common import launch_mc
from firewheel.tests.functional.verifier import TestVerifier, results_path


class MinimalTestCase(unittest.TestCase):
    """
    This class ensures that VMs can launch and networks can connect those
    VMs. This is the most minimally useful test case.
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
        not_configured_count = common.poll_not_configured(self.grpc_client)
        self.assertEqual(not_configured_count, 0)

        # Wait for experiment start time
        start_time = common.poll_start_time(self.grpc_client)
        self.assertIsNotNone(start_time)
        self.assertIsInstance(start_time, dt)

        # Collect data and check results
        ver = TestVerifier("pass")
        test_results = ver.get_results()
        self.assertTrue(ver.str_compare_results(test_results))

    def test_minimal(self):
        """
        This test case launches `tests.vm_gen` and `tests.connect_all`
        and ensures that all the nodes are correctly configured. This tests
        basic connectivity between non-routers in the experiment
        and can be run whenever a new cluster is set up.
        """
        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            "tests.vm_gen:2",
            "tests.connect_all",
            "tests.ping_all:False",
            f"{self.launch_mc}",
        ]

        self.run_test(exp_cmd)
