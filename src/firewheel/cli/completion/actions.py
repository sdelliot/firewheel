"""
Provide FIREWHEEL-dependent tools to be used by the Bash completion script.
"""

import functools
import subprocess

from firewheel.cli.firewheel_cli import FirewheelCLI
from firewheel.control.repository_db import RepositoryDb
from firewheel.control.model_component_iterator import ModelComponentIterator


def _keyboard_interruptable(func):
    """
    Wrap a function to fail gracefully on keyboard interruption.

    Args:
        func (callable): The callable to be wrapped.

    Returns:
        callable: The callable, wrapped to fail gracefully on keyboard
        interruption.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return_value = func(*args, **kwargs)
        except KeyboardInterrupt:
            return_value = None
        return return_value

    return wrapper


@_keyboard_interruptable
def get_available_cli_commands():
    """
    Get the set of available CLI commands.

    Uses the :py:class:`firewheel.cli.firewheel_cli.FirewheelCLI` object
    to look up the complete set of available CLI commands so that they
    may be used for autocompletion.
    """
    fw_command_prefix = "do_"
    fw_commands = []
    for cmd in dir(FirewheelCLI):
        if cmd.startswith(fw_command_prefix):
            fw_commands.append(cmd[len(fw_command_prefix) :])
    print(" ".join(fw_commands))


@_keyboard_interruptable
def get_model_component_names():
    """Get the names of all model component repositories."""
    rdb = RepositoryDb()
    mci = ModelComponentIterator(rdb.list_repositories())
    # Gather all the model components and print their names
    mcs = [mc.name for mc in mci]
    print(" ".join(mcs))


@_keyboard_interruptable
def get_total_model_components_size():
    """Determine the total size of all of the model component repositories."""
    rdb = RepositoryDb()
    size = 0
    for repo in rdb.list_repositories():
        # Check the size of the repo
        # (argument guaranteed to be a path; see `RepositoryDB._validate_repository`)
        output = subprocess.check_output(["/usr/bin/du", "-s", repo["path"]])  # nosec
        output_string = output.decode("utf-8")
        local_size = int(output_string.split("\t", maxsplit=1)[0])
        size += local_size
    print(size)
