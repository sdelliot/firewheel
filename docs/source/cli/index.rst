.. _cli:

######################
Command Line Interface
######################

The FIREWHEEL Command Line Interface (CLI) allows interaction with and management of FIREWHEEL.
The CLI (:py:mod:`cli/firewheel_cli.py <firewheel.cli.firewheel_cli>`) uses Python's
:py:mod:`cmd` module.
However, there is one notable difference: the CLI is designed to work with a FIREWHEEL cluster which means that commands may need to be executed on one or many hosts.
To accomplish this, the CLI has been extended with :ref:`cli_helper_section`.
:ref:`cli_helper_section` do not use the standard `Cmd <https://docs.python.org/3/library/cmd.html>`_ format, but they enable us to use Python and Shell scripting to perform various actions across the cluster (see :ref:`cli_executors`).
The CLI automatically distributes Helpers to enable performing actions over the entire cluster.
Therefore, the CLI may be accessed from any node in the cluster.
The distinction between commands and Helpers is not relevant for most users so we will use these terms interchangeably.
CLI commands may output error message to the screen, but remote commands will indicate an error through a non-zero exit code.

.. toctree::
    :hidden:

    usage.rst
    cli_design.rst
    cli_extention.rst
    commands.rst
    helper_docs.rst
