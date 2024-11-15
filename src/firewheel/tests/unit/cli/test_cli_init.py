import io
import copy
import tempfile
import unittest
import unittest.mock

import pytest

from firewheel.config import Config
from firewheel.cli.init_firewheel import InitFirewheel


# pylint: disable=protected-access
class CliInitTestCase(unittest.TestCase):
    def setUp(self):
        # Create a helper directory
        # pylint: disable=consider-using-with
        self.tmp_dir = tempfile.TemporaryDirectory()

        # Change the CLI settings
        self.fw_config = Config(writable=True)
        self.old_config = copy.deepcopy(self.fw_config.get_config())

    def tearDown(self):
        # remove the temp directory
        self.tmp_dir.cleanup()

        # Fix the config
        self.fw_config.set_config(self.old_config)
        self.fw_config.write()

    def test_check_discovery(self):
        cli = InitFirewheel()
        self.assertTrue(cli._check_discovery())

    @pytest.mark.long
    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_check_discovery_fail(self, mock_stdout):
        new_host = "asdf"
        old_setting = self.old_config["discovery"]["hostname"]

        tmp_config = copy.deepcopy(self.fw_config.get_config())
        tmp_config["discovery"]["hostname"] = new_host

        self.assertNotEqual(old_setting, new_host)

        self.fw_config.set_config(tmp_config)
        self.fw_config.write()

        cli = InitFirewheel()

        new_config = Config().get_config()
        self.assertEqual(new_config["discovery"]["hostname"], new_host)

        self.assertFalse(cli._check_discovery())

        msg = "ERROR: The Discovery service"
        self.assertIn(msg, mock_stdout.getvalue())

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_check_discovery_wrapper_not_headnode(self, mock_stdout):
        cli = InitFirewheel()

        with unittest.mock.patch("firewheel.lib.minimega.api.minimegaAPI") as mock:
            instance = mock.return_value
            instance.get_am_head_node.return_value = False
            cli._check_discovery_wrapper()

        msg = "Not checking discovery"
        self.assertIn(msg, mock_stdout.getvalue())

        msg = "Checking discovery"
        self.assertNotIn(msg, mock_stdout.getvalue())

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_check_discovery_wrapper(self, mock_stdout):
        cli = InitFirewheel()
        cli._check_discovery_wrapper()

        msg = "Checking discovery"
        self.assertIn(msg, mock_stdout.getvalue())

        msg = "OK"
        self.assertIn(msg, mock_stdout.getvalue())

        msg = "FAIL"
        self.assertNotIn(msg, mock_stdout.getvalue())
