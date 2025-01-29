from typing import Any, Dict
import re

class TypedDict:
    def __init__(self, enforce_schema: bool=True, enforce_typing: bool=True, schema: Dict[str, Any]=None) -> None:
        """
        Initialize with a schema where keys are the expected fields and
        values are the expected types.
        """
        self._enforce_schema = enforce_schema
        self._enforce_typing = enforce_typing
        self._schema = schema
        self._data = {}

    def __setitem__(self, key: str=None, value: Any=None) -> None:
        """
        Validate the key and value type when setting an item.
        If the key is param1...n, we will allow it.
        """
        if re.match(r'^param[\d+]', key):
            self._data[key] = value
            return
        if self._enforce_schema:
            if key not in self._schema:
                raise KeyError(f"Key '{key}' is not allowed.")
        if self._enforce_typing:
            expected_type = self._schema[key]
            if not isinstance(value, expected_type):
                raise TypeError(f"Value for '{key}' must be of type {expected_type.__name__}.")
        self._data[key] = value

    def __getitem__(self, key: str=None) -> Any:
        """
        Retrieve the value for the given key.
        """
        return self._data[key]

    def __repr__(self):
        """
        String representation of the TypedDict.
        """
        return repr(self._data)
    
    def __contains__(self, key: str=None) -> bool:
        """
        Check if a key exists in the TypedDict schema.
        """
        return key in self._data
    
    def items(self):
        """
        Return a view object that displays a list of dictionary's key-value tuple pairs.
        """
        return self._data.items()

    def pop(self, key: str=None) -> Dict[str, Any]:
        """
        Remove the item with the specified key from the TypedDict.
        If the key is not present in the data, raise a KeyError.
        """
        if key not in self._data:
            raise KeyError(f'Key "{key}" does not exist in the data.')
        return self._data.pop(key)

class Params(TypedDict):
    def __init__(self, enforce_schema: bool=True, enforce_typing: bool=True) -> None:
        super().__init__(
            enforce_schema = enforce_schema,
            enforce_typing = enforce_typing,
            schema={
                'ansi': bool,
                'color': str,
                'emojize': bool,
                'font': str,
                'length': int,
                'md': bool,
                'sfcolor': str,
                'sfsize': int,
                'size': int,
                'symbolize': bool,
                'trim': bool,

                'alternate': bool,
                'checked': bool,
                'dropdown': bool,
                'image': str,
                'sfimage': str,
                'templateImage': str,
                'tooltip': str,

                'bash': str,
                'cmd': list,
                'disabled': bool,
                'href': str,
                'key': str,
                'refresh': bool,
                'shell': str,
                'shortcut': str,
                'terminal': bool,
            }
        )

class ParamsXbar(TypedDict):
    def __init__(self, enforce_schema: bool=True, enforce_typing: bool=True) -> None:
        super().__init__(
            enforce_schema = enforce_schema,
            enforce_typing = enforce_typing,
            schema={
                'ansi': bool,
                'color': str,
                'emojize': bool,
                'font': str,
                'length': int,
                'size': int,
                'trim': bool,

                'alternate': bool,
                'dropdown': bool,
                'image': str,
                'templateImage': str,

                'bash': str,
                'cmd': list,
                'disabled': bool,
                'href': str,
                'key': str,
                'refresh': bool,
                'shell': str,
                'terminal': bool,
            }
        )

class ParamsSwiftBar(TypedDict):
    def __init__(self, enforce_schema: bool=True, enforce_typing: bool=True) -> None:
       super().__init__(
           enforce_schema = enforce_schema,
           enforce_typing = enforce_typing,
           schema = {
            'ansi': bool,
            'color': str,
            'emojize': bool,
            'font': str,
            'length': int,
            'md': bool,
            'sfcolor': str,
            'sfsize': int,
            'size': int,
            'symbolize': bool,
            'trim': bool,

            'alternate': bool,
            'checked': bool,
            'dropdown': bool,
            'image': str,
            'sfimage': str,
            'templateImage': str,
            'tooltip': str,

            'bash': str,
            'cmd': list,
            'href': str,
            'refresh': bool,
            'shell': str,
            'shortcut': str,
            'terminal': bool,
        }
    )
