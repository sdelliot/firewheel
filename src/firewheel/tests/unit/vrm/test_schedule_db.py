import unittest

from firewheel.config import config
from firewheel.lib.minimega.file_store import FileStore
from firewheel.vm_resource_manager.schedule_db import ScheduleDb


class ScheduleDbTestCase(unittest.TestCase):
    def setUp(self):
        self.test_schedule_db_name = config["test"]["schedule_test_database"]
        self.schedule_db = ScheduleDb(cache_name=self.test_schedule_db_name)
        self.schedule_db_cache = FileStore

        # Create valid and invalid repository directories
        self.entries = [
            {"server_name": "1", "text": b"", "ip": ""},
            {"server_name": "2", "text": b"", "ip": ""},
        ]
        self.invalid_entry_1 = {
            "server_name": "test-invalid",
            "text": b"asdf",
            "vm_resources_ip": "",
            "invalid": "value",
        }
        self.invalid_entry_2 = {"invalid": "value"}

    def tearDown(self):
        self.schedule_db.cache.remove_file("*")
        self.schedule_db.close()

    def test_put_schedule(self):
        self.schedule_db.put(self.entries[0]["server_name"], b"", self.entries[0]["ip"])
        found = self.schedule_db.list_all()

        self.assertEqual(self.entries[0]["server_name"], found[0]["server_name"])

    def test_batch_put(self):
        self.schedule_db.batch_put(self.entries)
        found1 = self.schedule_db.list_all(self.entries[0]["server_name"])[0]
        found2 = self.schedule_db.list_all(self.entries[1]["server_name"])[0]
        self.assertEqual(self.entries[0]["server_name"], found1["server_name"])
        self.assertEqual(self.entries[0]["text"], found1["text"])
        self.assertEqual(self.entries[1]["server_name"], found2["server_name"])
        self.assertEqual(self.entries[1]["text"], found2["text"])

    def test_add_too_many_keys(self):
        with self.assertRaises(TypeError):
            # pylint: disable=unexpected-keyword-arg
            self.schedule_db.put(**self.invalid_entry_1)

    def test_add_wrong_key(self):
        with self.assertRaises(TypeError):
            # pylint: disable=unexpected-keyword-arg
            self.schedule_db.put(**self.invalid_entry_2)

    def test_duplicate_put(self):
        self.schedule_db.put(
            self.entries[0]["server_name"], b"a", self.entries[0]["ip"]
        )
        self.schedule_db.put(
            self.entries[0]["server_name"], b"b", self.entries[0]["ip"]
        )
        found1 = self.schedule_db.list_all()[0]
        self.assertEqual(self.entries[0]["server_name"], found1["server_name"])
        self.assertEqual(b"b", found1["text"])

    def test_destroy_one(self):
        self.schedule_db.put(
            self.entries[0]["server_name"],
            self.entries[0]["text"],
            self.entries[0]["ip"],
        )
        self.schedule_db.destroy_one(self.entries[0]["server_name"])
        with self.assertRaises(IndexError):
            # pylint: disable=expression-not-assigned
            self.schedule_db.list_all()[0]
        self.assertEqual(self.schedule_db.get(self.entries[0]["server_name"]), None)

    def test_destroy_all(self):
        self.schedule_db.put(
            self.entries[0]["server_name"],
            self.entries[0]["text"],
            self.entries[0]["ip"],
        )
        self.schedule_db.put(
            self.entries[1]["server_name"],
            self.entries[1]["text"],
            self.entries[1]["ip"],
        )
        self.schedule_db.destroy_all()
        with self.assertRaises(IndexError):
            # pylint: disable=expression-not-assigned
            self.schedule_db.list_all()[0]

    def test_get(self):
        n_entries = []
        for entry in self.entries:
            self.schedule_db.put(entry["server_name"], entry["text"], entry["ip"])
            n_entries.append(entry["server_name"])

        got_entries = []
        for entry in n_entries:
            cur_text = self.schedule_db.get(entry)
            got_entries.append({"text": cur_text, "server_name": entry, "ip": ""})
        self.assertEqual(got_entries, self.entries)

        for ent in got_entries:
            del n_entries[n_entries.index(ent["server_name"])]

        self.assertEqual(len(n_entries), 0)

    def test_invalid_get(self):
        result = self.schedule_db.get("invalid")
        self.assertEqual(result, None)
