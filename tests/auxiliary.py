""" Utility functions """

from json_annotator.annotation import ErrorCode


def get_test_names() -> list[str]:
    """ 
    Returns test names

    Parameters
    ----------
    No parameters expected
            
    Returns
    -------
    `list` of `str`
        test name list
    """

    return ["complex_data", "different_items_in_array", "nulls_in_array",
            "bools_in_array"]

def error_code_registered(error_code_name: str) -> bool:
    """ 
    Tests whether an error code is known

    Parameters
    ----------
    error_code_name : `str`
        a name of error code to be searched for
        
    Returns
    -------
    `bool`
        true if the error code name is valid, false otherwise
    """

    return error_code_name in ErrorCode.__members__

def invalid_type_report(node_name: str|None, expected_type: str, where: str,
                        parent_node_name: str|None = None) -> str:
    """ 
    Creates a message about an invalid type based on the given params 

    Parameters
    ----------
    node_name : `str` or `None`
        a JSON object, array or a node of some other type, 
        if `None` string "Data" is assigned
    expected_type : `str` 
        the expected type of the value
    where : `str`
        file name with JSON content
    parent_node : `str` or `None`
        parent node name (if exists)
        
    Returns
    -------
    `str`
        error message
    """
    what: str = f'"{node_name}" node' if node_name else "Data"

    if parent_node_name:
        where = where + f', "{parent_node_name}"'

    return f"{what} should be a valid {expected_type} (file {where})"

def missing_item_report(node_name: str, where: str,
                        parent_node_name: str|None = None) -> str:
    """ 
    Creates a message about a missing item based on the given params

    Parameters
    ----------
    node_name : `str`
        a JSON object, array or a node of some other type
    where : `str`
        file name with JSON content
    parent_node : `str` or `None`
        parent node name (if exists)
        
    Returns
    -------
    `str`
        error message
    """
    if parent_node_name is not None:
        where = where + f', "{parent_node_name}"'

    return f"{node_name} node should be present (file {where})"
