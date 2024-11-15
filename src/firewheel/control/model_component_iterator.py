from firewheel.control.model_component import ModelComponent
from firewheel.control.model_component_path_iterator import ModelComponentPathIterator


class ModelComponentIterator:
    """
    This class iterates over the various repositories looking for model components.
    """

    def __init__(self, repositories):
        """
        Initialize the path iterator.

        Args:
            repositories (list_iterator): The list of repositories.
        """
        self.path_iter = ModelComponentPathIterator(repositories)

    def __iter__(self):
        return self

    def __next__(self):
        return ModelComponent(path=next(self.path_iter))
