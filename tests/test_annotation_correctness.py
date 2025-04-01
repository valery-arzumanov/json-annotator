""" Testing correctness of JSON annotation """

import os
import typing
import json

import pytest

from json_annotator.annotation import JsonAnnotator, ErrorCode
from .auxiliary import get_test_names

@pytest.mark.parametrize("test_name", get_test_names())
def test_annotations(
    test_name: str,
    get_annotator: JsonAnnotator
) -> None:
    """
    Tests the correctness of the annotation

    Parameters
    ----------
    test_name : `str`
        test name
    get_annotator : `JsonAnnotator`
        a `pytest` fixture required to get a JsonAnnotator object

    Returns
    -------
    `None`

    Raises
    ------
    `AssertionError`
        if the test fails.
    """

    input_path: str = os.path.abspath(f'./res/{test_name}.json')
    with open(input_path, mode='r', encoding='utf-8') as tested_file:
        tested_json: dict[str, typing.Any] = json.load(tested_file)
        error_code: ErrorCode = (
            get_annotator.build_node_reprs(tested_json["testInput"]).code
        )
        expected_error_code: str = tested_json["expectedOutput"]["errCode"]
        assert error_code == ErrorCode[expected_error_code]

        actual_node_reprs: list[str] = get_annotator.get_node_repr_list()
        expected_node_reprs: list[str] = sorted(
            tested_json["expectedOutput"]["result"]
        )
        assert actual_node_reprs == expected_node_reprs
