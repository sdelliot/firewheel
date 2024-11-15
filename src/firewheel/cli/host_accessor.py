"""Enable interaction with the FIREWHEEL cluster.

This module is responsible for containing classes and functions which communicate
to the rest of the FIREWHEEL cluster. This module uses `ClusterShell`_ to send
files and commands to the necessary nodes. This module also includes a custom
ClusterShell :py:class:`ClusterShell.Event.EventHandler`.

.. _ClusterShell: https://pypi.org/project/ClusterShell/
"""

import os
import grp
import errno
import shutil
import decimal
import tempfile
import subprocess

from rich.console import Console
from ClusterShell.Task import task_self
from ClusterShell.Event import EventHandler
from ClusterShell.NodeSet import NodeSet

from firewheel.cli import utils
from firewheel.config import Config
from firewheel.lib.log import Log


class ClusterHandler(EventHandler):
    """Define a custom :py:class:`ClusterShell.Event.EventHandler` for FIREWHEEL.

    This helps process the results from ClusterShell tasks. Most of the processing
    requires and handling/logging errors and printing output.
    """

    def __init__(self, cmd=None):
        """Initialize the event handler.

        Attributes:
            failed (int): The count of how many errors occur for the task.
            log (logging.Logger): Provides the logger to the various methods.
            cmd (str): The command being executed. This is used for logging.

        Args:
            cmd (str): The command which is being executed.
        """
        super().__init__()
        self.failed = 0
        self.log = Log(name="CLI").log
        self.cmd = cmd
        self.log.info("Starting to run cmd=%s", cmd)

    def ev_read(self, _worker, node, sname, msg):
        """Indicate that a worker has data to read from a specific node (or key).

        Args:
            _worker (ClusterShell.Worker.Ssh.WorkerSsh): Worker derived object.
            node (str): The node which completed the task.
            sname (str): The stream name (stdout or stderr).
            msg (bytes): The resulting output/message from the task.
        """
        if sname == "stderr":
            self.log.error(
                "Error from %s: `%s`",
                node,
                str(msg, "utf-8"),
            )
        else:
            self.log.debug(
                "Output from %s: `%s`",
                node,
                str(msg, "utf-8"),
            )
        print(str(msg, "utf-8"))

    def ev_hup(self, _worker, node, rc):
        """Indicate that a worker command for a specific node has just finished.

        This method also helps count errors that occur with the various workers.

        Args:
            _worker (ClusterShell.Worker.Ssh.WorkerSsh): Worker derived object.
            node (str): The node which completed the task.
            rc (int): The command return code (or None if the worker doesn't
                      support command return codes).
        """
        if rc != 0:
            self.failed += 1

            self.log.error(
                "Node %s returned with error code %s",
                node,
                rc,
            )
        else:
            self.log.debug(
                "Node %s returned successfully!",
                node,
            )

    def ev_close(self, worker, timedout):
        """Indicate that a worker has just finished.

        Args:
            worker (ClusterShell.Worker.Ssh.WorkerSsh): Worker derived object.
            timedout (bool): Indicates if the worker has timed out.
        """
        if timedout:
            self.log.error(
                "The following nodes timed out: %s",
                worker.iter_keys_timeout(),
            )
        if self.failed:
            self.log.error(
                "%s nodes failed running command.",
                self.failed,
            )
        else:
            self.log.info("Command succeeded!")


