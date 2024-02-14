"""Dummy tests."""
from kfp_component_lib.hello_world import message


def test_message():
    assert message() == "Hello, world!"
