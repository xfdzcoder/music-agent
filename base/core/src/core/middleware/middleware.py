import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from core.context.context import ContextHolder, Context
from core.mi.player import PlayerHolder


class ContextHolderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # FIXME 2025/11/10 xfdzcoder: 暂时没有用户这个维度，默认为 temp
        user_id = "temp"
        request_id = str(uuid.uuid4())
        token = ContextHolder.set(Context(user_id=user_id, thread_id="", request_id=request_id))
        await PlayerHolder.init()
        try:
            response = await call_next(request)
            response.headers["X-Request-Id"] = request_id
            return response
        finally:
            ContextHolder.reset(token)