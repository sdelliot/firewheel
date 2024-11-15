from abc import ABC, abstractmethod

from firewheel.lib.log import Log


class AbstractExecutor(ABC):
    """
    Abstract base class to define the Executor interface.

    As it currently stands, the division of work between __init__ and execute
    isn't all that important because they're always called in immediate
    succession.
    """

    def __init__(self, host_list_path, content):
        """
        Create a new Executor.

        Executors are intended to run a specific type of content. A new
        Executor is created for each RUN section to be executed. The content
        is always run on a group of hosts (there may only be 1 host in this
        group, however).

        Args:
            host_list_path (list): A list of hostnames (or IP addresses as strings). If
                hostnames are used, the system must be able to resolve them (when
                `ClusterShell` is ultimately called).
            content (list): The section's content that we want to
                execute. We're expected to dump it into a file for transfer,
                compile it, etc.
        """
        self.host_list_path = host_list_path
        self.content = content
        self.log = Log(name="CLI").log

    @abstractmethod
    def execute(self, cache_file, session, arguments):
        """
        Run our remote command(s).

        This method works best when it prints helpful error messages instead
        of throwing Exceptions. The CLI won't really handle decent error
        messages for us (it's too generic), but it shouldn't crash if we do end
        up throwing something.

        Args:
            cache_file (str): The file (cached copy of the section content) to try and
                              run from.
            session (dict): The overall CLI's view of the current session. This
                includes the current sequence number and session ID.
            arguments (list): Command-line arguments for the remote command. We are
                expected to pass this along to the HostAccessor's command
                execution method as well.

        Raises:
            NotImplementedError: This should be implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def get_file_extension(self):
        """
        Return the file extension expected for input files used with this Executor.

        This information is expected to be used to cache Helpers'
        RUN sections remotely.

        For example, a shell executor would expect a `.sh` extension.

        Raises:
            NotImplementedError: This should be implements by a subclass.
        """
        raise NotImplementedError
