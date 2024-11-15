import io
import os
import copy
import decimal
import tempfile
import unittest
import unittest.mock

from firewheel.config import Config
from firewheel.cli.helper import Helper
from firewheel.cli.host_accessor import sync
from firewheel.cli.executors.helpers import Helpers
from firewheel.cli.executable_section import ExecutableSection


class CliExecutorsTestCase(unittest.TestCase):
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

        # Fix the config
        self.fw_config.set_config(self.old_config)
        self.fw_config.write()

    def test_get_extension(self):
        content = ["multi", "line"]
        arguments = ["Shell", ["control", "compute"]]
        section = ExecutableSection(content, arguments)
        self.assertEqual(section.get_file_extension(), ".sh")

        arguments = ["Helpers", ["control", "compute"]]
        section = ExecutableSection(content, arguments)
        self.assertEqual(section.get_file_extension(), "")

        arguments = ["Python", ["control", "compute"]]
        section = ExecutableSection(content, arguments)
        self.assertEqual(section.get_file_extension(), ".py")

        arguments = ["LocalPython", ["control", "compute"]]
        section = ExecutableSection(content, arguments)
        self.assertEqual(section.get_file_extension(), ".py")

    def test_normal_shell(self):
        touch_file = "test1"

        helper_str = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, touch_file)}\n"
            "DONE\n"
        )

        name = "valid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper_str)

        helper = Helper(name, self.helper_root.name)

        session = {"sequence_number": 0}

        # Need to sync first
        sync(session, helper_list={name: helper})

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        results = helper.run(session, None)

        self.assertEqual(results, 0)

        # Check if the files exists
        self.assertTrue(os.path.exists(os.path.join(self.helper_root.name, touch_file)))

    def test_normal_local_python(self):
        touch_file = "test1"

        helper_str = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN LocalPython ON control\n"
            f"with open('{os.path.join(self.helper_root.name, touch_file)}', 'w') as f:\n"
            "    f.write('testing')\n"
            "DONE\n"
        )

        name = "valid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper_str)

        helper = Helper(name, self.helper_root.name)

        session = {"sequence_number": 0}

        # Need to sync first
        sync(session, helper_list={name: helper})

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        results = helper.run(session, None)

        self.assertEqual(results, 0)

        # Check if the files exists
        self.assertTrue(os.path.exists(os.path.join(self.helper_root.name, touch_file)))

    def test_args_local_python(self):
        touch_file = "test1"

        helper_str = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN LocalPython ON control\n"
            "import os\n"
            "import sys\n"
            f"base='{self.helper_root.name}'\n"
            f"full_path=os.path.join(base, sys.argv[1])\n"
            f"with open(full_path, 'w') as f:\n"
            "    f.write('testing')\n"
            "DONE\n"
        )

        name = "valid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper_str)

        helper = Helper(name, self.helper_root.name)

        session = {"sequence_number": 0}

        # Need to sync first
        sync(session, helper_list={name: helper})

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        results = helper.run(session, [touch_file])

        self.assertEqual(results, 0)

        # Check if the files exists
        self.assertTrue(os.path.exists(os.path.join(self.helper_root.name, touch_file)))

    def test_normal_python(self):
        touch_file = "test1"

        helper_str = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Python ON control\n"
            f"with open('{os.path.join(self.helper_root.name, touch_file)}', 'w') as f:\n"
            "    f.write('testing')\n"
            "DONE\n"
        )

        name = "valid"
        with open(
            os.path.join(self.helper_root.name, name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(helper_str)

        helper = Helper(name, self.helper_root.name)

        session = {"sequence_number": 0}

        # Need to sync first
        sync(session, helper_list={name: helper})

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        results = helper.run(session, None)

        self.assertEqual(results, 0)

        # Check if the files exists
        self.assertTrue(os.path.exists(os.path.join(self.helper_root.name, touch_file)))

    def test_normal_helpers(self):
        touch_file_1 = "test1"
        touch_file_2 = "test2"

        shell_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, touch_file_1)}\n"
            "DONE\n"
        )

        python_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN LocalPython ON control\n"
            f"with open('{os.path.join(self.helper_root.name, touch_file_2)}', 'w') as f:\n"
            "    f.write('testing')\n"
            "DONE\n"
        )

        help_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Helpers ON control\n"
            "valid_sh\n"
            "valid_py\n"
            "DONE\n"
        )

        shell_name = "valid_sh"
        python_name = "valid_py"
        helper_name = "valid_help"

        with open(
            os.path.join(self.helper_root.name, shell_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(shell_helper)

        with open(
            os.path.join(self.helper_root.name, python_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(python_helper)

        with open(
            os.path.join(self.helper_root.name, helper_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(help_helper)

        helper_sh = Helper(shell_name, self.helper_root.name)
        helper_py = Helper(python_name, self.helper_root.name)
        helper = Helper(helper_name, self.helper_root.name)

        session = {"sequence_number": 0}

        helper_dict = {
            helper_name: helper,
            shell_name: helper_sh,
            python_name: helper_py,
        }

        # Need to sync first
        sync(session, helper_list=helper_dict)

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        helpers_obj = Helpers(["control"], ["valid_sh", "valid_py"], helper_dict)

        results = helpers_obj.execute(None, session, None)

        self.assertEqual(results, 0)

        # Check if the files exists
        self.assertTrue(
            os.path.exists(os.path.join(self.helper_root.name, touch_file_1))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.helper_root.name, touch_file_2))
        )

    def test_not_found_helpers(self):
        touch_file_1 = "test1"

        shell_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            f"touch {os.path.join(self.helper_root.name, touch_file_1)}\n"
            "DONE\n"
        )

        help_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Helpers ON control\n"
            "invalid\n"
            "valid_sh\n"
            "DONE\n"
        )

        shell_name = "valid_sh"
        helper_name = "valid_help"

        with open(
            os.path.join(self.helper_root.name, shell_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(shell_helper)

        with open(
            os.path.join(self.helper_root.name, helper_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(help_helper)

        helper_sh = Helper(shell_name, self.helper_root.name)
        helper = Helper(helper_name, self.helper_root.name)

        session = {"sequence_number": 0}

        helper_dict = {helper_name: helper, shell_name: helper_sh}

        # Need to sync first
        sync(session, helper_list=helper_dict)

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        helpers_obj = Helpers(["control"], ["invalid", "valid_sh"], helper_dict)

        results = helpers_obj.execute(None, session, None)

        self.assertEqual(results, 1)

        # Check if the files exists
        self.assertTrue(
            os.path.exists(os.path.join(self.helper_root.name, touch_file_1))
        )

    def test_with_arguments(self):
        touch_file_1 = "test1"

        python_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN LocalPython ON control\n"
            "import os\n"
            "import sys\n"
            f"base='{self.helper_root.name}'\n"
            f"full_path=os.path.join(base, sys.argv[1])\n"
            f"with open(full_path, 'w') as f:\n"
            "    f.write('testing')\n"
            "DONE\n"
        )

        help_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Helpers ON control\n"
            f"valid_py {touch_file_1}\n"
            "DONE\n"
        )

        python_name = "valid_py"
        helper_name = "valid_help"

        with open(
            os.path.join(self.helper_root.name, python_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(python_helper)

        with open(
            os.path.join(self.helper_root.name, helper_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(help_helper)

        helper_py = Helper(python_name, self.helper_root.name)
        helper = Helper(helper_name, self.helper_root.name)

        session = {"sequence_number": 0}

        helper_dict = {helper_name: helper, python_name: helper_py}

        # Need to sync first
        sync(session, helper_list=helper_dict)

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        helpers_obj = Helpers(["control"], ["valid_py"], helper_dict)

        results = helpers_obj.execute(None, session, [touch_file_1])

        self.assertEqual(results, 0)

        # Check if the files exists
        self.assertTrue(
            os.path.exists(os.path.join(self.helper_root.name, touch_file_1))
        )

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_helper_error(self, mock_stdout):
        touch_file_2 = "test2"

        shell_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Shell ON control\n"
            "exit 1\n"
            "DONE\n"
        )

        python_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN LocalPython ON control\n"
            f"with open('{os.path.join(self.helper_root.name, touch_file_2)}', 'w') as f:\n"
            "    f.write('testing')\n"
            "DONE\n"
        )

        help_helper = str(
            f"AUTHOR\n{self.author}\nDONE\n"
            f"DESCRIPTION\n{self.description}\nDONE\n"
            "RUN Helpers ON control\n"
            "valid_sh\n"
            "valid_py\n"
            "DONE\n"
        )

        shell_name = "valid_sh"
        python_name = "valid_py"
        helper_name = "valid_help"

        with open(
            os.path.join(self.helper_root.name, shell_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(shell_helper)

        with open(
            os.path.join(self.helper_root.name, python_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(python_helper)

        with open(
            os.path.join(self.helper_root.name, helper_name), "w", encoding="utf8"
        ) as fhand:
            fhand.write(help_helper)

        helper_sh = Helper(shell_name, self.helper_root.name)
        helper_py = Helper(python_name, self.helper_root.name)
        helper = Helper(helper_name, self.helper_root.name)

        session = {"sequence_number": 0}

        helper_dict = {
            helper_name: helper,
            shell_name: helper_sh,
            python_name: helper_py,
        }

        # Need to sync first
        sync(session, helper_list=helper_dict)

        # Check that the sequence_number increased
        self.assertEqual(session["sequence_number"], decimal.Decimal("0.3"))

        helpers_obj = Helpers(["control"], ["valid_sh", "valid_py"], helper_dict)

        results = helpers_obj.execute(None, session, None)

        self.assertEqual(results, 1)

        # Check if the files exists
        self.assertTrue(
            os.path.exists(os.path.join(self.helper_root.name, touch_file_2))
        )
        self.assertIn("Continuing", mock_stdout.getvalue())
