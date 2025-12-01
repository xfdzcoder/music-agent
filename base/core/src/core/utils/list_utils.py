from symtable import Function
from typing import Any, Callable


def get_first(obj_list: list[Any], default: Any = None):
    if obj_list:
        return obj_list[0]
    return default


def index(obj_list: list[Any], item, map_item: Callable = None) -> int:
    if not obj_list:
        return -1
    for i, obj in enumerate(obj_list):
        if (map_item and map_item(obj) == item) or obj == item:
            return i
    return -1