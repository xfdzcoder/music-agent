from typing import Any


def get_first(obj_list: list[Any], default: Any = None):
    if obj_list:
        return obj_list[0]
    return default