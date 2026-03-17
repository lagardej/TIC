"""Dependency guard tests for the extracted abcdef framework."""

import abcdef


def test_abcdef_package_is_importable() -> None:
    """TIC should be able to import the extracted framework package."""
    assert hasattr(abcdef, "__all__")

