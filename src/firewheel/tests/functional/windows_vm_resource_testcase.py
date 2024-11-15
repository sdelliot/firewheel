from firewheel.tests.functional.vm_resource_testcase import VmResourceTestCase


class WindowsVmResourceTestCase(VmResourceTestCase):
    """
    This class leverages the `tests.large_resource` model component to ensure
    that VM Resources correctly get uploaded to experiment VMs.

    The host VMs will all be Windows 7 rather than Ubuntu.
    """

    def test_1b_file_preload(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 1B file onto 1 VM. It ensures that files
        can be dropped into locations that will be created by earlier
        running vm_resources, even if the file is preloaded.

        """
        num_vms = 1
        num_bytes = 1
        location_dir = "\\launch\\t2"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}:True",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_1b_file(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 1B file onto 1 VM.
        """
        num_vms = 1
        num_bytes = 1
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_1kb_file(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 1KB file onto 1 VM.
        """
        num_vms = 1
        num_bytes = 1024
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_1mb_file(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 1MB file onto 1 VM.
        """
        num_vms = 1
        num_bytes = 1048576
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_100mb_file(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 100MB file onto 1 VM.
        """
        num_vms = 1
        num_bytes = 104857600
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]
        self.run_test(exp_cmd)

    def test_1gb_file(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 1GB file onto 1 VM.
        """
        num_vms = 1
        num_bytes = 1073741824
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]

        print("NOTE: This test will take a long time to execute!")
        self.run_test(exp_cmd)

    def test_5gb_file(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 5GB file onto 1 VM.
        """
        num_vms = 1
        num_bytes = 5368709120
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]

        print("NOTE: This test will take a long time to execute!")
        self.run_test(exp_cmd, timeout=1200)

    def test_20gb_file(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 20GB file onto 1 VM.
        """
        num_vms = 1
        num_bytes = 21474836480
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]

        print("NOTE: This test will take a long time to execute!")
        self.run_test(exp_cmd, timeout=4800)

    def test_5gb_file_many(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 5GB file onto 50 VMs.
        """
        num_vms = 20
        num_bytes = 5368709120
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]
        print("NOTE: This test will take a long time to execute!")
        self.run_test(exp_cmd, timeout=1200)

    def test_1gb_file_3_times(self):
        """
        This test case launches a number of VMs and drops a file
        onto the VM. Then it checks to ensure that the file dropped
        is the same as the one that was supposed to have been send.

        This test drops a 1GB file onto 1 VM, three different times.
        The file will regenerate and this ensures that the new copy
        and not a cached version is sent to the VM.
        """
        num_vms = 1
        num_bytes = 1073741824
        location_dir = "\\launch\\"
        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.vm_gen:{num_vms}",
            f"tests.large_resource:{num_bytes}:{location_dir}",
            f"{self.launch_mc}",
        ]

        print("NOTE: This test will take a long time to execute!")
        self.run_test(exp_cmd)

        # Clean up the running experiment
        self.tearDown()

        # Second time
        # Launch the experiment
        self.run_test(exp_cmd)

        # Clean up the running experiment
        self.tearDown()

        # Third time
        self.run_test(exp_cmd)
