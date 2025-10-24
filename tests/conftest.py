"""Pytest configuration for Portal Gun tests."""

import sys
from pathlib import Path

# Add project root to path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up mock modules to be available as if they were real MicroPython modules
from tests.mocks import mock_machine, mock_neopixel, mock_time

sys.modules['machine'] = mock_machine
sys.modules['neopixel'] = mock_neopixel
sys.modules['time'] = mock_time

import pytest


@pytest.fixture(autouse=True)
def reset_mock_time():
    """Reset mock time before each test"""
    mock_time.reset()
    yield
    mock_time.reset()
