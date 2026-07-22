"""pytest configuration - enables async test support via anyio."""
import pytest

def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.anyio)
