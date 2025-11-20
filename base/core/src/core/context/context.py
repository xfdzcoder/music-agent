from contextvars import ContextVar

from pydantic import BaseModel


class Context(BaseModel):

    user_id: str
    thread_id: str
    request_id: str

    def __init__(self, *, user_id: str, thread_id: str, request_id: str):
        super().__init__(user_id=user_id, thread_id=thread_id, request_id=request_id)


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
    def user_id(cls) -> str:
        return cls.get().user_id

    @classmethod
    def thread_id(cls) -> str:
        return cls.get().thread_id

    @classmethod
    def set_thread_id(cls, thread_id: str) -> str:
        old_thread_id = cls.get().request_id
        cls._context.get().thread_id = thread_id
        return old_thread_id