class HostAccessor:
    """Enable copying files and running commands with a FIREWHEEL cluster.

    Loads the host group from the config information and permits
    access to hosts. Allows file transfer and single-command execution
    leveraging ClusterShell.
    """

    def __init__(self, host_group_name):
        """Initialize the HostAccessor attributes and ensure the host group is valid.

        Attributes:
            log (logging.Logger): A class-accessible log.
            host_group_name (str): The host group to use for the instantiation
                of the class.
            ssh_options (str): Necessary SSH options for ClusterShell. Currently the default
                options used include:
                * ``-C`` - Enable compression
                * ``-oStrictHostKeyChecking=no`` - Disable host key checking because many
                clusters use the same hosts but have new keys.
                * ``-oUserKnownHostsFile=/dev/null`` - Blackholing the known hosts file
                due to auto-generated keys.
                * ``-oNumberOfPasswordPrompts=1`` - Only get a single password prompt
                (if any).
                * ``-oLogLevel=ERROR`` - Remove any debug/warnings from SSH connections.
            ssh_user (str): Specify a specific user for SSHing. This is set in the
                FIREWHEEL config.

        Args:
            host_group_name (str):The name of the host group we're representing.

        Raises:
            RuntimeError: If the hostgroup is not valid.
        """
        config = Config().get_config()
        try:
            config["cluster"][host_group_name]
        except KeyError as exp:
            raise RuntimeError(
                f"The hostgroup {host_group_name} is not valid!"
            ) from exp

        self.host_group_name = host_group_name
        self.log = Log(name="CLI").log

        # Setup options for SSH.
        self.ssh_options = " ".join(
            [
                "-C",
                "-oStrictHostKeyChecking=no",
                "-oUserKnownHostsFile=/dev/null",
                "-oNumberOfPasswordPrompts=1",
                "-oLogLevel=ERROR",
            ]
        )

        self.ssh_user = config["ssh"]["user"]

    def copy_file(self, local_file_path, remote_file_path):
        """Copy a file from the local system to all remote systems in the host group.

        File permissions (such as execute) are preserved.

        Args:
            local_file_path (str): Path to the file to be copied on the local system.
            remote_file_path (str): Destination for the file on remote systems.

        Returns:
            int: The number of errors from copying the file.
        """
        config = Config().get_config()

        # Get the list of remote hosts
        host_list = config["cluster"][self.host_group_name]

        self.log.debug(
            "Preparing to copy file %s to %s for nodes=%s.",
            local_file_path,
            remote_file_path,
            host_list,
        )
        nodeset = NodeSet.fromlist(host_list)

        task = task_self()

        # Set options
        task.set_info("ssh_options", self.ssh_options)
        if self.ssh_user:
            task.set_info("ssh_user", self.ssh_user)

        # If there is only a single node that is both the control and
        # the compute node, we can just regular copy
        if host_list != config["cluster"]["control"]:
            command_string = f"scp {local_file_path} {nodeset}:{remote_file_path}"

            worker = task.copy(
                local_file_path,
                remote_file_path,
                nodes=nodeset,
                handler=ClusterHandler(command_string),
                preserve=True,
                stderr=True,
            )
            task.run()

            # Get the number of errors
            error_count = 0
            for _node, status in worker.iter_node_retcodes():
                if status != 0:
                    error_count += 1

        else:
            error_count = 0
            try:
                subprocess.run(
                    ["/bin/cp", "-R", local_file_path, remote_file_path], check=True
                )
            except subprocess.CalledProcessError:
                error_count += 1

        self.log.debug("There were %s errors copying the file.", error_count)
        return error_count

    def run_command(self, command_string, session, arguments):
        """Run a single command on all remote systems in the host group.

        This method attempts to run the command on the remote nodes. If the command
        fails with status code `2` or `127`, this may indicate that the command/Helper is
        not found on the remote system. Therefore, we call :py:func:`sync` and then retry.
        If the retry fails or if there are other non-zero status codes the number of
        errors is returned.

        Before each command, this method appends a change directory command
        which changes directory to the users current directory.

        Args:
            command_string (str): The command to execute
            session (dict): The current CLI session dictionary, containing sequence
                number, among other things. This is largely used to pass
                to :py:func:`sync`.
            arguments (list): Arguments for the remote command.

        Returns:
            int: Non-zero if an unresolvable error is encountered in execution.
            Zero otherwise.
        """
        config = Config().get_config()

        if arguments:
            command_string = f"{command_string} {' '.join(arguments)}"

        # Make sure we switch to the correct directory on the remote system.
        working_dir = os.getcwd()
        command_string = f"cd {working_dir} 2>/dev/null; {command_string}"

        host_list = config["cluster"][self.host_group_name]
        if not host_list:
            print(
                "No hosts are found in configuration. Please set this before "
                "attempting to run the Helper."
            )
            return errno.ENODATA

        nodeset = NodeSet.fromlist(host_list)

        self.log.debug(
            "Preparing to run command=`%s` for nodes=%s.", command_string, host_list
        )

        task = task_self()

        # Set options
        task.set_info("ssh_options", self.ssh_options)
        if self.ssh_user:
            task.set_info("ssh_user", self.ssh_user)

        worker = task.shell(
            command_string,
            nodes=nodeset,
            handler=ClusterHandler(command_string),
            preserve=True,
            stderr=True,
        )
        task.run()

        # Set up variables to check for a sync error
        do_sync = False
        fatal_error_count = 0
        nodes_to_sync = []
        codes_to_sync = {2, 127}

        # Check for "Command not found" returns. If we find them we need
        # to re-sync and re-try if there are no other errors.
        for node, status in worker.iter_node_retcodes():
            if status in codes_to_sync:
                do_sync = True
                nodes_to_sync.append(node)
                message = (
                    f"Command not found on host={node} this is likely caused "
                    f"by a missing Helper cache. We will re-sync and then "
                    f"re-try."
                )
                print(message)
                self.log.warning(message)

            # Check for other errors. We don't want to re-try if we cannot
            # resolve all errors.
            if status != 0 and status not in codes_to_sync:
                fatal_error_count += 1

        # In the right circumstances, re-try.
        new_error_count = 0
        if (do_sync is True) and (fatal_error_count == 0):
            self.log.info("Re-syncing Helper cache and re-trying command.")

            # Sync Helper cache
            sync(session)

            self.log.debug(
                "Re-running command=`%s` for nodes=%s after sync.",
                command_string,
                nodes_to_sync,
            )

            # Rebuild a worker
            nodeset = NodeSet.fromlist(nodes_to_sync)
            worker = task.shell(
                command_string,
                nodes=nodeset,
                handler=ClusterHandler(command_string),
                preserve=True,
                stderr=True,
            )

            # Re-run the command
            task.run()

            # Re-check our output. We won't re-re-try, but try to give
            # some indication of what's going wrong.
            for _node, status in worker.iter_node_retcodes():
                if status != 0:
                    new_error_count += 1

            if new_error_count != 0:
                print(f"Error: {new_error_count} hosts reported errors on re-try.")
                self.log.error(
                    "%d hosts reported errors on re-try after Helper cache re-sync.",
                    new_error_count,
                )
            self.log.info("new_error_count = %s", new_error_count)
            return new_error_count

        self.log.info("fatal_error_count = %s", fatal_error_count)
        return fatal_error_count


