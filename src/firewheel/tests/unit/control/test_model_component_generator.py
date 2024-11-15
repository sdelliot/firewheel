# pylint: disable=invalid-name

import os
import shutil
import argparse
import tempfile
import unittest

import yaml

from firewheel.control.utils.new_model_component import (
    ModelComponentGenerator,
    python_file,
)


class TestModelComponentGenerator(unittest.TestCase):
    def setUp(self):
        self.base_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.base_dir)

    def test_non_string_name_init(self):
        with self.assertRaises(TypeError) as assertion:
            ModelComponentGenerator("", {})

        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("ModelComponent name"))

    def test_basic_init(self):
        mcg = ModelComponentGenerator("path", "name")
        self.assertTrue(isinstance(mcg, ModelComponentGenerator))

    def test_get_name(self):
        mcg = ModelComponentGenerator("path", "name")
        self.assertEqual(mcg.name, "name", "path")

    def test_no_default_name(self):
        mcg = ModelComponentGenerator("path", "name")
        del mcg._name
        with self.assertRaises(AttributeError):
            # pylint: disable=pointless-statement
            mcg.name

    def test_default_attribute_depends(self):
        mcg = ModelComponentGenerator("path", "name")
        default_deps = mcg.attribute_depends
        self.assertEqual(default_deps, [])

    def test_single_attribute_depends(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.attribute_depends = "attr"
        self.assertEqual(mcg.attribute_depends, ["attr"])

        mcg.attribute_depends = "test"
        self.assertEqual(mcg.attribute_depends, ["test"])

    def test_attribute_depends_as_list(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.attribute_depends = ["attr1", "attr2"]
        self.assertEqual(mcg.attribute_depends, ["attr1", "attr2"])

        mcg.attribute_depends = ["test1", "test2"]
        self.assertEqual(mcg.attribute_depends, ["test1", "test2"])

    def test_non_string_attribute_depends(self):
        mcg = ModelComponentGenerator("path", "name")

        with self.assertRaises(TypeError) as assertion:
            mcg.attribute_depends = {}
        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("ModelComponent must depend"))
        self.assertTrue("list of string attr" in exception_message)

        with self.assertRaises(TypeError) as assertion:
            mcg.attribute_depends = [{}]
        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("Attribute depends"))
        self.assertTrue("list of strings." in exception_message)

    def test_default_attribute_provides(self):
        mcg = ModelComponentGenerator("path", "name")
        default_provides = mcg.attribute_provides
        self.assertEqual(default_provides, [])

    def test_single_attribute_provides(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.attribute_provides = "attr"
        self.assertEqual(mcg.attribute_provides, ["attr"])

        mcg.attribute_provides = "test"
        self.assertEqual(mcg.attribute_provides, ["test"])

    def test_attribute_provides_as_list(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.attribute_provides = ["attr1", "attr2"]
        self.assertEqual(mcg.attribute_provides, ["attr1", "attr2"])

        mcg.attribute_provides = ["test1", "test2"]
        self.assertEqual(mcg.attribute_provides, ["test1", "test2"])

    def test_non_string_attribute_provides(self):
        mcg = ModelComponentGenerator("path", "name")

        with self.assertRaises(TypeError) as assertion:
            mcg.attribute_provides = {}
        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("ModelComponent must provide"))
        self.assertTrue("one or a list of string" in exception_message)

        with self.assertRaises(TypeError) as assertion:
            mcg.attribute_provides = [{}]
        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("Attribute provides"))
        self.assertTrue("must be a list of strings" in exception_message)

    def test_default_attribute_precedes(self):
        mcg = ModelComponentGenerator("path", "name")
        default_deps = mcg.attribute_precedes
        self.assertEqual(default_deps, [])

    def test_single_attribute_precedes(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.attribute_precedes = "attr"
        self.assertEqual(mcg.attribute_precedes, ["attr"])

        mcg.attribute_precedes = "test"
        self.assertEqual(mcg.attribute_precedes, ["test"])

    def test_attribute_precedes_as_list(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.attribute_precedes = ["attr1", "attr2"]
        self.assertEqual(mcg.attribute_precedes, ["attr1", "attr2"])

        mcg.attribute_precedes = ["test1", "test2"]
        self.assertEqual(mcg.attribute_precedes, ["test1", "test2"])

    def test_non_string_attribute_precedes(self):
        mcg = ModelComponentGenerator("path", "name")

        with self.assertRaises(TypeError) as assertion:
            mcg.attribute_precedes = {}
        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("ModelComponent must precede"))
        self.assertTrue("list of string attr" in exception_message)

        with self.assertRaises(TypeError) as assertion:
            mcg.attribute_precedes = [{}]
        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("Attribute precedes"))
        self.assertTrue("list of strings." in exception_message)

    def test_default_model_component_depends(self):
        mcg = ModelComponentGenerator("path", "name")
        default_mcd = mcg.model_component_depends
        self.assertEqual(default_mcd, [])

    def test_single_model_component_depends(self):
        mcg = ModelComponentGenerator("path", "name")

        mcg.model_component_depends = "mc1"
        self.assertEqual(mcg.model_component_depends, ["mc1"])

        mcg.model_component_depends = "mc2"
        self.assertEqual(mcg.model_component_depends, ["mc2"])

    def test_model_component_depends_as_list(self):
        mcg = ModelComponentGenerator("path", "name")

        mcg.model_component_depends = ["mc1", "mc2"]
        self.assertEqual(mcg.model_component_depends, ["mc1", "mc2"])

        mcg.model_component_depends = ["test1", "test2"]
        self.assertEqual(mcg.model_component_depends, ["test1", "test2"])

    def test_non_string_model_component_depends(self):
        mcg = ModelComponentGenerator("path", "name")

        with self.assertRaises(TypeError) as assertion:
            mcg.model_component_depends = {}
        exception_message = assertion.exception.args[0]
        self.assertTrue(
            exception_message.startswith("Model Component dependencies must provide")
        )
        self.assertTrue("one or a list of string" in exception_message)

        with self.assertRaises(TypeError) as assertion:
            mcg.model_component_depends = [{}]
        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("Model Component dependencies"))
        self.assertTrue("list of string" in exception_message)

    def test_default_model_component_precedes(self):
        mcg = ModelComponentGenerator("path", "name")
        default_mcd = mcg.model_component_precedes
        self.assertEqual(default_mcd, [])

    def test_single_model_component_precedes(self):
        mcg = ModelComponentGenerator("path", "name")

        mcg.model_component_precedes = "mc1"
        self.assertEqual(mcg.model_component_precedes, ["mc1"])

        mcg.model_component_precedes = "mc2"
        self.assertEqual(mcg.model_component_precedes, ["mc2"])

    def test_model_component_precedes_as_list(self):
        mcg = ModelComponentGenerator("path", "name")

        mcg.model_component_precedes = ["mc1", "mc2"]
        self.assertEqual(mcg.model_component_precedes, ["mc1", "mc2"])

        mcg.model_component_precedes = ["test1", "test2"]
        self.assertEqual(mcg.model_component_precedes, ["test1", "test2"])

    def test_non_string_model_component_precedes(self):
        mcg = ModelComponentGenerator("path", "name")

        with self.assertRaises(TypeError) as assertion:
            mcg.model_component_precedes = {}
        exception_message = assertion.exception.args[0]
        self.assertTrue(
            exception_message.startswith("Model Component precedes must provide")
        )
        self.assertTrue("one or a list of string" in exception_message)

        with self.assertRaises(TypeError) as assertion:
            mcg.model_component_precedes = [{}]
        exception_message = assertion.exception.args[0]
        self.assertTrue(exception_message.startswith("Model Component precedes"))
        self.assertTrue("list of string" in exception_message)

    def test_error_vmr(self):
        mcg = ModelComponentGenerator("path", "name")
        with self.assertRaises(TypeError):
            mcg.vm_resources = 42

        with self.assertRaises(TypeError):
            mcg.vm_resources = {}

        mcg.vm_resources = None
        self.assertIsNone(mcg.vm_resources)

    def test_string_vmr(self):
        mcg = ModelComponentGenerator("path", "name2")
        vmr = "string.sh"
        mcg.vm_resources = vmr
        self.assertEqual([vmr], mcg.vm_resources)

    def test_arch(self):
        mcg = ModelComponentGenerator("path", "name")
        with self.assertRaises(TypeError):
            mcg.arch = 42

        with self.assertRaises(TypeError):
            mcg.arch = []

        with self.assertRaises(TypeError):
            mcg.arch = {}

        arch = "arm"
        mcg.arch = arch
        self.assertEqual(arch, mcg.arch)

        mcg.arch = None
        self.assertIsNone(mcg.arch)

    def test_read_path(self):
        mcg = ModelComponentGenerator("path", "name")
        with self.assertRaises(TypeError):
            mcg.readme_path = 42

        with self.assertRaises(TypeError):
            mcg.readme_path = []

        with self.assertRaises(TypeError):
            mcg.readme_path = {}

        var = "readme_path"
        mcg.readme_path = var
        self.assertEqual(var, mcg.readme_path)

        mcg.readme_path = None
        self.assertEqual("path/README.rst", mcg.readme_path)

    def test_arch_default(self):
        mcg = ModelComponentGenerator("path", "name")
        self.assertIsNone(mcg.arch)

    def test_error_image(self):
        mcg = ModelComponentGenerator("path", "name")
        with self.assertRaises(TypeError):
            mcg.image = 42

        with self.assertRaises(TypeError):
            mcg.image = {}

        mcg.image = None
        self.assertIsNone(mcg.image)

    def test_string_image(self):
        mcg = ModelComponentGenerator("path", "name2")
        image = "string.xz"
        mcg.image = image
        self.assertEqual([image], mcg.image)

    def test_absolute_plugin(self):
        mcg = ModelComponentGenerator("path", "name")
        with self.assertRaises(ValueError) as assertion:
            # We can ignore this hardcoded tmp path as it is expected to error.
            mcg.plugin = "/tmp/plugin"  # nosec
            exception_message = assertion.exception.args[0]
            self.assertTrue(exception_message.startswith("ModelComponent plugin"))
            self.assertTrue("relative" in exception_message)

    def test_non_string_plugin(self):
        mcg = ModelComponentGenerator("path", "name")
        with self.assertRaises(TypeError) as assertion:
            mcg.plugin = {}
            exception_message = assertion.exception.args[0]
            self.assertTrue(exception_message.startswith("plugin must"))
            self.assertTrue("relative" in exception_message)

    def test_relative_plugin(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.plugin = "dir/plugin"
        self.assertEqual(mcg.plugin, "dir/plugin")

    def test_simple_plugin(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.plugin = "plugin"
        self.assertEqual(mcg.plugin, "plugin")

    def test_default_plugin(self):
        mcg = ModelComponentGenerator("path", "name")
        self.assertEqual(mcg.plugin, None)

    def test_absolute_mc_objects(self):
        mcg = ModelComponentGenerator("path", "name")
        with self.assertRaises(ValueError) as assertion:
            # We can ignore this hardcoded tmp path as it is expected to error.
            mcg.model_component_objects = "/tmp/objs/"  # nosec
        exception_message = assertion.exception.args[0]
        self.assertTrue(
            exception_message.startswith("ModelComponent model_component_objects")
        )
        self.assertTrue("relative" in exception_message)

    def test_non_string_mc_objects(self):
        mcg = ModelComponentGenerator("path", "name")
        with self.assertRaises(TypeError) as assertion:
            mcg.model_component_objects = {}
        exception_message = assertion.exception.args[0]
        self.assertTrue(
            exception_message.startswith(
                "model_component_objects must specify a string"
            )
        )
        self.assertTrue("relative" in exception_message)

    def test_relative_mc_objects(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.model_component_objects = "dir/objs"
        self.assertEqual(mcg.model_component_objects, "dir/objs")

    def test_simple_mc_objects(self):
        mcg = ModelComponentGenerator("path", "name")
        mcg.model_component_objects = "objs"
        self.assertEqual(mcg.model_component_objects, "objs")

    def test_model_component_depends_as_list_not_str(self):
        mcg = ModelComponentGenerator("path", "name")

        with self.assertRaises(TypeError):
            mcg.model_component_depends = ["mc1", "mc2", 5]

    def test_vm_resources_as_list_not_str(self):
        mcg = ModelComponentGenerator("path", "name")

        with self.assertRaises(TypeError):
            mcg.vm_resources = ["test.sh", 5]

    def test_image_as_list_not_str(self):
        mcg = ModelComponentGenerator("path", "name")

        with self.assertRaises(TypeError):
            mcg.image = ["test.sh", 5]

    def test_write_manifest_basic_no_set(self):
        mcg = ModelComponentGenerator(self.base_dir, "name")
        mcg.write_manifest()

        with open(os.path.join(self.base_dir, "MANIFEST"), "r", encoding="utf8") as f:
            result = yaml.safe_load(f)

        expected_dict = {
            "name": "name",
            "attributes": {"depends": [], "provides": [], "precedes": []},
            "model_components": {"depends": [], "precedes": []},
        }

        self.assertEqual(result, expected_dict)

    def test_write_manifest_basic_all_set(self):
        depends = ["foo"]
        provides = ["bar"]
        precedes = []
        mc_depends = ["name"]
        mc_precedes = []
        vmr = ["test.sh", "run.py"]
        image_paths = ["windows.xz", "linux.xz"]
        arch = "x86_64"

        mcg = ModelComponentGenerator(self.base_dir, "test")

        mcg.attribute_depends = depends
        mcg.attribute_precedes = precedes
        mcg.attribute_provides = provides
        mcg.model_component_depends = mc_depends
        mcg.model_component_precedes = mc_precedes
        mcg.vm_resources = vmr
        mcg.image = image_paths
        mcg.arch = arch

        mcg.write_manifest()

        with open(os.path.join(self.base_dir, "MANIFEST"), "r", encoding="utf8") as f:
            result = yaml.safe_load(f)

        expected_dict = {
            "name": "test",
            "attributes": {"depends": depends, "provides": provides, "precedes": []},
            "images": [{"paths": image_paths, "architecture": arch}],
            "model_components": {"depends": mc_depends, "precedes": []},
            "vm_resources": vmr,
        }
        self.assertEqual(result, expected_dict)

    def test_write_manifest_plugin(self):
        mcg = ModelComponentGenerator(self.base_dir, "test")
        mcg.plugin = "my_plugin"

        mcg.write_manifest()

        with open(os.path.join(self.base_dir, "MANIFEST"), "r", encoding="utf8") as f:
            result = yaml.safe_load(f)

        self.assertTrue("plugin" in result)
        self.assertEqual(result["plugin"], "my_plugin")

    def test_write_manfiest_mc_objects(self):
        mcg = ModelComponentGenerator(self.base_dir, "test")
        mcg.model_component_objects = "objs.py"

        mcg.write_manifest()

        with open(os.path.join(self.base_dir, "MANIFEST"), "r", encoding="utf8") as f:
            result = yaml.safe_load(f)

        self.assertTrue("model_component_objects" in result)
        self.assertEqual(result["model_component_objects"], "objs.py")

    def test_create_readme(self):
        mcg = ModelComponentGenerator(self.base_dir, "test")

        mcg.create_readme()
        with open(
            os.path.join(self.base_dir, mcg.readme_filename), "r", encoding="utf8"
        ) as readme:
            contents = readme.read()
        self.assertTrue("TODO" in contents)  # noqa: T101
        self.assertTrue(mcg.name in contents)
        os.remove(os.path.join(self.base_dir, mcg.readme_filename))

    def test_plugin_class_property(self):
        mcg = ModelComponentGenerator(self.base_dir, "test")

        self.assertEqual(mcg.plugin_class, "Plugin")

        mcg.plugin_class = "ClassName"
        self.assertEqual(mcg.plugin_class, "ClassName")

        with self.assertRaises(ValueError) as assertion:
            mcg.plugin_class = "Invalid-Name"
        exp_msg = assertion.exception.args[0]
        self.assertEqual(exp_msg, "Must specify a valid Python class name.")

    def test_create_component(self):
        mcg = ModelComponentGenerator(self.base_dir, "test")

        # Stub out methods
        # pylint: disable=global-variable-undefined
        global counter
        counter = 0

        def fail():
            raise RuntimeError("Invalid method called.")

        # pylint: disable=unused-argument
        def increment(do_docs=None):
            # pylint: disable=global-variable-undefined
            global counter
            counter += 1

        mcg.write_manifest = increment
        mcg.create_readme = fail
        mcg.create_plugin_module = fail
        mcg.create_model_component_objects_module = fail

        mcg.create_component(manifest_only=True)
        self.assertEqual(counter, 1)
        counter = 0
        with self.assertRaises(RuntimeError) as assertion:
            mcg.create_component()
        exp_msg = assertion.exception.args[0]
        self.assertEqual(exp_msg, "Invalid method called.")
        self.assertEqual(counter, 1)
        counter = 0

        mcg.create_readme = increment
        mcg.create_component()
        self.assertEqual(counter, 2)
        counter = 0

        mcg.plugin = "plugin.py"
        mcg.create_plugin_module = increment
        mcg.create_component()
        self.assertEqual(counter, 3)
        counter = 0

        mcg.model_component_objects = "model_component_objects.py"
        mcg.create_model_component_objects_module = increment
        mcg.create_component()
        self.assertEqual(counter, 4)
        counter = 0

    def test_python_file(self):
        name = "anything.py"
        self.assertEqual(python_file(name), name)

    def test_python_file_invalid(self):
        name = "anything.sh"
        with self.assertRaises(argparse.ArgumentTypeError):
            python_file(name)

        name = "anything"
        with self.assertRaises(argparse.ArgumentTypeError):
            python_file(name)

        name = 42
        with self.assertRaises(argparse.ArgumentTypeError):
            python_file(name)

        name = []
        with self.assertRaises(argparse.ArgumentTypeError):
            python_file(name)

        name = {}
        with self.assertRaises(argparse.ArgumentTypeError):
            python_file(name)
