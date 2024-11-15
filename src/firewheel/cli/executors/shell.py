import sys
from typing import Dict, List, Optional
from decimal import Decimal

import firewheel.cli.firewheel_cli
import firewheel.lib.grpc.firewheel_grpc_server
from firewheel.cli.host_accessor import HostAccessor
from firewheel.cli.executors.abstract_executor import AbstractExecutor


class Shell(AbstractExecutor):
    """
    An Executor to handle bash shell scripts.

    This class tries to avoid throwing any Exceptions.
    """

    def execute(
        self,
        cache_file: str,
        session: Dict[str, Decimal],
        arguments: Optional[List[str]],
    ) -> int:
        """
        Execute Shell scripts via the :class:`firewheel.cli.host_accessor.HostAccessor`.

        Dump our content to a temporary file, upload it to the remote hosts
        we'll run on, then run that file (a shell script).

        This method tries to avoid throwing any Exceptions, instead printing
        helpful error messages.

        Args:
            cache_file (str): The file (cached copy of the section content) to try and
                              run from.
            session (dict): The overall CLI's view of the current session. This
                     includes the current sequence number and session ID.
            arguments (list): Command-line arguments for the remote command. We are
                       expected to pass this along to the HostAccessor's command
                       execution method as well.

        Returns:
            int: Zero on success, non-zero otherwise. Expects HostAccessor to handle
            the details of specific return code meanings.
        """
        # Try to run from the cache.
        try:
            hosts = HostAccessor(self.host_list_path)
            fw_path = firewheel.cli.firewheel_cli.__file__
            grpc_path = firewheel.lib.grpc.firewheel_grpc_server.__file__
            cache_file = (
                f"FIREWHEEL={fw_path} "
                f"FIREWHEEL_PYTHON={sys.executable} "
                f"FIREWHEEL_GRPC_SERVER={grpc_path} "
                f"{cache_file}"
            )
            return hosts.run_command(cache_file, session, arguments)
        except IOError as exp:
            print(f"Error: Local I/O error: {exp}")
            self.log.exception("Local I/O error.")

        self.log.error("Unexpected error trying to execute Helper.")
        return 1

    def get_file_extension(self) -> str:
        """
        Return the file extension expected for Shell files.

        Returns:
            str: Always returns ``.sh``.
        """
        return ".sh"
