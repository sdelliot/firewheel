from firewheel.tests.functional.router_tree_testcase import RouterTreeTestCase


class WindowsRouterTreeTestCase(RouterTreeTestCase):
    """
    This class creates a flat star topology to ensure 1) connectivity
    with all the nodes of the FIREWHEEL cluster 2) ensure connectivity of all the
    VMs within the experiment (assuming they should be connected) and 3)
    that all the NICs/networks expected in the experiment are created correctly.

    The host VMs will all be Windows 7 rather than Ubuntu.
    """

    def test_ping_all_router_tree_50(self):
        """
        This test case launches `windowstests.router_tree` and ensures
        that all the nodes are correctly configured. This tests
        basic connectivity between non-routers in the experiment
        and can be run whenever a new cluster is set up.

        This experiment connects router_tree with a degree of 50.
        """
        degree = 50

        exp_cmd = [
            "firewheel",
            "experiment",
            f"windowstests.router_tree:{degree}",
            "tests.ping_all:False",
            f"{self.launch_mc}",
        ]

        self.run_test(exp_cmd)
