#!/usr/bin/env python
import os
import sys
import shutil
import tempfile
import subprocess
from time import sleep
from subprocess import call
from multiprocessing import Pool

from firewheel.lib.minimega.api import minimegaAPI

results_path = tempfile.mkdtemp()


def grab_file(name):
    """
    This function is intended to be used as a process call. It is responsible
    for pulling the status file from the VM, reading it, and passing back the
    result.

    Args:
        name (str): The name of the VM.

    Returns:
        tuple: A tuple containing the name and result.
    """
    r_file = os.path.join(results_path, name)

    # This should be ignored by Bandit as that tmp file is within the experiment.
    cmd = ["firewheel", "pull", "file", "/tmp/status", name, r_file]  # noqa: S108
    res = call(cmd, stderr=subprocess.DEVNULL)
    result = None
    if res != 0:
        return name, result

    try:
        with open(r_file, "r", encoding="utf8") as f_hand:
            result = f_hand.read().strip()
    except FileNotFoundError:
        return name, None

    return name, result


class TestVerifier:
    """
    This class ensures that a FIREWHEEL test case passes successfully. In order
    to use this class, we assume that each VM in the FIREWHEEL experiment will
    produce a file in `/tmp/status`. This file will contain the tests' condition.
    Currently, we only support tests which expect a string located within the file.
    For example, the `/tmp/status` may contain either 'pass' or 'fail'.
    """

    def __init__(self, expected_value, comparison_type="str", num_threads=20):
        """
        Initialize the variables needed to perform the verification.

        Args:
            expected_value: The value that you should expect to compare against.
                            This is typically going to be a string.
            comparison_type (str): The type of the expected value. Currently we
                                   only support `str` and `float_range`, but in the future
                                   other  values like `datetime` may be supported.
            num_threads (int): The number of threads for grabbing the status from the VMs.
        """
        self.expected_value = expected_value
        self.comparison_type = comparison_type
        self.num_threads = num_threads

    def get_results(self):
        """
        This is the main function which loops until a status file is procured
        from each VM in the experiment. It uses a process pool to dole out the
        job of grabbing the status files.

        Returns:
            dict: A dictionary of the results where key=VM name and value is
            the value from the status file.
        """
        # Get the list of VMs
        mm_api = minimegaAPI()
        vm_dict = mm_api.mm_vms()
        results = dict.fromkeys(vm_dict, None)

        timeout = 10
        count = 0
        while None in results.values():
            remain = [k for k, v in results.items() if v is None]
            with Pool(processes=self.num_threads) as pool:
                for i in pool.map(grab_file, remain):
                    results[i[0]] = i[1]

            if count >= timeout:
                print("Timeout occurred getting results")
                break
            count += 1
            sleep(5)

        return results

    def str_compare_results(self, results):
        """
        This method is a simple string compare function which verifies that
        the expected value is the same for each of the results.

        Args:
            results (dict): The dictionary of results where the key is the name of
                            a VM and the value is the result.

        Returns:
            bool: True is all the results match and False otherwise.
        """
        for name, val in results.items():
            if val is None:
                print(f"name={name},obs={val},exp={self.expected_value}")
                return False
            if val.lower() != self.expected_value.lower():
                print(f"name={name},obs={val},exp={self.expected_value}")
                return False
        return True

    def float_range_compare_results(self, results):
        """
        This method is a simple string compare function which verifies that
        the expected value is within an acceptable delta for each of the results.

        Args:
            results (dict): The dictionary of results where the key is the name of
                            a VM and the value is the result.

        Returns:
            bool: True is all the results are within the range and False otherwise.
        """
        true_value = self.expected_value[0]
        tolerance = self.expected_value[1]
        for name, val in results.items():
            if val is None:
                return False
            fval = float(val)
            delta = abs(fval - true_value)
            if delta > tolerance:
                print(f"name={name},obs={fval},exp={true_value},delta={delta}")
                return False
        return True


# pylint: disable=invalid-name
if __name__ == "__main__":
    usage = f"Usage: {sys.argv[0]} <expected value> [comparison_type]"

    if (len(sys.argv) < 2) or (len(sys.argv) > 3):
        print(usage)
        sys.exit(-1)
    if len(sys.argv) == 2:
        ver = TestVerifier(sys.argv[1])
    else:
        ver = TestVerifier(sys.argv[1], sys.argv[2])

    test_results = ver.get_results()

    is_valid = False
    if ver.comparison_type == "str":
        is_valid = ver.str_compare_results(test_results)
    if ver.comparison_type == "float_range":
        is_valid = ver.float_range_compare_results(test_results)
    print(f"Test Passed={is_valid}")

    # Clean up all the files
    shutil.rmtree(results_path)

    # Provide the correct exit code
    sys.exit(not is_valid)
