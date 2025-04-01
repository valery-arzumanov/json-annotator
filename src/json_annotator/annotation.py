""" Core file of the package """

import enum
from typing import cast, Any

from .utils import get_type_name


class ErrorCode(enum.IntEnum):
    """ Processing error codes """

    OK = 0
    """ No errors """

    INCORRECT_INPUT_FORMAT = enum.auto()
    """ An error code signaling that the input 
        has incorrect format"""

    INTERNAL_FATAL_ERROR = enum.auto()
    """ An error code signaling that there have occurred 
        an internal problem which should be reported """

    DIFFERENT_ARRAY_ITEM_TYPES = enum.auto()
    """ An error code signaling that 
        the items of the input array have different types """

    NULLS_IN_ARRAY = enum.auto()
    """ An error code signaling that the input array has nulls """

    BOOLS_IN_ARRAY = enum.auto()
    """ An error code signaling that 
        the input array has boolean values """

class ErrorData:
    """
    Class used for keeping error data 

    Attributes
    ----------
    code : `ErrorCode`
        error code
    entity : `str` or `None`
        name of the erroneous entity; may be `None` if not required
    """

    def __init__(self) -> None:
        """ Constructs all the necessary attributes for a 
            `ErrorData` instance """

        self.code: ErrorCode = ErrorCode.OK
        self.entity: str = ""

    def get_error_code(self) -> ErrorCode:
        """
        Returns the error code

        Parameters
        ----------
        No parameters expected

        Returns
        -------
        `ErrorCode`
            error code
        """

        return self.code

    def get_error_message(self) -> str:
        """
        Returns the error message

        Parameters
        ----------
        No parameters expected

        Returns
        -------
        `str`
            error message
        """

        return f'Error occurred. Problematic entity: "{self.entity}"'



