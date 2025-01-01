"""Prettifier fixtures."""

from pytest_prettifier.prettifier import prettify


def pytest_make_parametrize_id(config, val, argname=None):
    """Prettify the id of parameterized tests."""
    return prettify(val, indent=0, newline="")
