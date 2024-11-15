import os
import copy
import tempfile
import unittest

from firewheel.config import Config
from firewheel.lib.log import Log
from firewheel.cli.helper import Helper
from firewheel.cli.helper_group import HelperGroup


class CliHelperGroupTestCase(unittest.TestCase):
    def setUp(self):
        # Create a helper directory
        # pylint: disable=consider-using-with
        self.helper_root = tempfile.TemporaryDirectory()
        # pylint: disable=consider-using-with
        self.helper_cache = tempfile.TemporaryDirectory()

        self.author = "Unittest"
        self.description = "Testing this case."

        # Change the CLI settings
        self.fw_config = Config(writable=True)
        self.old_config = copy.deepcopy(self.fw_config.get_config())
        self.fw_config.resolve_set(
            "cli.root_dir", os.path.dirname(self.helper_cache.name)
        )
        self.fw_config.resolve_set(
            "cli.cache_dir", os.path.basename(self.helper_cache.name)
        )
        self.fw_config.write()

    def tearDown(self):
        # remove the temp directory
        self.helper_root.cleanup()
        self.helper_cache.cleanup()

        # Fix the config
        self.fw_config.set_config(self.old_config)
        self.fw_config.write()

    def test_get_keys(self):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create HelperGroup dict
        helper_group = HelperGroup(index_path)
        index_helper_obj = Helper("index", index_path)
        helpers = {
            helper_name: Helper(helper_name, index_path),
            "index": index_helper_obj,
        }
        helper_group.helpers = helpers

        self.assertEqual({"index", helper_name}, set(helper_group.keys()))

    def test_build_cache_create_dirs_default_path(self):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create HelperGroup dict
        helper_group = HelperGroup(index_path)
        index_helper_obj = Helper("index", index_path)
        helpers = {
            helper_name: Helper(helper_name, index_path),
            "index": index_helper_obj,
        }
        helper_group.helpers = helpers

        # Build the cache
        test_dir = "new/cache"
        new_cache = os.path.join(self.helper_cache.name, test_dir)

        self.assertFalse(os.path.exists(new_cache))

        helper_group.build_cache(path=new_cache)

        self.assertTrue(os.path.exists(new_cache))

    def test_build_cache_create_dirs(self):
        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create HelperGroup dict
        helper_group = HelperGroup(index_path)
        index_helper_obj = Helper("index", index_path)
        helpers = {
            helper_name: Helper(helper_name, index_path),
            "index": index_helper_obj,
        }
        helper_group.helpers = helpers

        # Build the cache
        test_dir = "new/cache"
        new_cache = os.path.join(self.helper_cache.name, test_dir)

        self.fw_config.resolve_set(
            "cli.cache_dir",
            os.path.join(os.path.basename(self.helper_cache.name), test_dir),
        )
        self.fw_config.write()

        self.assertFalse(os.path.exists(new_cache))

        helper_group.build_cache()

        self.assertTrue(os.path.exists(new_cache))

    def test_build_cache_bad_group(self):
        self.fw_config.resolve_set("logging.root_dir", self.helper_cache.name)
        self.fw_config.write()

        # Create a log file path
        log_file = os.path.join(
            self.helper_cache.name, self.old_config["logging"]["firewheel_log"]
        )

        # Create a directory in the temp directory
        index_name = "testing"
        index_path = os.path.join(self.helper_root.name, index_name)
        os.makedirs(index_path)

        run_f1 = "test1"
        run_f2 = "test2"

        # Add an index helper
        helper_index = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "index"), "w", encoding="utf8") as fhand:
            fhand.write(helper_index)

        # Add a regular helper
        helper_name = "normal"
        helper_regular = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
        )

        with open(os.path.join(index_path, "normal"), "w", encoding="utf8") as fhand:
            fhand.write(helper_regular)

        # Create HelperGroup dict
        helper_group = HelperGroup(index_path)
        index_helper_obj = Helper("index", index_path)
        helpers = {
            helper_name: Helper(helper_name, index_path),
            "index": index_helper_obj,
        }
        helper_group.helpers = helpers

        # Reset the logger
        helper_group.log.handlers = []
        helper_group.log = Log(name="CLI", log_file=log_file).log

        # Build the cache
        test_dir = "new/cache"
        new_cache = os.path.join(self.helper_cache.name, test_dir)

        self.assertFalse(os.path.exists(new_cache))
        bad_group = "asdfasdf"
        self.fw_config.resolve_set("system.default_group", bad_group)
        self.fw_config.write()

        msg = "Not setting group on local Helper cache"

        # Check that the FW log does not yet have the message
        with open(log_file, "r", encoding="utf8") as fhand:
            lines = fhand.read()
        self.assertNotIn(msg, lines)

        helper_group.build_cache(path=new_cache)

        self.assertTrue(os.path.exists(new_cache))

        with open(log_file, "r", encoding="utf8") as fhand:
            lines = fhand.read()
        self.assertIn(msg, lines)

        # Reset the logger
        helper_group.log.handlers = []
