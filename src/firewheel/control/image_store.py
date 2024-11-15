from firewheel.lib.minimega.file_store import FileStore


class ImageStore(FileStore):
    """
    A repository for VM images that uses the minimega FileStore for easy access
    on all hosts in a Firewheel cluster.
    """

    def __init__(self, store: str = "images", decompress: bool = True) -> None:
        """Initialize the ImageStore.

        Args:
            store (str): The relative path from the minimega files directory
                for this FileStore. Defaults to "images".
            decompress (bool): Whether to decompress files by default when using
                this FileStore. Defaults to True.
        """
        super().__init__(store=store, decompress=decompress)
