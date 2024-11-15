import math
import time
import unittest

import pytest

from firewheel.config import config
from firewheel.vm_resource_manager.experiment_start import ExperimentStart


class ExperimentStartTestCase(unittest.TestCase):
    def setUp(self):
        self.experiment_start = ExperimentStart(
            hostname=config["grpc"]["hostname"],
            port=config["grpc"]["port"],
            db=config["test"]["grpc_db"],
        )

    def tearDown(self):
        self.experiment_start.clear_start_time()
        del self.experiment_start
        self.experiment_start = None

    def test_single_start_time(self):
        inserted_time = self.experiment_start.add_start_time()
        determined_start_time = self.experiment_start.get_start_time()

        self.assertEqual(inserted_time, determined_start_time)

    def test_two_start_time(self):
        inserted_time_1 = self.experiment_start.add_start_time()
        # The database ends up rounding to a 1-second resolution.
        # Sleep 2 seconds to make sure we get different time stamps
        # every time.
        time.sleep(2)
        # pylint: disable=unused-variable
        inserted_time_2 = self.experiment_start.add_start_time()  # noqa: F841

        determined_start_time = self.experiment_start.get_start_time()
        self.assertEqual(inserted_time_1, determined_start_time)

    def test_duplicate_connection(self):
        # Do this first, to test that the second doesn't blow everything away.
        inserted_time = self.experiment_start.add_start_time()
        first_fetch = self.experiment_start.get_start_time()

        second_conn = ExperimentStart(
            hostname=config["grpc"]["hostname"],
            port=config["grpc"]["port"],
            db=config["test"]["grpc_db"],
        )

        second_fetch = second_conn.get_start_time()

        self.assertEqual(first_fetch, second_fetch)
        self.assertEqual(inserted_time, first_fetch)

    def test_get_no_start_yet(self):
        determined_start_time = self.experiment_start.get_start_time()
        self.assertEqual(None, determined_start_time)

    def test_clear_start_time(self):
        inserted_time = self.experiment_start.add_start_time()
        fetch = self.experiment_start.get_start_time()
        self.assertEqual(inserted_time, fetch)

        ret = self.experiment_start.clear_start_time()
        self.assertEqual({}, ret)

        second_fetch = self.experiment_start.get_start_time()
        self.assertTrue(fetch != second_fetch)
        self.assertEqual(None, second_fetch)

    def test_set_launch_time(self):
        inserted_time = self.experiment_start.set_launch_time()
        determined_start_time = self.experiment_start.get_launch_time()

        self.assertEqual(inserted_time, determined_start_time)

        time.sleep(5)

        determined_start_time = self.experiment_start.get_launch_time()
        self.assertEqual(inserted_time, determined_start_time)

    def test_get_launch_time(self):
        determined_start_time = self.experiment_start.get_launch_time()

        self.assertEqual(None, determined_start_time)

        time.sleep(5)

        inserted_time = self.experiment_start.set_launch_time()
        determined_start_time = self.experiment_start.get_launch_time()
        self.assertEqual(inserted_time, determined_start_time)

    def test_get_time_to_start(self):
        # Set launch time
        inserted_time = self.experiment_start.set_launch_time()
        determined_launch_time = self.experiment_start.get_launch_time()
        self.assertEqual(inserted_time, determined_launch_time)

        # Should return none if the experiment hasn't started
        delta = self.experiment_start.get_time_to_start()
        self.assertEqual(None, delta)

        # Set the start time
        inserted_time = self.experiment_start.add_start_time()
        determined_start_time = self.experiment_start.get_start_time()
        self.assertEqual(inserted_time, determined_start_time)

        # The time should be "close" to 60 seconds
        delta = self.experiment_start.get_time_to_start()
        self.assertTrue(math.isclose(delta, 60, rel_tol=0.05))

    @pytest.mark.long
    def test_get_time_since_start(self):
        # Should return none if the experiment hasn't started
        delta = self.experiment_start.get_time_since_start()
        self.assertEqual(None, delta)

        # Set the start time
        inserted_time = self.experiment_start.add_start_time()
        determined_start_time = self.experiment_start.get_start_time()
        self.assertEqual(inserted_time, determined_start_time)

        time.sleep(65)

        # The time should be "close" to 5 seconds
        delta = self.experiment_start.get_time_since_start()
        self.assertTrue(math.isclose(delta, 5, rel_tol=0.05))
