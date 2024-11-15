# pylint: disable=invalid-name

import os
import shutil
import tempfile
import unittest
from datetime import datetime

from firewheel.config import config
from firewheel.lib.minimega.file_store import FileStoreFile
from firewheel.vm_resource_manager.vm_resource_store import VmResourceStore


# pylint: disable=protected-access
class VmResourceStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache_base = os.path.join(self.tmpdir, "base")
        os.makedirs(self.cache_base)

        self.test_vmr_store_name = config["test"]["vm_resource_store_test_database"]
        self.vm_resource_store = VmResourceStore(store=self.test_vmr_store_name)
        self.metadata_cache = self.vm_resource_store.cache

        self.vm_resource1_path = os.path.join(self.tmpdir, "vm_resource1.sh")
        self.vm_resource1 = """
#!/bin/bash
echo 'Hello, World!'
"""
        with open(self.vm_resource1_path, "w", encoding="utf8") as f:
            f.write(self.vm_resource1)

    def tearDown(self):
        # Clear the VM Resource store
        self.vm_resource_store.remove_file("*")

        # remove the temp directories
        shutil.rmtree(self.tmpdir)

    def test_cache_already_exists(self):
        self.assertTrue(os.path.isdir(self.metadata_cache))
        new_vm_resource_store = VmResourceStore(store=self.test_vmr_store_name)
        self.assertNotEqual(None, new_vm_resource_store)

    def test_get_lock(self):
        lock_path = os.path.join(self.metadata_cache, "locktest")
        test_lock_path = lock_path + "-lock"

        self.assertFalse(os.path.isdir(test_lock_path))
        self.vm_resource_store._get_lock(lock_path)
        self.assertTrue(os.path.isdir(test_lock_path))

    def test_get_lock_exception(self):
        lock_path = os.path.join(self.metadata_cache, "locktest")
        test_lock_path = lock_path + "-lock"

        self.assertFalse(os.path.isdir(test_lock_path))
        self.vm_resource_store._get_lock(lock_path)
        self.assertTrue(os.path.isdir(test_lock_path))

        with self.assertRaises(FileExistsError):
            self.vm_resource_store._get_lock(lock_path)

    def test_release_lock(self):
        lock_path = os.path.join(self.metadata_cache, "locktest")
        test_lock_path = lock_path + "-lock"

        self.assertFalse(os.path.isdir(test_lock_path))
        self.vm_resource_store._get_lock(lock_path)
        self.assertTrue(os.path.isdir(test_lock_path))

        self.vm_resource_store._release_lock(lock_path)
        self.assertFalse(os.path.isdir(test_lock_path))

    def test_list_contents(self):
        self.vm_resource_store.add_file(self.vm_resource1_path)
        contents = self.vm_resource_store.list_distinct_contents()
        contents = list(contents)
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0], os.path.basename(self.vm_resource1_path))

    def test_minimega_get_cache_exists(self):
        exists_cache_path = os.path.join(self.metadata_cache, "exists")
        original_contents = "This file should not be altered."
        with open(exists_cache_path, "w", encoding="utf8") as f:
            f.write(original_contents)

        self.vm_resource_store._minimega_get_file(exists_cache_path, "unused")

        with open(exists_cache_path, "r", encoding="utf8") as f:
            contents = f.read()
        self.assertEqual(original_contents, contents)

    def test_minimega_get_no_minimega_file(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        get_path = os.path.join(self.metadata_cache, vm_resource_name)
        original_contents = "This file should not be altered."
        with open(vm_resource_path, "w", encoding="utf8") as f:
            f.write(original_contents)

        with self.assertRaises(FileNotFoundError):
            self.vm_resource_store._minimega_get_file(get_path, vm_resource_name)

    def test_minimega_get(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        get_path = os.path.join(self.metadata_cache, vm_resource_name)
        original_contents = "This file should not be altered."
        with open(vm_resource_path, "w", encoding="utf8") as f:
            f.write(original_contents)

        self.vm_resource_store.add_file(vm_resource_path)
        self.vm_resource_store._minimega_get_file(get_path, vm_resource_name)

        with open(get_path, "r", encoding="utf8") as f:
            get_contents = f.read()
        with open(vm_resource_path, "r", encoding="utf8") as f:
            vm_resource_contents = f.read()

        self.assertEqual(get_contents, vm_resource_contents)
        self.assertEqual(vm_resource_contents, original_contents)

    def test_file_read(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        # Set up contents in binary mode so we match the binary read later.
        original_contents = b"This file should not be altered."
        with open(vm_resource_path, "wb") as f:
            f.write(original_contents)

        self.vm_resource_store.add_file(vm_resource_path)

        with self.vm_resource_store.get_file(vm_resource_name) as n:
            new_contents = n.read()

        self.assertEqual(original_contents, new_contents)

    # pylint: disable=unnecessary-dunder-call
    def test_file_read_manual(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        # Set up contents in binary mode so we match the binary read later.
        original_contents = b"This file should not be altered."
        with open(vm_resource_path, "wb") as f:
            f.write(original_contents)

        self.vm_resource_store.add_file(vm_resource_path)

        af = self.vm_resource_store.get_file(vm_resource_name)
        result = af.__enter__()
        self.assertEqual(result, af)
        new_contents = af.read()
        result = af.__exit__()
        self.assertEqual(result, True)
        self.assertEqual(original_contents, new_contents)

    def test_file_bad_exit(self):
        af = FileStoreFile("Invalid", self.vm_resource_store)
        result = af.__exit__()
        self.assertEqual(result, False)

    def test_file_bad_read(self):
        af = FileStoreFile("Invalid", self.vm_resource_store)
        with self.assertRaises(RuntimeError):
            af.read()

    def test_metadata_cache_creation_path_not_writable(self):
        cache_base = os.path.join(self.metadata_cache, "no_perms")
        cache = os.path.join(cache_base, "cache")
        os.makedirs(cache_base)

        # These permissions should cause an error and are not a security concern
        os.chmod(cache_base, 0o555)  # nosec

        with self.assertRaises(PermissionError):
            VmResourceStore(store=cache)

        # Restore write so we can delete it later.
        # These permissions are required to delete the directory
        os.chmod(cache_base, 0o775)  # nosec

    def test_file_size(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        # Set up contents in binary mode so we match the binary read later.
        original_contents = b"This file should not be altered."
        with open(vm_resource_path, "wb") as f:
            f.write(original_contents)

        self.vm_resource_store.add_file(vm_resource_path)

        fs_size = os.stat(vm_resource_path).st_size
        db_size = self.vm_resource_store.get_file_size(vm_resource_name)
        self.assertEqual(fs_size, db_size)

    def test_file_size_no_file(self):
        with self.assertRaises(FileNotFoundError):
            self.vm_resource_store.get_file_size("invalid")

    def test_minimega_get_data_cache_exists(self):
        exists_cache_path = os.path.join(self.metadata_cache, "exists")
        original_contents = "This file should not be altered."
        with open(exists_cache_path, "w", encoding="utf8") as f:
            f.write(original_contents)

        result, _error = self.vm_resource_store._minimega_get_data(
            exists_cache_path, "unused"
        )
        self.assertEqual(result, exists_cache_path)

        with open(exists_cache_path, "r", encoding="utf8") as f:
            contents = f.read()
        self.assertEqual(original_contents, contents)

    def test_minimega_get_data_no_minimega_file(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        get_path = os.path.join(self.metadata_cache, vm_resource_name)
        original_contents = "This file should not be altered."
        with open(vm_resource_path, "w", encoding="utf8") as f:
            f.write(original_contents)

        with self.assertRaises(FileNotFoundError):
            self.vm_resource_store._minimega_get_data(get_path, vm_resource_name)

    def test_minimega_get_data(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        get_path = os.path.join(self.metadata_cache, vm_resource_name)
        original_contents = "This file should not be altered."
        with open(vm_resource_path, "w", encoding="utf8") as f:
            f.write(original_contents)

        self.vm_resource_store.add_file(vm_resource_path)
        result, _error = self.vm_resource_store._minimega_get_data(
            get_path, vm_resource_name
        )
        self.assertEqual(result, get_path)

        with open(get_path, "r", encoding="utf8") as f:
            get_contents = f.read()
        with open(vm_resource_path, "r", encoding="utf8") as f:
            vm_resource_contents = f.read()

        self.assertEqual(get_contents, vm_resource_contents)
        self.assertEqual(vm_resource_contents, original_contents)

    def test_get_file_invalid(self):
        vm_resource_file = self.vm_resource_store.get_file("invalid")
        self.assertTrue(isinstance(vm_resource_file, FileStoreFile))

        with self.assertRaises(FileNotFoundError):
            with vm_resource_file as _resource:
                pass

    def test_get_modified_time(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        original_contents = "This file should not be altered."
        with open(vm_resource_path, "w", encoding="utf8") as f:
            f.write(original_contents)

        self.vm_resource_store.add_file(vm_resource_path)
        result = self.vm_resource_store.get_file_upload_date(vm_resource_name)
        self.assertNotEqual(result, None)
        self.assertEqual(type(result), datetime)

    def test_get_modified_time_no_vm_resource(self):
        result = self.vm_resource_store.get_file_upload_date("invalid")
        self.assertEqual(result, None)

    def test_get_hash(self):
        vm_resource_name = "vm_resource"
        vm_resource_path = os.path.join(self.cache_base, vm_resource_name)
        original_contents = "This file should not be altered."
        with open(vm_resource_path, "w", encoding="utf8") as f:
            f.write(original_contents)

        self.vm_resource_store.add_file(vm_resource_path)
        result = self.vm_resource_store.get_file_hash(vm_resource_name)
        self.assertNotEqual(result, None)
        self.assertEqual(type(result), str)

    def test_get_hash_no_vm_resource(self):
        result = self.vm_resource_store.get_file_hash("invalid")
        self.assertEqual(result, "")
