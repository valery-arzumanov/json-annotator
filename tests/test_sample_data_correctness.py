""" Testing presence and format correctness of test data files """

import os
import json
import typing
import pytest

from .auxiliary import (
    invalid_type_report, missing_item_report, error_code_registered,
    get_test_names
)


@pytest.mark.parametrize("test_name", get_test_names())
def test_resource_file_presence(test_name: str) -> None:
    """
    Check the presence of the file necessary 
    to run the test with the given name

    Parameters
    ----------
    test_name
        test name

    Returns
    -------
    `None`

    Raises
    ------
    `AssertionError`
        if the test fails.
    """

    input_path: str = os.path.abspath(f'./res/{test_name}.json')
    assert os.path.isfile(input_path), f'File "{input_path} not found'

@pytest.mark.parametrize("test_name", get_test_names())
def test_resource_file_format_correctness(test_name: str) -> None:
    """
    Checks the format correctness of the file
    necessary to run the test with the given name

    Parameters
    ----------
    test_name
        test name

    Returns
    -------
    `None`

    Raises
    ------
    `AssertionError`
        if the test fails.
    """

    input_path: str = os.path.abspath(f'./res/{test_name}.json')
    try:
        with open(input_path, mode='r', encoding='utf-8') as tested_file:
            tested_json: dict[str, typing.Any] = json.load(tested_file)

            # General checks
            assert isinstance(tested_json, dict), (
                invalid_type_report(None, "JSON object", input_path)
            )

            # Test input data checks
            assert "testInput" in tested_json, (
                missing_item_report("testInput", input_path)
            )

            assert isinstance(tested_json["testInput"], dict), (
                invalid_type_report("testInput", "JSON object", input_path)
            )

            # Expected output data checks
            assert "expectedOutput" in tested_json, (
                missing_item_report("expectedOutput", input_path)
            )

            assert isinstance(tested_json["expectedOutput"], dict), (
                invalid_type_report("expectedOutput", "JSON object",
                                    input_path)
            )

            assert "result" in tested_json["expectedOutput"], (
                missing_item_report("result", input_path, "expectedOutput")
            )

            assert isinstance(tested_json["expectedOutput"]["result"], list), (
                invalid_type_report("result", "JSON array", input_path,
                                    "expectedOutput")
            )

            assert "errCode" in tested_json["expectedOutput"], (
                missing_item_report("errCode", input_path, "expectedOutput")
            )

            assert isinstance(tested_json["expectedOutput"]["errCode"], str), (
                invalid_type_report("errCode", "string", input_path,
                                    "expectedOutput")
            )

            error_code: str = tested_json["expectedOutput"]["errCode"]
            assert error_code_registered(error_code), (
                'Value of "errCode" is not a valid error code name'
            )

    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        pytest.fail(f'File "{input_path}" is not a valid JSON file.'
                    f'Exception info: {exc}')
