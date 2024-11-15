# pylint: disable=invalid-name

import os
import sys
import shutil
import tempfile
import unittest

import yaml

from firewheel.control.model_component import ModelComponent
from firewheel.control.model_component_iterator import ModelComponentIterator


class ModelComponentIteratorTestCase(unittest.TestCase):
    def setUp(self):
        self.base_dir = tempfile.mkdtemp()
        self.repo_dir = "repo"
        self.test_manifests = []

        self.c11 = os.path.join(self.base_dir, self.repo_dir, "c11")
        self.test_mcs = [self.c11]

        self.depends = ["c1"]
        self.provides = ["c3", "c2"]
        self.mc_depends = ["mca", "aa.bb"]
        self.manifest = {
            "name": "test.model_component",
            "attributes": {"depends": self.depends, "provides": self.provides},
            "model_components": {"depends": self.mc_depends},
        }

        self.test_manifests.append(self.manifest)
        os.makedirs(self.c11)
        with open(os.path.join(self.c11, "MANIFEST"), "w", encoding="utf8") as f:
            f.write(yaml.safe_dump(self.manifest))

    def tearDown(self):
        shutil.rmtree(self.base_dir)
        for test_manifest in self.test_manifests:
            if test_manifest["name"] in sys.modules:
                del sys.modules[test_manifest["name"]]

    def test_single(self):
        repos = [{"path": os.path.join(self.base_dir, self.repo_dir)}]
        it = ModelComponentIterator(iter(repos))

        expected_list = [ModelComponent(path=self.c11)]

        actual_list = []
        for comp in it:
            actual_list.append(comp)
        self.assertEqual(expected_list, actual_list)
