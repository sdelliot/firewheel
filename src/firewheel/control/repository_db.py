import os

from importlib_metadata import entry_points

from firewheel.config import config
from firewheel.lib.log import Log
from firewheel.lib.grpc.firewheel_grpc_client import FirewheelGrpcClient


class RepositoryDb:
    """
    Provides an interface to the Repository database on the gRPC service.

    Repositories in the database are uniquely identified by their path.

    A repository, as stored in the database, is expected to have the form::

        {
            "path": ""
        }

    """

    def __init__(
        self,
        host=config["grpc"]["hostname"],
        port=config["grpc"]["port"],
        db=config["grpc"]["db"],
    ):
        """
        Set up the connection to the gRPC server.

        Args:
            host (str): The GRPC server IP/hostname.
            port (int): The GRPC server port.
            db (str): The GRPC database.
        """
        self.log = Log(name="RepositoryDb").log
        self.grpc_client = None
        if host:
            self.grpc_client = FirewheelGrpcClient(hostname=host, port=port, db=db)

    def close(self):
        """
        Close the database connection.
        """
        self.grpc_client.close()

    def list_repositories(self):
        """
        List the repositories in the database.

        This method will list all repositories in the database and check for
        any installed Python packages that provide the ``firewheel.mc_repo``
        `entry point <https://setuptools.pypa.io/en/latest/userguide/entry_point.html>`_.

        Returns:
            list: An iterator, where each dictionary is a repository.
                (See repository format for the database).
        """
        entries = []

        # Add all model component repositories identified by the gRPC client
        if self.grpc_client is not None:
            entries.extend(list(self.grpc_client.list_repositories()))

        # Add all model components that have been added via entry points
        for entry in entry_points(group="firewheel.mc_repo"):
            entries.append({"path": entry.load()[0]})

        return iter(entries)

    def add_repository(self, repository):
        """
        Add a new repository entry to the database.

        Args:
            repository (dict): A repository dictionary to add. See format for the database.
        """
        self._validate_repository(repository)
        self.grpc_client.set_repository(repository)

    def delete_repository(self, repository):
        """
        Delete a repository entry from the database.

        Args:
            repository (dict): A repository dictionary to delete.

        Returns:
            int: Number of entries removed (expect 0 or 1), or None if an
            error occurred.
        """
        self._validate_repository(repository)
        result = self.grpc_client.remove_repository(repository)["removed_count"]
        return result

    def _validate_repository(self, repository):
        """
        Validate a given repository has the correct format

        Args:
            repository (dict): A repository dictionary to add. See format for the database.

        Raises:
            KeyError: if there is a missing key/val pair in the repository.
            FileNotFoundError: If the repository does not exist.
            PermissionError: If the user is unable to access that directory.
        """

        # Validate repository format.
        if "path" not in repository:
            raise KeyError('Cannot add malformed repository to database. Need "path".')
        expected_key_len = 1
        if len(repository.keys()) != expected_key_len:
            raise KeyError(
                "Cannot add malformed repository to database."
                f" Expected {expected_key_len} key."
            )

        # Check if the path exists
        path = os.path.abspath(repository["path"])
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Path '{path}' does not exist! Please create it before adding it as a repository."
            )

        if not os.access(path, os.R_OK):
            raise PermissionError(
                f"Do not have correct permissions to access '{path}'!"
            )
