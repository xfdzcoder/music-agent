from abc import abstractmethod, ABC
from typing import ClassVar

from pydantic import BaseModel


class BaseRedisModel(BaseModel, ABC):
    _key_format: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls._key_format is None:
            raise TypeError(
                f"{cls.__name__} 必须定义类变量 '_key_format'"
            )

    @classmethod
    @abstractmethod
    def format_key(cls, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
