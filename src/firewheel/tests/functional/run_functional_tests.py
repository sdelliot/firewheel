#!/usr/bin/env python

import os
import sys
import unittest

from firewheel.tests.functional.qos_testcase import QosTestCase
from firewheel.tests.functional.reboot_testcase import RebootTestCase
from firewheel.tests.functional.minimal_testcase import MinimalTestCase
from firewheel.tests.functional.network_testcase import NetworkTestCase
from firewheel.tests.functional.check_times_testcase import CheckTimesTestCase
from firewheel.tests.functional.router_tree_testcase import RouterTreeTestCase
from firewheel.tests.functional.vm_resource_testcase import VmResourceTestCase
from firewheel.tests.functional.windows_router_tree_testcase import (
    WindowsRouterTreeTestCase,
)
from firewheel.tests.functional.windows_vm_resource_testcase import (
    WindowsVmResourceTestCase,
)


class EndToEndTests:
    """
    This class provides an object for creating and running
    the end-to-end test suite.
    """

    def __init__(self, only_basic=False, only_windows=False, minimal=False):
        """
        Initialize loading all the test cases and class variables.

        Args:
            only_basic (bool): If True, only run the basic test cases.
            only_windows (bool): If True, only run the windows test cases.
            minimal (bool): If True, only run the minimal test case.

        Raises:
            Exception: If no test suites are available.
        """

        # Get the .coverage file location
        current_module_path = os.path.abspath(os.path.dirname(__file__))
        self.cov_rc_file = os.path.join(current_module_path, ".coveragerc")

        # Add all test cases to test suite
        self.suite_list = []
        if only_basic:
            e2e_test_suite = self.add_basic_tests()
        elif only_windows:
            e2e_test_suite = self.add_windows_tests()
        elif minimal:
            e2e_test_suite = self.add_minimal_tests()
        else:
            e2e_test_suite = self.add_tests()

        self.suite_list.append(e2e_test_suite)

        # Check to make sure we added some tests.
        if not self.suite_list:
            raise Exception("No test suites available")

        self.alltests = unittest.TestSuite(self.suite_list)

    def add_minimal_tests(self):
        """
        Initializing the minimal test suite.

        Returns:
            unittest.TestSuite: The set of minimal end-to-end tests.
        """
        # End-to-end FIREWHEEL test cases
        end_to_end_test_suite = unittest.TestSuite()
        end_to_end_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(MinimalTestCase)
        )

        return end_to_end_test_suite

    def add_basic_tests(self):
        """
        Initializing the basic test suite.

        Returns:
            unittest.TestSuite: The set of basic end-to-end tests.
        """
        # End-to-end FIREWHEEL test cases
        end_to_end_test_suite = unittest.TestSuite()
        end_to_end_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(RouterTreeTestCase)
        )

        return end_to_end_test_suite

    def add_tests(self):
        """
        Initializing the test suite.

        Returns:
            unittest.TestSuite: The set of end-to-end tests.
        """
        # End-to-end FIREWHEEL test cases
        end_to_end_test_suite = unittest.TestSuite()
        end_to_end_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(RouterTreeTestCase)
        )
        end_to_end_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(NetworkTestCase)
        )
        end_to_end_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(CheckTimesTestCase)
        )
        end_to_end_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(VmResourceTestCase)
        )
        end_to_end_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(RebootTestCase)
        )
        end_to_end_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(QosTestCase)
        )

        return end_to_end_test_suite

    def add_windows_tests(self):
        """
        Initializing the Windows test suite.

        Returns:
            unittest.TestSuite: The set of end-to-end tests using Windows.
        """
        # End-to-end FIREWHEEL test cases
        win_test_suite = unittest.TestSuite()
        win_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(WindowsRouterTreeTestCase)
        )
        win_test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(WindowsVmResourceTestCase)
        )

        return win_test_suite

    def run_tests(self):
        """
        Run all the available tests.

        Returns:
            unittest.runner.TextTestResult: The results from running the test.
        """
        return unittest.TextTestRunner(verbosity=2).run(self.alltests)


if __name__ == "__main__":
    test_obj = EndToEndTests()
    result = test_obj.run_tests()
    sys.exit(not result.wasSuccessful())
