"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from src.config import Settings

    return Settings(
        demo_mode=True,
        meta_app_id="test_app_id",
        meta_app_secret="test_secret",
    )