class JsonAnnotator:
    """
    The main class of the module performing the annotation

    Attributes
    ----------
    node_reprs : `list` of `str`
        the resulting node representations
    error_data : `ErrorData`
        error data
    node_separator : `str`
        a delimiter character or a string used to separate one node
        from another in an annotation string
    type_indication_mark : `str`
        a character or a string to separate a node name from a type hint
    """

    def __init__(self, node_separator: str, type_indication_mark: str) -> None:
        """ Constructs all the necessary attributes for a 
            `JsonAnnotator` instance """

        self.node_reprs: list[str] = []
        self.error_data: ErrorData = ErrorData()
        self.node_separator: str = node_separator
        self.type_indication_mark: str = type_indication_mark

    def _process_as_tuple(self, source: Any, path_to_node: str,
                          dest: list[str]) -> None:
        """ This function parses non-object and non-array JSON nodes """

        item_as_tuple: tuple[str, Any] = cast(tuple[str, Any], source)
        path_to_node = (
            item_as_tuple[0]
            if path_to_node == ""
            else f"{path_to_node}{self.node_separator}{item_as_tuple[0]}"
        )

        if isinstance(item_as_tuple[1], (int, float, str, bool)):
            path_to_node += ( f'{self.type_indication_mark}'
                              f'{get_type_name(item_as_tuple[1])}' )
            dest.append(path_to_node)
        elif item_as_tuple[1] is None:
            path_to_node += f'{self.type_indication_mark}null'
            dest.append(path_to_node)
        elif isinstance(item_as_tuple[1], (dict, list)):
            self._process_node(item_as_tuple[1], path_to_node, dest)
        else:
            self.error_data.entity = path_to_node
            self.error_data.code = ErrorCode.INTERNAL_FATAL_ERROR
            self.clear_node_repr_list()

    def _process_as_dict(self, source: Any, path_to_node: str,
                         dest: list[str]) -> None:
        """ This function parses JSON objects """

        item_as_dict: dict[str, Any] = cast(dict[str, Any], source)

        for index, elem in enumerate(item_as_dict.items()):
            path_to_node_check_value: str = "#"
            if self.node_separator in path_to_node:
                path_to_node_check_value = (
                    path_to_node[
                        path_to_node.rindex(self.node_separator)+
                                        len(self.node_separator):
                    ]
                )
            if index == 0 and not path_to_node_check_value.isnumeric():
                dest.append(f'{path_to_node}{self.type_indication_mark}object')
            self._process_node(elem, path_to_node, dest)

    def _process_as_list(self, source: Any, path_to_node: str,
                         dest: list[str]) -> None:
        """ This function parses JSON arrays """

        item_as_list: list[Any] = cast(list[Any], source)
        last_type: type = type(None)

        for index, elem in enumerate(item_as_list):
            if elem is None:
                self.error_data.entity = (
                    f'{path_to_node}{self.node_separator}{index}'
                )
                self.error_data.code = ErrorCode.NULLS_IN_ARRAY
                self.clear_node_repr_list()
                return

            if isinstance(elem, bool):
                self.error_data.entity = (
                    f'{path_to_node}{self.node_separator}{index}'
                )
                self.error_data.code = ErrorCode.BOOLS_IN_ARRAY
                self.clear_node_repr_list()
                return

            if last_type != type(elem) and last_type != type(None):
                self.error_data.entity = (
                    f'{path_to_node}{self.node_separator}{index}'
                )
                self.error_data.code = ErrorCode.DIFFERENT_ARRAY_ITEM_TYPES
                self.clear_node_repr_list()
                return

            if isinstance(elem, (int, float, str, bool)):
                last_type = type(elem)
                if index == 0:
                    dest.append(f'{path_to_node}{self.type_indication_mark}'
                                f'{get_type_name(elem)}Array')
            elif isinstance(elem, dict):
                last_type = dict
                if index == 0:
                    dest.append(f'{path_to_node}{self.type_indication_mark}'
                                f'objectArray')
                self._process_node(
                    elem, f'{path_to_node}{self.node_separator}{index}', dest
                )
            else:
                self.error_data.entity = (
                    f'{path_to_node}{self.node_separator}{index}'
                )
                self.error_data.code = ErrorCode.INTERNAL_FATAL_ERROR
                self.clear_node_repr_list()

    def _process_node(self, source: Any, path_to_node: str,
                      dest: list[str]) -> None:
        """ This function parses JSON nodes of all types """        

        if isinstance(source, tuple):
            self._process_as_tuple(source, path_to_node, dest)
            if self.error_data.code != ErrorCode.OK:
                return

        elif isinstance(source, dict):
            self._process_as_dict(source, path_to_node, dest)
        elif isinstance(source, list):
            self._process_as_list(source, path_to_node, dest)
            if self.error_data.code != ErrorCode.OK:
                return

        else:
            self.error_data.entity = path_to_node
            self.error_data.code = ErrorCode.INTERNAL_FATAL_ERROR
            return

    def build_node_reprs(self, source: dict[str, Any]) -> ErrorData:
        """
        Constructs the list of node representations

        Parameters
        ----------
        source : `dict[str, typing.Any]`
            JSON content preprocessed via 
            a `json.load` or a `json.loads` call

        Returns
        -------
        `ErrorCode`
        """

        if isinstance(source, dict):
            for item in source.items():
                self._process_node(item, str(), self.node_reprs)

            # it is ok to return self.error here: it either remains
            # intact from __init__ or modified by _process_node.
            return self.error_data

        self.error_data.entity = "Whole document"
        return ErrorCode.INCORRECT_INPUT_FORMAT

    def get_node_repr_list(self) -> list[str]:
        """
        Returns the list of node representations

        Parameters
        ----------
        No parameters expected

        Returns
        -------
        `list` of `str`
            resulting data items for all JSON nodes
        """

        return sorted(self.node_reprs)

    def clear_node_repr_list(self) -> None:
        """
        Clears the list of node representations

        Parameters
        ----------
        No parameters expected

        Returns
        -------
        `None`
        """

        self.node_reprs.clear()
