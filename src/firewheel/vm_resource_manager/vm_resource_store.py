from firewheel.lib.minimega.file_store import FileStore


class VmResourceStore(FileStore):
    """
    A repository for VM resources that uses the minimega FileStore for easy access
    on all hosts in a Firewheel cluster.
    """

    def __init__(self, store="vm_resources", decompress=False):
        """
        Initialize the :class:`VmResourceStore`.

        Args:
            store (str): The name of the resource store. Defaults to "vm_resources".
            decompress (bool): Whether to decompress files. Defaults to False.
        """
        super().__init__(store=store, decompress=decompress)
