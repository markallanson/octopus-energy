import json
import os
from asyncio import get_event_loop

import jsonpickle


def load_json(filename: str) -> str:
    """Load a fixture for a test from the fixtures directory.

    Args:
        filename: The name of the fixture file to load

    Returns:
        The content of the file
    """
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as fptr:
        return fptr.read()


def load_fixture_json(filename: str) -> dict:
    """Load a fixture for a test from the fixtures directory.

    Args:
        filename: The name of the fixture file to load

    Returns:
        The content of the file parsed as json.
    """
    return json.loads(load_json(os.path.join("fixtures", filename)))


def does_asyncio(func):
    """Simple decorator for running a test inside an asyncio event loop."""

    def wrapper(*args, **kwargs):
        get_event_loop().run_until_complete(func(*args, **kwargs))

    return wrapper