def sync(session, helper_list=None):
    """
    Update the Helper cache on all hosts controlled by the CLI.

    Args:
        session (dict): The current CLI session.
        helper_list (dict): The in-memory dict of Helpers to sync. If not
                    specified, it will be loaded from the file system.

    Returns:
        int: The number of errors encountered while copying files. Zero on success.
    """
    logger = Log(name="CLI").log
    config = Config().get_config()

    # Load the Helper list ourselves if we have to.
    if helper_list is None:
        helper_list = utils.build_helper_dict()

    # Copy the entire cache directory out to the compute nodes.
    host_group = "compute"

    # Floating point math is weird. We want to increment by 0.1
    # however, it might get odd for certain values. In Python 3
    # we can use the ``decimal`` module to help but we must make
    # the decimal value a string input, otherwise the exact floating
    # point value will be used. See https://0.30000000000000004.com/ and
    # https://docs.python.org/3/library/decimal.html for more information.
    sequence_increment = decimal.Decimal("0.1")
    session["sequence_number"] = (
        decimal.Decimal(session["sequence_number"]) + sequence_increment
    )
    error_count = 0
    cache_directory = os.path.join(
        config["cli"]["root_dir"], config["cli"]["cache_dir"]
    )

    # Create a tmp directory for the CLI cache
    local_cache = tempfile.mkdtemp()

    # Update the temp directory permissions
    # This is okay for directories have these permissions.
    os.chmod(local_cache, 0o775)  # noqa: S103

    accessor = HostAccessor(host_group)

    # Make sure we don't already have a cache (SCP isn't that smart)
    logger.debug("Cleaning up old CLI cache for %s.", host_group)
    accessor.run_command("rm", session, ["-rf", cache_directory])

    # Build the cache directory structure locally.
    # Loop through our list of Helpers
    for helper in helper_list:
        helper_list[helper].build_cache(path=local_cache)

    Console().print(
        f"Syncing FIREWHEEL Helpers from [cyan]{utils.helpers_path}[/ cyan] "
        f"to cache directory at [cyan]{cache_directory}[/ cyan]"
    )

    session["sequence_number"] = (
        decimal.Decimal(session["sequence_number"]) + sequence_increment
    )

    # Copy the files over.
    logger.debug("Syncing cached Helper files.")
    error_count = accessor.copy_file(local_cache, cache_directory)

    if config["system"]["default_group"]:
        logger.debug(
            "Attempting to set group on Helper cache to %s.",
            config["system"]["default_group"],
        )
        group = grp.getgrnam(config["system"]["default_group"])
        errors = accessor.run_command(
            "chgrp", session, ["-R", str(group.gr_gid), cache_directory]
        )
        if errors:
            logger.warning(
                "Setting group failed for %s node(s). Continuing anyway.", errors
            )
        else:
            logger.debug("Setting group was successful!")
        session["sequence_number"] = (
            decimal.Decimal(session["sequence_number"]) + sequence_increment
        )

    # Clean up tmp directory
    shutil.rmtree(local_cache)

    return error_count
