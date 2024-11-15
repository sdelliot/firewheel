# pylint: disable=invalid-name

import os
import shutil
import tempfile
import unittest

from firewheel.control.model_component_path_iterator import ModelComponentPathIterator


class ModelComponentPathIteratorTestCase(unittest.TestCase):
    def setUp(self):
        self.base_dir = tempfile.mkdtemp()

        self.valid_repository1 = os.path.join(self.base_dir, "valid1")
        self.valid_repository2 = os.path.join(self.base_dir, "valid2")
        self.invalid_repository1 = os.path.join(self.base_dir, "invalid1")

        os.makedirs(self.valid_repository1)
        os.makedirs(self.valid_repository2)
        os.makedirs(self.invalid_repository1)

        self.c11 = os.path.join(self.valid_repository1, "c11")
        os.makedirs(self.c11)

        self.c21 = os.path.join(self.valid_repository2, "c21")
        os.makedirs(os.path.join(self.c21))
        self.c22 = os.path.join(self.valid_repository2, "c22")
        os.makedirs(os.path.join(self.c22))

        self.c31 = os.path.join(self.invalid_repository1, "c31")
        os.makedirs(self.c31)

        with open(os.path.join(self.c11, "MANIFEST"), "w", encoding="utf8") as f:
            f.write("")
        with open(os.path.join(self.c21, "MANIFEST"), "w", encoding="utf8") as f:
            f.write("")
        with open(os.path.join(self.c22, "MANIFEST"), "w", encoding="utf8") as f:
            f.write("")
        # DO NOT WRITE c31

    def tearDown(self):
        shutil.rmtree(self.base_dir)

    def test_single_component_repo(self):
        repos = [{"path": self.valid_repository1}]
        i = ModelComponentPathIterator(iter(repos))
        comp = next(i)
        self.assertEqual(self.c11, comp)
        with self.assertRaises(StopIteration):
            next(i)

    def test_two_component_repo(self):
        repos = [{"path": self.valid_repository2}]
        expected_list = sorted([self.c21, self.c22])

        mci = ModelComponentPathIterator(iter(repos))
        actual_list = []
        for i in mci:
            actual_list.append(i)

        actual_list.sort()
        self.assertEqual(expected_list, actual_list)

    def test_both_repos(self):
        repos = [{"path": self.valid_repository1}, {"path": self.valid_repository2}]
        expected_list = sorted([self.c11, self.c21, self.c22])

        mci = ModelComponentPathIterator(iter(repos))
        actual_list = []
        for i in mci:
            actual_list.append(i)

        actual_list.sort()
        self.assertEqual(expected_list, actual_list)

    def test_invalid_repo(self):
        repos = [{"path": self.invalid_repository1}]
        expected_list = []

        mci = ModelComponentPathIterator(iter(repos))
        actual_list = []
        for i in mci:
            actual_list.append(i)

        # Don't sort since we expect an empty list anyway--and it seems to give
        # a None back, not an empty list.
        self.assertEqual(expected_list, actual_list)

    def test_missing_repo(self):
        repos = [{"path": os.path.join(self.base_dir, "omitted")}]
        expected_list = []

        mci = ModelComponentPathIterator(iter(repos))
        actual_list = []
        for i in mci:
            actual_list.append(i)

        # Don't sort since we expect an empty list anyway
        self.assertEqual(expected_list, actual_list)
