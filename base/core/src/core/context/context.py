from contextvars import ContextVar

from pydantic import BaseModel


class Context(BaseModel):

    user_id: str
    request_id: str

    def __init__(self, *, user_id: str, request_id: str):
        super().__init__(user_id=user_id, request_id=request_id)


class ContextHolder:
    _context: ContextVar[Context] = ContextVar("context")

    @classmethod
    def get(cls) -> Context:
        return cls._context.get()

    @classmethod
    def set(cls, context: Context):
        return cls._context.set(context)

    @classmethod
    def reset(cls, token):
        cls._context.reset(token)

    @classmethod
    def user_id(cls):
        return cls.get().user_id
