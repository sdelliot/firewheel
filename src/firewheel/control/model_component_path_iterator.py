import os

from firewheel.lib.log import Log


class ModelComponentPathIterator:
    """
    This class takes in a repository iterator and enables searching
    over all the repositories for model components and their specific
    fully qualified paths.
    """

    def __init__(self, repositories):
        """
        Initialize the class variables and the current position of the iterator.

        Args:
            repositories (list_iterator): The list of repositories.
        """
        self.repository_iterator = repositories

        self.current_repo = None
        self.current_repo_components = None
        self.current_repo_components_position = 0

        self.log = Log(name="ModelComponentPathIterator").log

    def walk_repository_for_model_component_paths(self, path):
        """
        Search each repository for model component paths.

        Args:
            path (str): Path of the repository.

        Returns:
            list: A list of components contained within the repository.
        """
        if not os.path.exists(path):
            self.log.warning(
                "Unable to locate repository at expected location: %s", path
            )
            return []

        component_list = self._walk_dir(path)
        return component_list

    def _walk_dir(self, path):
        """
        This is a helper method for `walk_repository_for_model_component_paths()`.
        It will walk the path and create a recursive list of directories with
        the repository which are model components.

        Args:
            path (str): Path of the repository.

        Returns:
            list: A list of model component paths contained within the repository.
        """
        if self._is_path_model_component(path):
            return [path]

        ret_list = []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                ret_list.extend(self._walk_dir(os.path.join(path, entry)))
        return ret_list

    def _is_path_model_component(self, path):
        """
        Check to see if the passed-in directory is a model component. The condition for being
        a model component in this context is if a MANIFEST file exists.

        Args:
            path (str): Path of the potential model component.

        Returns:
            bool: True if a MANIFEST file exists within the directory, False otherwise.
        """
        # Walk the given repository.
        for entry in os.listdir(path):
            # If there is a manifest in this directory, stop walking, we found
            # a component.
            if os.path.isfile(os.path.join(path, entry)) and entry == "MANIFEST":
                return True
        return False

    def __iter__(self):
        return self

    def __next__(self):  # noqa: DOC502
        """
        A custom `__next__` method to get the next ModelComponentPathIterator. It resets
        all the class variables and returns a new instance.

        Returns:
            ModelComponentPathIterator: The next MCPI with a different repository.

        Raises:
            StopIteration: If there are no more repositories, this is desired
                behavior.
        """
        if self.current_repo_components is None:
            # Load the next repository
            # This should raise StopIteration if there are no more, which is
            # desired behavior.
            self.current_repo = next(self.repository_iterator)
            self.current_repo_components = (
                self.walk_repository_for_model_component_paths(
                    self.current_repo["path"]
                )
            )
            self.current_repo_components_position = 0

            # Just use the next repository if there are no components in this
            # one.
            if not self.current_repo_components:
                self.current_repo_components = None
                return self.__next__()
            # Fall-through to generic code now that we've set things up again.

        # We have either set up current repo components, or they were already
        # set up, so work through them to find the next suitable component.
        for i in range(
            self.current_repo_components_position, len(self.current_repo_components)
        ):
            self.current_repo_components_position += 1
            return self.current_repo_components[i]

        # We did not find any suitable components, so try the next repo.
        self.current_repo_components = None
        return self.__next__()
