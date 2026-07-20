"""Shared fixtures and configuration for the test suite.

Modules under disinfo/config.py open a JSON file at import time.  The
tests below only import modules that do NOT transitively pull in
disinfo.config, so this file is primarily a safety net: it injects a
minimal config file path into the environment so that if something ever
does trigger that import the tests still work rather than crashing.
"""
import json
import os
import tempfile

import pytest


@pytest.fixture(autouse=True, scope="session")
def minimal_config_file():
    """Write a bare-minimum .config.json and point DI_CONFIG_PATH at it."""
    cfg = {
        "idfm_api_key": "test",
        "latitude": 48.0,
        "longitude": 2.0,
        "timezone": "Europe/Paris",
        "width": 64,
        "height": 64,
        "name": "test",
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(cfg, f)
        path = f.name

    os.environ.setdefault("DI_CONFIG_PATH", path)

    yield path

    os.unlink(path)
