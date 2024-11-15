"""
Callable script wrapper for the
:py:func:`firewheel.cli.completion.get_available_cli_commands` function.
"""

from firewheel.cli.completion.actions import get_available_cli_commands

if __name__ == "__main__":
    get_available_cli_commands()
