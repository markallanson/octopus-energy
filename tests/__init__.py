import json
import os


def load_fixture(filename: str) -> str:
    """Load a fixture for a test from the fixtures directory.

    Args:
        filename: The name of the fixture file to load

    Returns:
        The content of the file
    """
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fptr:
        return fptr.read()


def load_fixture_json(filename: str) -> dict:
    """Load a fixture for a test from the fixtures directory.

    Args:
        filename: The name of the fixture file to load

    Returns:
        The content of the file parsed as json.
    """
    return json.loads(load_fixture(filename))
