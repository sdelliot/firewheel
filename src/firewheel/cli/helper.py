import os
import grp
import decimal

from firewheel.config import Config
from firewheel.lib.log import Log
from firewheel.cli.section import Section, MalformedSectionError
from firewheel.cli.executable_section import ExecutableSection


class Helper:
    """
    Class representing a single Helper.

    Allows access to all sections as a dictionary, keyed on section name.
    Because multiples are allowed for RUN section, the entry for "RUN"
    is actually a list. This entry is not expected to be accessed directly,
    but rather through methods like run.
    """

    SECTION_TERMINATOR = "DONE"
    REQUIRED_SECTIONS = ["RUN", "AUTHOR", "DESCRIPTION"]

    def __init__(self, helper_path, helpers_root):
        """
        Initialize this Helper, reading our sections from the file defining us.

        Args:
            helper_path (str): The relative path to the Helper. This specifies Helper
                               name and group.
            helpers_root (str): The root directory for the Helpers.
        """
        self.log = Log(name="CLI").log
        self.name = helper_path

        file_path = os.path.join(helpers_root, helper_path)
        self._read_sections(file_path)

    def _read_sections(self, helper_path):
        """
        Read the sections from definition file and store them in a dictionary.

        Args:
            helper_path (str): The absolute path to the Helper definition file.

        Raises:
            MalformedSectionError: Caused by syntax errors.

        """
        # Open file helpers_dir/helper_name
        # We assume we're given an absolute path.
        filename = helper_path
        reading_section = False
        section_name = ""
        section_content = []
        section_args = []

        self.sections = {}

        with open(filename, "r", encoding="utf8") as fhand:
            for line_s in fhand:
                # Always strip the newline so we don't get extra ones when printing
                line = line_s.strip("\n")
                if reading_section:
                    if line == self.SECTION_TERMINATOR:
                        reading_section = False
                        if section_name == "RUN":
                            if section_name not in self.sections:
                                self.sections[section_name] = []
                            self.sections[section_name].append(
                                ExecutableSection(section_content, section_args)
                            )
                        else:
                            self.sections[section_name] = Section(
                                section_content, section_args
                            )
                    else:
                        section_content.append(line)
                elif line:
                    reading_section = True
                    split_line = line.split()
                    section_name = split_line[0].strip()
                    section_content = []
                    section_args = []

                    # Executable sections have arguments.
                    # Expected format: RUN <executor> <host_list>
                    if section_name == "RUN":
                        # Parse arguments.
                        if len(split_line) < 4:
                            raise MalformedSectionError(
                                "Improperly formatted RUN section."
                            )
                        section_args.append(split_line[1])
                        on_marker = 2
                        try:
                            while split_line[on_marker] != "ON":
                                on_marker += 1
                            section_args.append(split_line[on_marker + 1 :])
                        except IndexError as exp:
                            self.log.exception("Unable to find ON clause.")
                            raise MalformedSectionError(
                                "Unable to find ON clause."
                            ) from exp

        # If we stop reading the file but are in the middle of a section, throw an error.
        if reading_section:
            raise MalformedSectionError("EOF encountered before end of section.")

        # Make sure we found all the sections we expected.
        for section in self.REQUIRED_SECTIONS:
            if section not in self.sections:
                raise MalformedSectionError(f"No {section} section found.")

    def __getitem__(self, key):
        """
        Dictionary-style read access.

        Args:
            key (str): The section key.

        Returns:
            str: The corresponding value from the sections dictionary.
        """
        return self.sections[key]

    def __contains__(self, key):
        """
        Allow outsiders to test for the existence of a section.

        Args:
            key (str): The section key.

        Returns:
            bool: True if the key is in the sections, False otherwise.
        """
        return key in self.sections

    def build_cache(self, path=None):
        """
        Build the cache of this Helper's RUN sections on the local system.

        Args:
            path (str): The path to the cache directory. By default it uses
                the FIREWHEEL CLI `cache_dir`.
        """
        config = Config().get_config()

        if not path:
            path = os.path.join(config["cli"]["root_dir"], config["cli"]["cache_dir"])

        # Make sure the cache path exists.
        if not os.path.isdir(path):
            os.makedirs(path)
            if config["system"]["default_group"]:
                try:
                    # There does not appear to be a single "get" call for umask.
                    cur_umask = os.umask(0o777)
                    os.umask(cur_umask)
                    permissions_value = 0o777 - cur_umask
                    group = grp.getgrnam(config["system"]["default_group"])
                    path_stat_info = os.stat(path)
                    if (
                        path_stat_info.st_gid != group.gr_gid
                        and path_stat_info.st_gid != os.getgid()
                    ):
                        os.chown(path, -1, group.gr_gid)
                    os.chmod(path, permissions_value)
                except KeyError as exp:
                    self.log.warning(
                        "Group %s does not exist. Not setting group on "
                        "local Helper cache directory and continuing.",
                        exp,
                    )
                except OSError as exp:
                    self.log.warning(
                        "Unable to change group on local Helper cache directory: %s",
                        exp,
                    )

        run_counter = 0
        # For each Helper, loop through the RUN sections.
        for section in self.sections["RUN"]:
            # Build a file for the section based on the executor's file
            #  extension.
            if section.is_executable():
                filename = f"{self.name}{run_counter}{section.get_file_extension()}"
                run_counter += 1
                file_path = os.path.join(path, filename)

                # If the file already existed, it won't be re-created, so there
                # is no need to adjust the permissions. Additionally, we may not
                # own the file, so trying to adjust the permissions may cause an
                # error in this case.
                file_preexisted = os.path.exists(file_path)

                with open(file_path, "w", encoding="utf8") as cache_file:
                    for line in section.content:
                        cache_file.write(f"{line}\n")
                section.cache = file_path

                # Make sure our script is executable. p-scp will preserve our mode.
                if not file_preexisted:
                    try:
                        cur_umask = os.umask(0o777)
                        os.umask(cur_umask)
                        # The default file mode is 0o666.
                        # We want these files to be executable, so add 0o111.
                        new_mode = 0o666 - cur_umask + 0o111
                        os.chmod(file_path, new_mode)
                        if config["system"]["default_group"]:
                            try:
                                group = grp.getgrnam(config["system"]["default_group"])
                                path_stat_info = os.stat(file_path)
                                if (
                                    path_stat_info.st_gid != group.gr_gid
                                    and path_stat_info.st_gid != os.getgid()
                                ):
                                    os.chown(file_path, -1, group.gr_gid)
                            except KeyError as exp:
                                self.log.warning(
                                    "Group %s does not exist. Not "
                                    "setting group on cached local "
                                    "Helper file %s and continuing.",
                                    file_path,
                                    exp,
                                )
                            except OSError as exp:
                                self.log.warning(
                                    "Unable to change group on cached "
                                    "local Helper file %s: %s",
                                    file_path,
                                    exp,
                                )
                    except IOError as exp:
                        print(
                            "Error: I/O error trying to set permissions on local "
                            f"temp file: {exp}"
                        )
                        self.log.exception(
                            "I/O error trying to set permissions on local temp file."
                        )

    def run(self, session, arguments):
        """
        Run this Helper (all RUN sections).

        Executes the list found in the "RUN" key, not necessarily all
        ExecutableSections (although these 2 groups *should* always be the same).

        Args:
            session (dict): The current CLI session properties.
            arguments (list): Command-line arguments for the invocation of the RUN
                              sections. Also passing through (eventually) to the
                              HostAccessor.

        Returns:
            int: The summation of the error codes from the executable sections that
            were run. In the case of the `Helpers` executor, this would be the number
            of Helpers that failed. In the case of the `LocalPython` executor this would be the
            error code from the Helper itself. For the `Python` and `Shell` executors,
            the number of nodes which produced errors. This will return 0 on success.

        Raises:
            MalformedSectionError: Caused if there are no sections in the "RUN" key or
                if an object in the "RUN" key returns false from its `is_executable`
                method.

        """
        config = Config().get_config()

        # Execute the section with the default name ("RUN").
        # Throw exceptions if it doesn't exist or isn't executable
        if "RUN" not in self.sections:
            raise MalformedSectionError("No default executable section found")

        if len(self.sections["RUN"]) > 1:
            sequence_increment = decimal.Decimal("0.1")
        else:
            sequence_increment = 0
        counter = 0
        section_failed_count = 0
        for section in self.sections["RUN"]:
            if not section.is_executable:
                raise MalformedSectionError("RUN section is not executable")
            cache_file = os.path.join(
                config["cli"]["root_dir"],
                config["cli"]["cache_dir"],
                f"{self.name}{counter}{section.get_file_extension()}",
            )
            counter += 1

            ret_code = section.execute(cache_file, session, arguments)
            if ret_code != 0:
                section_failed_count += ret_code
            session["sequence_number"] = (
                decimal.Decimal(session["sequence_number"]) + sequence_increment
            )
        return section_failed_count
