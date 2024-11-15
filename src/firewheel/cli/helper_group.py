import os
import grp

from firewheel.config import Config
from firewheel.lib.log import Log


class HelperGroup:
    """
    Represent a group of Helpers.

    This extends a basic dictionary by implementing the build_cache() method.
    """

    def __init__(self, helper_path):
        """
        Initialize some class variables.

        Args:
            helper_path (str): The name of the Helper group.
        """
        self.log = Log(name="CLI").log
        self.name = helper_path
        # Technically, these can be Helpers or Helper groups.
        # They just need to have a build_cache() method.
        self.helpers = {}

    def __getitem__(self, key):
        """
        Dictionary-style read access.

        Args:
            key (str): The section key.

        Returns:
            str: The corresponding value from the sections dictionary.
        """
        return self.helpers[key]

    def __contains__(self, key):
        """
        Allow outsiders to test for the existence of a section.

        Args:
            key (str): The section key.

        Returns:
            bool: True if the key is in the sections, False otherwise.
        """
        return key in self.helpers

    def __setitem__(self, key, item):
        """
        Dictionary-style write access.

        Args:
            key (str): The string key (i.e. Helper name)
            item (Any): The value.
        """
        self.helpers[key] = item

    def __iter__(self):
        """
        Return iterator over the `self.helper` keys.

        Returns:
            iterable: The iterable of `self.helper` keys.
        """
        return iter(self.helpers)

    def keys(self):
        """
        Dictionary-style keys method.

        Returns:
            list: A list of keys from the Helpers dictionary (i.e. Helper names).
        """
        return list(self.helpers)

    def build_cache(self, path=None):
        """
        Make sure the cache structure is correctly in place.

        This will then call :meth:`build_cache` for each Helper we have.

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
                        "local Helper cache and continuing.",
                        exp,
                    )
                except OSError as exp:
                    self.log.warning(
                        "Unable to change group on local Helper cache file: %s", exp
                    )

        # Now make sure the cache path for our group exists.
        group_cache_path = os.path.join(path, self.name)
        if not os.path.isdir(group_cache_path):
            os.makedirs(group_cache_path)
            if config["system"]["default_group"]:
                try:
                    # There does not appear to be a single "get" call for umask.
                    cur_umask = os.umask(0o777)
                    os.umask(cur_umask)
                    permissions_value = 0o777 - cur_umask
                    group = grp.getgrnam(config["system"]["default_group"])
                    path_stat_info = os.stat(group_cache_path)
                    if (
                        path_stat_info.st_gid != group.gr_gid
                        and path_stat_info.st_gid != os.getgid()
                    ):
                        os.chown(group_cache_path, -1, group.gr_gid)
                    os.chmod(group_cache_path, permissions_value)
                except KeyError as exp:
                    self.log.warning(
                        "Group %s does not exist. Not setting group "
                        'on local Helper cache for group "%s" and '
                        "continuing.",
                        self.name,
                        exp,
                    )
                except OSError as exp:
                    self.log.warning(
                        "Unable to change group on local Helper cache for "
                        'group "%s" file: %s',
                        self.name,
                        exp,
                    )

        # For each Helper, build it's cache.
        for helper_obj in self.helpers.values():
            helper_obj.build_cache(path)
