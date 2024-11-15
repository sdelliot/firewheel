import os
import copy
import decimal
import tempfile
import unittest

from firewheel.config import Config
from firewheel.lib.log import Log
from firewheel.cli.helper import Helper
from firewheel.cli.section import MalformedSectionError
from firewheel.cli.host_accessor import sync


class CliHelperTestCase(unittest.TestCase):
    def setUp(self):
        # Create a helper directory
        # pylint: disable=consider-using-with
        self.helper_root = tempfile.TemporaryDirectory()
        # pylint: disable=consider-using-with
        self.helper_cache = tempfile.TemporaryDirectory()

        self.helper_name = "valid"
        self.author = "Unittest"
        self.description = "Testing this case."
        self.touch_file = "testing"
        self.run = f"touch {os.path.join(self.helper_root.name, self.touch_file)}"
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )
        with open(
            os.path.join(self.helper_root.name, self.helper_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

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

        # Fix the config
        self.fw_config.set_config(self.old_config)
        self.fw_config.write()

    def test_normal_read_sections(self):
        helper = Helper(self.helper_name, self.helper_root.name)

        # Check all the sections
        self.assertEqual(helper["AUTHOR"].format_content().strip(), self.author)
        self.assertEqual(
            helper["DESCRIPTION"].format_content().strip(), self.description
        )

        # Check the RUN section(s)
        self.assertEqual(helper["RUN"][0].format_content().strip(), self.run)

    def test_unordered_sections(self):
        helper = str(
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        # Check all the sections
        self.assertEqual(helper["AUTHOR"].format_content().strip(), self.author)
        self.assertEqual(
            helper["DESCRIPTION"].format_content().strip(), self.description
        )

        # Check the RUN section(s)
        self.assertEqual(helper["RUN"][0].format_content().strip(), self.run)

    def test_missing_run_done(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
        )

        name = "invalid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        with self.assertRaises(MalformedSectionError):
            helper = Helper(name, self.helper_root.name)

    def test_missing_author_done(self):
        helper = str(
            f"AUTHOR\n{self.author}\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "invalid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        with self.assertRaises(MalformedSectionError):
            helper = Helper(name, self.helper_root.name)

    def test_missing_author_section(self):
        helper = str(
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "invalid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        with self.assertRaises(MalformedSectionError):
            helper = Helper(name, self.helper_root.name)

    def test_missing_description_section(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "invalid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        with self.assertRaises(MalformedSectionError):
            helper = Helper(name, self.helper_root.name)

    def test_missing_run_section(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n" f"DESCRIPTION\n{self.description}\nDONE\n"
        )

        name = "invalid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        with self.assertRaises(MalformedSectionError):
            helper = Helper(name, self.helper_root.name)

    def test_run_too_long(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell test extra words ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        # Check all the sections
        self.assertEqual(helper["AUTHOR"].format_content().strip(), self.author)
        self.assertEqual(
            helper["DESCRIPTION"].format_content().strip(), self.description
        )

        # Check the RUN section(s)
        self.assertEqual(helper["RUN"][0].format_content().strip(), self.run)

    def test_run_too_short(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "invalid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        with self.assertRaises(MalformedSectionError):
            helper = Helper(name, self.helper_root.name)

    def test_run_no_on(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell via control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "invalid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        with self.assertRaises(MalformedSectionError):
            helper = Helper(name, self.helper_root.name)

    def test_new_section(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"UNKNOWN\nInteresting section\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        # Check all the sections
        self.assertEqual(helper["AUTHOR"].format_content().strip(), self.author)
        self.assertTrue("UNKNOWN" in helper)
        self.assertEqual(
            helper["UNKNOWN"].format_content().strip(), "Interesting section"
        )
        self.assertEqual(
            helper["DESCRIPTION"].format_content().strip(), self.description
        )

        # Check the RUN section(s)
        self.assertEqual(helper["RUN"][0].format_content().strip(), self.run)

    def test_blank_line(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
            "\n\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        # Check all the sections
        self.assertEqual(helper["AUTHOR"].format_content().strip(), self.author)
        self.assertEqual(
            helper["DESCRIPTION"].format_content().strip(), self.description
        )

        # Check the RUN section(s)
        self.assertEqual(helper["RUN"][0].format_content().strip(), self.run)

    def test_run_normal(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        # Check the RUN section(s)
        self.assertEqual(helper["RUN"][0].format_content().strip(), self.run)

        session = {"sequence_number": 0}
        # Need to sync first
        sync(session, helper_list={name: helper})
        helper.run(session, None)

        # Check if the file exists
        self.assertTrue(
            os.path.exists(os.path.join(self.helper_root.name, self.touch_file))
        )

    def test_multi_run_normal(self):
        run_f1 = "test1"
        run_f2 = "test2"
        run_f3 = "test3"

        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f1)}\n"
            "DONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f3)}\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        session = {"sequence_number": 0}
        # Need to sync first
        sync(session, helper_list={name: helper})

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        results = helper.run(session, None)

        self.assertEqual(results, 0)

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.6"))

        # Check if the files exists
        self.assertTrue(os.path.exists(os.path.join(self.helper_root.name, run_f1)))
        self.assertTrue(os.path.exists(os.path.join(self.helper_root.name, run_f2)))
        self.assertTrue(os.path.exists(os.path.join(self.helper_root.name, run_f3)))

    def test_del_run_section(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        session = {"sequence_number": 0}

        # Need to sync first
        sync(session, helper_list={name: helper})

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        with self.assertRaises(MalformedSectionError):
            del helper.sections["RUN"]
            helper.run(session, None)

    def test_failed_run(self):
        run_f2 = "test2"

        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            "exit 1\n"
            "DONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, run_f2)}\n"
            "DONE\n"
            "RUN Shell ON control\n"
            "exit 1\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        session = {"sequence_number": 0}
        # Need to sync first
        sync(session, helper_list={name: helper})

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        results = helper.run(session, None)

        # Two of the commands should have failed
        self.assertEqual(results, 2)

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.6"))

        # Check if the files exists
        self.assertTrue(os.path.exists(os.path.join(self.helper_root.name, run_f2)))

    def test_build_cache_create_dirs_default_path(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        # Build the cache
        test_dir = "new/cache"
        new_cache = os.path.join(self.helper_cache.name, test_dir)

        self.assertFalse(os.path.exists(new_cache))

        helper.build_cache(path=new_cache)

        self.assertTrue(os.path.exists(new_cache))

    def test_build_cache_create_dirs(self):
        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        # Build the cache
        test_dir = "new/cache"
        new_cache = os.path.join(self.helper_cache.name, test_dir)

        self.fw_config.resolve_set(
            "cli.cache_dir",
            os.path.join(os.path.basename(self.helper_cache.name), test_dir),
        )
        self.fw_config.write()

        self.assertFalse(os.path.exists(new_cache))

        helper.build_cache()

        self.assertTrue(os.path.exists(new_cache))

    def test_build_cache_bad_group(self):
        self.fw_config.resolve_set("logging.root_dir", self.helper_cache.name)
        self.fw_config.write()

        # Create a log file path
        log_file = os.path.join(
            self.helper_cache.name, self.old_config["logging"]["firewheel_log"]
        )

        helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"{self.run}\n"
            "DONE\n"
        )

        name = "valid2"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper)

        helper = Helper(name, self.helper_root.name)

        # Reset the logger
        helper.log.handlers = []
        helper.log = Log(name="CLI", log_file=log_file).log

        # Build the cache
        test_dir = "new/cache"
        new_cache = os.path.join(self.helper_cache.name, test_dir)

        self.assertFalse(os.path.exists(new_cache))
        bad_group = "asdfasdf"
        self.fw_config.resolve_set("system.default_group", bad_group)
        self.fw_config.write()

        msg = "Not setting group on local Helper cache directory"

        # Check that the FW log does not yet have the message
        with open(log_file, "r", encoding="utf8") as fhand:
            lines = fhand.read()
        self.assertNotIn(msg, lines)

        helper.build_cache(path=new_cache)

        self.assertTrue(os.path.exists(new_cache))

        with open(log_file, "r", encoding="utf8") as fhand:
            lines = fhand.read()
        self.assertIn(msg, lines)

        # Reset the logger
        helper.log.handlers = []
