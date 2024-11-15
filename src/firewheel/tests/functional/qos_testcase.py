import shutil
import unittest
from datetime import datetime as dt
from subprocess import call

from firewheel.tests.functional import common
from firewheel.tests.functional.common import launch_mc
from firewheel.tests.functional.verifier import TestVerifier, results_path


class QosTestCase(unittest.TestCase):
    """
    This class leverages the :ref:`tests.qos_mc` model component to provide a topology
    and VMR which will test various QoS parameters available in FIREWHEEL.
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

    def test_drop_packets(self):
        """
        This test case ensures that all the nodes are correctly configured.
        This tests that the QoS parameter related to packet drops functions
        as anticipated, i.e., all links with the parameter set have an
        appropriate amount of dropped packets as they go out on their links
        within an acceptable threshold from the specified parameter.
        """

        qos_type = "drops"

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.qos:{qos_type}",
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

        # The tests.qos MC with drop parameter expects that 50% of the packets
        # will be dropped. Therefore, an acceptable range should be within 10%.
        acceptable_range = [50, 10]

        # Collect data and check results
        ver = TestVerifier(acceptable_range, "float_range")
        test_results = ver.get_results()
        self.assertTrue(ver.float_range_compare_results(test_results))

    def test_delay(self):
        """
        This test case ensures that all the nodes are correctly configured.
        This tests that the QoS parameter related to link delay functions
        as anticipated, i.e., all links with the parameter set have an
        appropriate amount of egress delay added to their packets and are
        within an acceptable threshold from the specified parameter.
        """

        qos_type = "delay"

        exp_cmd = [
            "firewheel",
            "experiment",
            "--no-install",
            f"tests.qos:{qos_type}",
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

        # The tests.qos MC with delay parameter expects that 10s (10000ms) delay
        # will be added to each outgoing link. We expect as much as 1s deviation.
        acceptable_range = [10000, 1000]

        # Collect data and check results
        ver = TestVerifier(acceptable_range, "float_range")
        test_results = ver.get_results()
        self.assertTrue(ver.float_range_compare_results(test_results))
