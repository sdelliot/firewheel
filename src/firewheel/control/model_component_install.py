import sys
import stat
import subprocess
from pathlib import Path

import yaml
import ansible_runner
from rich.prompt import PromptBase
from rich.syntax import Syntax
from rich.console import Console

from firewheel.lib.log import Log
from firewheel.config import config


class InstallPrompt(PromptBase[str]):
    """A prompt that has a custom error message."""

    response_type = str
    msg = (
        "[prompt.invalid.choice]Please select one of the available options:\n"
        "y - yes, install execute this script\n"
        "n - no, do not execute this script\n"
        "v - view, see the script text\n"
        "vc - view color, see the script text with color support, must use "
        "a system pager which supports this behavior (e.g. PAGER='less -R')\n"
        "q - quit, exit immediately\n"
    )
    illegal_choice_message = msg
    validate_error_message = msg


class ModelComponentInstall:
    """
    Some Model Components may provide an additional install script called ``INSTALL``
    which can be executed to perform other setup steps (e.g. installing an extra python package
    or downloading an external VM resource).
    This class helps execute that file and install a Model Component.
    ``INSTALL`` scripts can be can be any executable file type as defined by a
    `shebang <https://en.wikipedia.org/wiki/Shebang_(Unix)>`_ line.

    .. warning::

        The execution of Model Component ``INSTALL`` scripts can be a **DANGEROUS** operation.
        Please ensure that you **fully trust** the repository developer prior to executing
        these scripts.

    .. seealso::

        See :ref:`mc_install` for more information on ``INSTALL`` scripts.

    When installing a Model Component, users will have a variety of choices to select:

        - ``y`` - yes, install execute this script
        - ``n`` - no, do not execute this script
        - ``v`` - view, see the script text
        - ``vc`` - view color, see the script text with color support, must use a system pager
          which supports this behavior (e.g. ``PAGER='less -R'``)
        - ``q`` - quit, exit immediately

    """

    def __init__(self, mc=None):
        """
        Initialize the object.

        Args:
            mc (ModelComponent): The :py:class:`ModelComponent` to install.

        Raises:
            ValueError: Caused if a user didn't specify ``mc``.
        """
        if mc is None:
            raise ValueError("Must specify a Model Component.")

        self.mc = mc
        self.log = Log(name="ModelComponentInstall").log

    def install_mc(self, name, install_path):
        """
        Execute a given Model Component's ``INSTALL`` script.

        Args:
            name (str): The name of the Model Component.
            install_path (pathlib.Path): The path of the ``INSTALL`` file.

        Returns:
            bool: True if the MC was installed successfully (or it was already
            installed), False otherwise
        """
        console = Console()

        # Make the install file executable
        # We assume that it can be run with a "shebang" line
        install_path.chmod(
            install_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        console.print(f"[b green]Starting to install [cyan]{name}[/cyan]!")

        # Check if the install script is a valid Ansible playbook
        # if it is, we should execute it with "ansible-runner"
        if self.is_ansible_playbook(install_path):
            return self.run_ansible_playbook(install_path)

        try:
            # We have already checked with the user to ensure that they want to run
            # this script.
            subprocess.run(  # nosec
                [str(install_path)], cwd=install_path.parent, check=True
            )
            console.print(f"[b green]Installed [cyan]{name}[/cyan]!")
            return True
        except subprocess.CalledProcessError as exp:
            if exp.returncode == 117:  # Structure needs cleaning
                console.print(f"[b yellow][cyan]{name}[/cyan] is already installed!")
                return True

            console.print(f"[b red]Failed to install [cyan]{name}[/cyan]!")
            return False

    def is_ansible_playbook(self, install_path):
        """
        Check if the given script is a valid `Ansible <https://docs.ansible.com/>`_ playbook.

        Args:
            install_path (pathlib.Path): The path of the ``INSTALL`` file.

        Returns:
            bool: :py:data:`True` if the script is a valid Ansible playbook, :py:data:`False` otherwise.
        """
        try:
            with open(install_path, "r", encoding="utf-8") as fhand:
                playbook_content = fhand.read()
                playbook = yaml.safe_load(playbook_content)

                # Check if the playbook has the required structure
                return isinstance(playbook, list) and all(
                    "hosts" in play for play in playbook
                )
        except yaml.YAMLError:
            return False

    def run_ansible_playbook(self, install_path):
        """
        Run the Ansible playbook using ansible-runner.

        Args:
            install_path (pathlib.Path): The path of the Ansible playbook.

        Returns:
            bool: :py:data:`True` if the playbook executed successfully, :py:data:`False` otherwise.

        Raises:
            ValueError: If an invalid ansible.cash_type is provided in the FIREWHEEL config.
        """
        console = Console()

        ansible_config = {
            "ansible_remote_tmp": config["system"]["default_output_dir"],
        }

        # Add any remaining configuration options provided in the FIREWHEEL
        # configuration
        ansible_config.update(config["ansible"])

        # Get the cache_type and default to an empty string
        # for easy access
        cache_type = ansible_config.get("cache_type", "")

        # If we set a different cache type, then we should use it
        # to download the needed cached files.
        if cache_type != "online":
            cached_files = []

            # Read the playbook file to get the cached_files variables
            with open(install_path, "r") as file:
                playbook = yaml.safe_load(file)

            # Extract variables from the playbook
            variables = {}
            for play in playbook:
                if "vars" in play:
                    variables.update(play["vars"])

            cached_files = variables.get("cached_files", [])

            # Now we need to update the destination path for all the cached files
            # we can prepend the directory of the original install file.
            for file in cached_files:
                file["destination"] = str(
                    install_path.parent / Path(file["destination"])
                )

            # Call the cache playbook from the ansible_playbooks directory
            cache_playbook_path = Path(__file__).resolve().parent / Path(
                f"ansible_playbooks/{cache_type}.yml"
            )

            if not cache_playbook_path.exists():
                # Get a list of all cache types
                available_types = [
                    file.stem
                    for file in cache_playbook_path.parent.iterdir()
                    if file.is_file()
                ]
                console.print(
                    f"[b red]Failed to find cache_type=[cyan]{cache_type}[/cyan]."
                    f"Available types are: [magenta]{available_types}[/magenta]"
                )
                raise ValueError("Available `cache_type` are: {available_types}")

            # By defining everything here, we can enable prompt's as we will no longer
            # use pexpect by default, but rather use subprocess, enabling stdin
            # See: https://github.com/ansible/ansible-runner/issues/1399
            rc = ansible_runner.RunnerConfig(
                private_data_dir=str(ansible_config["ansible_remote_tmp"]),
                playbook=str(cache_playbook_path),
                extravars={"cached_files": cached_files, **ansible_config},
            )

            rc.prepare()

            # Now we need to ensure the config has these properties
            # so that it will properly take in values passed.
            rc.input_fd = sys.stdin
            rc.output_fd = sys.stdout
            rc.error_fd = sys.stderr
            cache_runner = ansible_runner.Runner(config=rc)

            # Ensure we are using subprocess mode
            cache_runner.runner_mode = "subprocess"

            ret = cache_runner.run()

            # Invoking the runner this way uses an (unnamed) tuple as a return value
            # For example: ("success", 0)
            if ret[1] == 0:
                console.print(
                    f"[b green]Successfully collected cached files via: [cyan]{cache_type}[/cyan]!"
                )
                return True
            else:
                console.print(
                    f"[b red]Failed to collect cached files via: [cyan]{cache_type}[/cyan]; Failed with return code {ret.rc}."
                )
                return False

        # Run the Ansible playbooks
        ret = ansible_runner.run(
            private_data_dir=str(install_path.parent),
            playbook=str(install_path),
            extravars=ansible_config,
        )

        if ret.rc == 0:
            console.print(
                f"[b green]Successfully executed Ansible playbook [cyan]{install_path}[/cyan]!"
            )
            return True
        else:
            console.print(
                f"[b red]Ansible playbook [cyan]{install_path}[/cyan] failed with return code {ret.rc}."
            )
            return False

    def run_install_script(self, insecure=False):
        """
        Ask the user to run the install script for the given Model Component.

        Args:
            insecure (bool): Whether to automatically install the Model Component without asking.
                Default is ``False``.

        Returns:
            bool: ``True`` if all MCs were installed successfully, ``False`` otherwise.
        """
        console = Console()

        install_script = Path(self.mc.path) / "INSTALL"
        install_flag = Path(self.mc.path) / f".{self.mc.name}.installed"

        if not install_script.exists():
            return True

        if install_flag.exists():
            return True

        if insecure is True:
            success = self.install_mc(self.mc.name, install_script)
            if not success:
                console.print(f"[b red]Failed to install [cyan]{self.mc.name}[/cyan].")
                return False
            return True

        choices = ["y", "n", "v", "vc", "q"]
        ask = f"[yellow]Do you want to execute [cyan]{install_script}"
        while True:
            value = InstallPrompt.ask(ask, choices=choices)
            if value == "y":
                success = self.install_mc(self.mc.name, install_script)
                if not success:
                    console.print(
                        f"[b red]Failed to install [cyan]{self.mc.name}[/cyan]"
                        " this may cause downstream issues!"
                    )
                    return False

                # If the install script didn't create the "installed" flag
                # we should do it here.
                if not install_flag.exists():
                    install_flag.touch()
                break
            if value == "n":
                console.print(
                    f"[b red]Continuing WITHOUT running [cyan]{install_script}[/cyan]"
                    " this may cause downstream issues!"
                )
                break
            if value.startswith("v"):
                contents = ""
                with open(install_script, "r", encoding="utf-8") as fhand:
                    contents = fhand.read()
                style = False
                if value == "vc":
                    style = True
                with console.pager(styles=style):
                    console.print(Syntax(contents, lexer="bash"))
            elif value.startswith("q"):
                sys.exit(0)
        return True
