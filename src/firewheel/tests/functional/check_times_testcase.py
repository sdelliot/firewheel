import shutil
import unittest
from datetime import datetime as dt
from datetime import timezone
from subprocess import call

from firewheel.tests.functional import common
from firewheel.tests.functional.common import launch_mc
from firewheel.tests.functional.verifier import TestVerifier, results_path


class CheckTimesTestCase(unittest.TestCase):
    """
    This class leverages the `tests.check_times` model component to ensure connectivity
    with all the nodes of the FIREWHEEL cluster and ensure connectivity of all the
    VMs within the experiment.
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

    def test_check_times(self):
        """
        This test case launches the VmGen topology and ensures
        that all the nodes are correctly configured. This tests
        that all VMs have times that are within an acceptable
        threshold from the experiment_start time.
        """
        num_vms = 5

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.vm_gen:{num_vms}",
            "tests.check_times",
            f"{self.launch_mc}",
        ]

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
        start_timestamp = start_time.replace(tzinfo=timezone.utc).timestamp()
        # the check_time schedule_entry is running at time +30
        target_time = start_timestamp + 30
        # timestamp is in whole seconds with fractional microseconds,
        # we want whole milliseconds.
        target_time *= 1000
        delta_milliseconds = 3 * 1000
        acceptable_range = [target_time, delta_milliseconds]

        # Collect data and check results
        ver = TestVerifier(acceptable_range, "float_range")
        test_results = ver.get_results()
        self.assertTrue(ver.float_range_compare_results(test_results))
