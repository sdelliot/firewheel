class MalformedSectionError(Exception):
    """
    Error for when a section declaration doesn't meet our syntax expectations.
    """


class Section:
    """
    A basic section, the building-block of a Helper.

    This is a "text" section. It isn't runnable, but stores the section
    contents. These contents may be requested by the user and we'll print them.
    """

    def __init__(self, content, _arguments):
        """
        Initialize ourselves.

        We don't do any operations besides setting instance variables.

        Args:
            content (list): The content of this section.
            _arguments: This argument is ignored.

        Raises:
            MalformedSectionError: If the content is not a list.
        """
        if content is None:
            content = []

        if not isinstance(content, list):
            raise MalformedSectionError("Section content is not a list")

        self.content = content  # Expected to be a list.
        self.cache = (
            None  # Expected to be a file path to a file containing self.content
        )

    def format_content(self, pre="", post="\n"):
        """
        Formats the contents of the section for printing.

        Args:
            pre (str): Prepend this string to the section.
            post (str): Append this string to the section.

        Returns:
            str: The modified content.
        """
        ret = ""
        for line in self.content:
            ret += pre + line + post
        return ret

    def print_content(self):
        """
        Print the content of this section.
        """
        for line in self.content:
            print(line)

    def is_executable(self):
        """
        Determine if it is a :py:class:`Section` or an :py:class:`ExectuableSection`.

        Returns:
            bool: This always returns False as text sections are not executable.
        """
        return False

    def get_file_extension(self):
        """
        Needed by ExecutableSections.

        Raises:
            NotImplementedError: This method is not used.
        """
        raise NotImplementedError

    def has_content(self):
        """
        Checks if the item has any content.

        Returns:
            bool: True if content exists and False if content does not exists
        """
        return bool(self.content)
