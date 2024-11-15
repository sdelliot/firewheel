import unittest

from firewheel.cli.section import Section, MalformedSectionError


class CliSectionTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_format_content_single(self):
        content = ["single line"]
        section = Section(content, None)
        self.assertEqual(section.format_content(), f"{content[0]}\n")

        # Try with custom pre/post
        self.assertEqual(section.format_content(pre="asdf"), f"asdf{content[0]}\n")
        self.assertEqual(
            section.format_content(pre="asdf", post="asdf"), f"asdf{content[0]}asdf"
        )

    def test_format_custom_pre_post_single(self):
        content = ["multi", "line"]
        section = Section(content, None)
        self.assertEqual(section.format_content(), f"{content[0]}\n{content[1]}\n")

        # Try with custom pre/post
        self.assertEqual(
            section.format_content(pre="asdf"), f"asdf{content[0]}\nasdf{content[1]}\n"
        )
        self.assertEqual(
            section.format_content(pre="asdf", post="asdf"),
            f"asdf{content[0]}asdfasdf{content[1]}asdf",
        )

    def test_invalid_content(self):
        content = 1234
        with self.assertRaises(MalformedSectionError):
            section = Section(content, None)

        content = None
        section = Section(content, None)
        self.assertEqual(section.format_content(), "")

        content = ""
        with self.assertRaises(MalformedSectionError):
            section = Section(content, None)

    def test_is_executable(self):
        content = ["multi", "line"]
        section = Section(content, None)
        self.assertFalse(section.is_executable())

        content = ["single line"]
        section = Section(content, None)
        self.assertFalse(section.is_executable())

    def test_has_content(self):
        content = ["multi", "line"]
        section = Section(content, None)
        self.assertTrue(section.has_content())

        content = ["single line"]
        section = Section(content, None)
        self.assertTrue(section.has_content())

        content = []
        section = Section(content, None)
        self.assertFalse(section.has_content())

        content = None
        section = Section(content, None)
        self.assertFalse(section.has_content())

    def test_no_extension(self):
        content = ["single line"]
        section = Section(content, None)
        with self.assertRaises(NotImplementedError):
            section.get_file_extension()
