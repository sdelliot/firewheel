# pylint: disable=invalid-name

import os
import shutil
import tempfile
import unittest

import jinja2
from jinja2 import Environment, StrictUndefined, FileSystemLoader

from firewheel.control.utils.new_model_component import PythonModule


class TestPythonModule(unittest.TestCase):
    def setUp(self):
        self.base_dir = tempfile.mkdtemp()

        self.template_dir = os.path.join(self.base_dir, "templates")
        os.makedirs(self.template_dir, exist_ok=True)
        loader = FileSystemLoader(self.template_dir, followlinks=True)
        self.jinja_env = Environment(loader=loader, autoescape=True)
        self.jinja_env.undefined = StrictUndefined

    def tearDown(self):
        shutil.rmtree(self.base_dir)

    def test_non_env(self):
        with self.assertRaises(ValueError) as assertion:
            PythonModule("string")

        exception_message = assertion.exception.args[0]
        self.assertTrue("jinja2.Environment" in exception_message)

    def test_module_no_template(self):
        pm = PythonModule(self.jinja_env)
        pm.module_name = "test"
        pm.base_path = self.base_dir

        pm.create_module()
        with open(os.path.join(self.base_dir, "test.py"), encoding="utf8") as output:
            contents = output.read()
        self.assertEqual(contents, "# TODO: Write code here.")  # noqa: T101

    def test_module_unwritable_base_path(self):
        pm = PythonModule(self.jinja_env)

        with self.assertRaises(ValueError) as assertion:
            pm.base_path = "/fake"
        exp_msg = assertion.exception.args[0]
        self.assertEqual("Specified path is invalid or not writable.", exp_msg)

    def test_module_no_base_path(self):
        pm = PythonModule(self.jinja_env)
        pm.module_name = "test"

        with self.assertRaises(ValueError) as assertion:
            pm.create_module()
        exp_msg = assertion.exception.args[0]
        self.assertEqual("Must specify a base path.", exp_msg)

    def test_module_no_module_name(self):
        pm = PythonModule(self.jinja_env)
        pm.base_path = self.base_dir

        pre_len = len(os.listdir(self.base_dir))
        with self.assertRaises(ValueError) as assertion:
            pm.create_module()
        post_len = len(os.listdir(self.base_dir))

        self.assertEqual(pre_len, post_len)
        self.assertFalse(os.path.isfile(os.path.join(self.base_dir, "None.py")))

        exp_msg = assertion.exception.args[0]
        self.assertEqual("Must specify a module name.", exp_msg)

    def test_module_template(self):
        pm = PythonModule(self.jinja_env)

        with open(
            os.path.join(self.template_dir, "test_template"), "w", encoding="utf8"
        ) as template:
            template.write("class {{ class_name }}")

        pm.base_path = self.base_dir
        pm.module_name = "test"
        pm.class_name = "Foo"
        pm.module_template = "test_template"

        pm.create_module()

        with open(
            os.path.join(self.base_dir, "test.py"), "r", encoding="utf8"
        ) as output:
            contents = output.read()
        self.assertEqual(contents, "class Foo")

    def test_module_template_no_class_name(self):
        pm = PythonModule(self.jinja_env)

        template_path = os.path.join(self.template_dir, "test_template")
        with open(template_path, "w", encoding="utf8") as template:
            template.write("class {{ class_name }}")

        pm.base_path = self.base_dir
        pm.doc_module_name = "test"
        pm.module_name = "test_module"
        pm.module_template = "test_template"

        with self.assertRaises(jinja2.exceptions.UndefinedError):
            pm.create_module()

    def test_module_custom_var(self):
        pm = PythonModule(self.jinja_env)

        template_path = os.path.join(self.template_dir, "test_template")
        with open(template_path, "w", encoding="utf8") as template:
            template.write("{{custom_var}}")

        pm.base_path = self.base_dir
        pm.module_name = "test"
        pm.module_template = "test_template"

        pm.create_module(other_vars={"custom_var": "value"})

        with open(
            os.path.join(pm.base_path, pm.module_relpath, "test.py"),
            "r",
            encoding="utf8",
        ) as result:
            contents = result.read()
        self.assertEqual(contents, "value")

    def test_base_path_property(self):
        pm = PythonModule(self.jinja_env)

        with self.assertRaises(ValueError) as assertion:
            self.assertEqual(pm.base_path, None)
        exp_msg = assertion.exception.args[0]
        self.assertEqual("Must specify a base path.", exp_msg)

        invalid_path_msg = "Specified path is invalid or not writable."
        with self.assertRaises(ValueError) as assertion:
            pm.base_path = {}
        exp_msg = assertion.exception.args[0]
        self.assertEqual(invalid_path_msg, exp_msg)

        # Base path doesn't need to be portable, so 'random:colon' or similar is
        # fine (if it passes validation, which it will on Linux).
        # We just don't bother testing.

        valid_win_path = "C:\\Users\\Public"
        pm.base_path = valid_win_path
        self.assertEqual(pm.base_path, valid_win_path)

        pm.base_path = os.path.join(self.base_dir, "deep", "deep", "deep", "nesting")

    def test_module_name(self):
        pm = PythonModule(self.jinja_env)

        def assert_none_error():
            with self.assertRaises(ValueError) as assertion:
                self.assertEqual(pm.module_name, None)
            exp_msg = assertion.exception.args[0]
            self.assertEqual("Must specify a module name.", exp_msg)

        assert_none_error()
        with self.assertRaises(ValueError) as assertion:
            pm.module_name = "invalid-name"
        exp_msg = assertion.exception.args[0]
        self.assertEqual("Must specify a valid Python module name.", exp_msg)

        assert_none_error()

        pm.module_name = "valid_name"
        self.assertEqual(pm.module_name, "valid_name")

    def test_module_relpath(self):
        pm = PythonModule(self.jinja_env)

        self.assertEqual(pm.module_relpath, "")

        pm.module_relpath = "valid/path with/spaces"
        self.assertEqual(pm.module_relpath, "valid/path with/spaces")

        with self.assertRaises(ValueError) as assertion:
            # This should raise an error and is not a security issue
            pm.module_relpath = "/tmp/foo"  # nosec
        exp_msg = assertion.exception.args[0]
        self.assertEqual(exp_msg, "Module relpath must be relative.")

        pm.module_relpath = "foo/../bar"
        self.assertEqual(pm.module_relpath, "foo/../bar")

    def test_module_template_property(self):
        pm = PythonModule(self.jinja_env)

        self.assertEqual(pm.module_template, None)

        with self.assertRaises(ValueError) as assertion:
            pm.module_template = os.path.join(self.template_dir, "invalid")
        exp_msg = assertion.exception.args[0]
        self.assertEqual("Must specify a module template file that exists.", exp_msg)

        test_template_path = os.path.join(self.template_dir, "test_template")
        with open(test_template_path, "w", encoding="utf8") as f:
            f.write("test")

        pm.module_template = "test_template"
        self.assertEqual(pm.module_template, "test_template")

        pm.module_template = None
        self.assertEqual(pm.module_template, None)

    def test_module_exists(self):
        pm = PythonModule(self.jinja_env)

        with open(
            os.path.join(self.template_dir, "test_template"), "w", encoding="utf8"
        ) as template:
            template.write("class {{ class_name }}")

        pm.base_path = self.base_dir
        pm.module_name = "test"
        pm.class_name = "Foo"
        pm.module_template = "test_template"

        self.assertFalse(pm.module_exists())
        pm.create_module()
        self.assertTrue(pm.module_exists())

    def test_module_exists_nested(self):
        pm = PythonModule(self.jinja_env)

        with open(
            os.path.join(self.template_dir, "test_template"), "w", encoding="utf8"
        ) as template:
            template.write("class {{ class_name }}")

        pm.base_path = self.base_dir
        pm.module_name = "test"
        pm.module_relpath = "deeply/nested"
        pm.class_name = "Foo"
        pm.module_template = "test_template"

        self.assertFalse(pm.module_exists())
        pm.create_module()
        self.assertTrue(pm.module_exists())
