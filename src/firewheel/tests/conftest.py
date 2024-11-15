"""
Configuration file for pytest

This file establishes shared pytest functionality, including some command
line options for testing.

Notes:
    For more information on adding command line options (such as those
    added here to skip long-running tests), see `the pytest documentation
    <https://docs.pytest.org/en/7.1.x/example/simple.html#control-skipping-of-tests-according-to-command-line-option>`.
"""

from typing import List

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Register argparse-style options for running tests.

    Register argparse-style options and ini-style config values,
    called once at the beginning of a test run. This is an
    `initialization hook
    <https://docs.pytest.org/en/7.4.x/reference/reference.html#pytest.hookspec.pytest_addoption>`
    provided by :py:mod:`pytest`.

    Args:
        parser (pytest.Parser): The parser that will received added
            options.
    """
    parser.addoption(
        "--quick",
        action="store_true",
        default=False,
        help="exclude tests marked as long",
    )


def pytest_configure(config: pytest.Config) -> None:
    """
    Enable this conftest file to perform initial configuration.

    This is an `initialization hook
    <https://docs.pytest.org/en/7.4.x/reference/reference.html#pytest.hookspec.pytest_configure>`
    provided by :py:mod`pytest`. It allows plugins and conftest files to
    perform initial configuration. The hook is called for every plugin
    and initial conftest file after command line options have been
    parsed. After that, the hook is called for other conftest files as
    they are imported.

    This specific hook adds custom markers to the test suite, such as a
    ``long`` marker to indicate long-running tests.

    Args:
        config (pytest.Config): The pytest config object.
    """
    # As a heuristic, mark tests that take more than 10 seconds as "long"
    config.addinivalue_line("markers", "long: mark test as long running")


def pytest_collection_modifyitems(
    session: pytest.Session,  # noqa: ARG001
    config: pytest.Config,
    items: List[pytest.Item],
) -> None:
    """
    Modify the set of tests/items collected by :py:mod:`pytest`.

    This is a `collection hook
    <https://docs.pytest.org/en/7.4.x/reference/reference.html#pytest.hookspec.pytest_collection_modifyitems>`
    provided by :py:mod:`pytest` to modify the set of tests or items
    collected by the test runner. The hook is called after collection
    has been performed and it may filter or re-order the items in-place.

    Args:
        session (pytest.Session): The pytest session object.
        config (pytest.Config): The pytest config object.
        items (list): A list of item objects
    """
    # Use the custom `--quick` option with the `long` marker to skip long running tests
    if config.getoption("--quick"):
        skip_long = pytest.mark.skip(
            reason="--quick option excludes long running tests"
        )
        for item in items:
            if "long" in item.keywords:
                item.add_marker(skip_long)
