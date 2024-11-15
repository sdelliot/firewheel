import io
import unittest
import unittest.mock

from firewheel.cli.section import MalformedSectionError
from firewheel.cli.executable_section import (
    BadExecutorError,
    IllegalListError,
    ExecutableSection,
)


class CliExecutableSectionTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_invalid_content(self):
        content = 1234
        with self.assertRaises(MalformedSectionError):
            ExecutableSection(content, None)

    def test_bad_arguments(self):
        content = ["single line"]
        with self.assertRaises(IllegalListError):
            ExecutableSection(content, None)

        content = ["single line"]
        arguments = ""
        with self.assertRaises(MalformedSectionError):
            ExecutableSection(content, arguments)

        content = ["single line"]
        arguments = []
        with self.assertRaises(IllegalListError):
            ExecutableSection(content, None)

        content = ["single line"]
        arguments = ["Shell", ["control", "compute"], "extra"]
        with self.assertRaises(IllegalListError):
            ExecutableSection(content, arguments)

        content = ["single line"]
        arguments = ["Shell"]
        with self.assertRaises(IllegalListError):
            ExecutableSection(content, arguments)

    def test_is_executable(self):
        content = ["multi", "line"]
        arguments = ["Shell", ["control", "compute"]]
        section = ExecutableSection(content, arguments)
        self.assertTrue(section.is_executable())

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_get_extension(self, mock_stdout):
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

        arguments = ["Asdf", ["control", "compute"]]
        section = ExecutableSection(content, arguments)
        with self.assertRaises(BadExecutorError):
            section.get_file_extension()

        arguments = ["Test Spaces", ["control", "compute"]]
        section = ExecutableSection(content, arguments)
        with self.assertRaises(BadExecutorError):
            section.get_file_extension()

        self.assertIn("Unable to find executor", mock_stdout.getvalue())

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_bad_execute(self, mock_stdout):
        content = ["exit 0"]
        arguments = ["Shell", ["asdf"]]
        session = {"sequence_number": 0}
        section = ExecutableSection(content, arguments)
        ret = section.execute("asdf.sh", session, None)

        # This will have failed due to an invalid hostgroup
        self.assertEqual(ret, 1)

        arguments = ["Shell", ["control"]]
        section = ExecutableSection(content, arguments)
        ret = section.execute("asdf.sh", session, None)

        # This will have failed due to an invalid cache_file
        self.assertEqual(ret, 1)
        self.assertIn("Command not found", mock_stdout.getvalue())
