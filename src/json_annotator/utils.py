""" Utility functions """

import typing


def get_type_name(variable: typing.Any) -> str:
    """ 
    Gets the variable type name

    Parameters
    ----------
    variable : `typing.Any`
        the variable
    
    Returns
    -------
    `str`
        variable type name
    """

    return type(variable).__name__
