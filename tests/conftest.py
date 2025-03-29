""" Test setup file """

import typing

import pytest
from json_annotator.annotation import JsonAnnotator


@pytest.fixture
def get_annotator() -> typing.Generator[JsonAnnotator, None, None]:
    """ 
    Creates a JsonAnnotator object

    Parameters
    ----------
    No parameters expected
        
    Yields
    -------
    `JsonAnnotator`
        JsonAnnotator object
    """

    annotator: JsonAnnotator = JsonAnnotator("/", " -> ")
    yield annotator
    annotator.clear_node_repr_list()
