"""
This file holds various specific exceptions.
"""


class MissingImageError(Exception):
    """
    This exception occurs when required image is not uploaded.
    """


class MissingVmResourceError(Exception):
    """
    This exception occurs when a vm resource is not included in a model component.
    """

    def __init__(self, path):
        """
        Initialize exception.

        Args:
            path (str): The path is the path of the model component
        """
        Exception.__init__(self)
        self.path = path

    def __str__(self):
        return f"The vm resource {self.path} is not present."


class MissingRequiredVMResourcesError(Exception):
    """
    This exception occurs when required vm_resource(s) are not uploaded.
    """

    def __init__(self, vm_resources):
        """
        Initialize exception.

        Args:
            vm_resources (list): A list of vm_resources that are not uploaded.
        """
        Exception.__init__(self)
        self.vm_resources = vm_resources

    def __str__(self):
        return f"These vm_resources have not been uploaded: {self.vm_resources}"


class ModelComponentImportError(Exception):
    """
    This is caused if a plugin or model component objects file fail to import
    an object correctly. This is typically caused by importing a model component
    but neglecting to depend on the that model component in the `MANIFEST` file.
    """

    def __init__(self, mc_name, error):
        """
        Initialize exception.

        Args:
            mc_name (str): The name of the model component which had the error.
            error (list): The bottom few lines of the stack trace which caused this problem.
        """
        Exception.__init__(self)

        self.name = mc_name
        try:
            self.filename = error[0].split('"')[1]
        except IndexError:
            self.filename = None

        try:
            self.importline = error[1].strip()
        except IndexError:
            self.importline = None

        # Get the last element from the error. In this case it will be the
        # model component which could not be imported.
        try:
            self.error = error[2].split()[-1]
        except IndexError:
            self.error = error

    def __str__(self):
        return str(
            f"\n\nModel Component '{self.name}' could not import {self.error}.\n"
            "This is typically caused by either importing a model component but neglecting "
            "to depend on it in the MANIFEST file or a spelling mistake.\n"
            f"The file causing the error is '{self.filename}'.\n"
            f"The failing line is: '{self.importline}'"
        )
