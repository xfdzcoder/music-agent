import asyncio
from typing import Annotated

from ag_ui.core import RunAgentInput
from fastapi import APIRouter, Path
from starlette.responses import StreamingResponse

from chat.service.chat import gen_ag_ui_chat_resp, get_histories, add_thread_history, get_history
from core.context.context import ContextHolder

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@router.post("")
async def chat(agent_input: RunAgentInput):
    ContextHolder.set_thread_id(agent_input.thread_id)
    asyncio.create_task(add_thread_history(agent_input.thread_id))
    return StreamingResponse(gen_ag_ui_chat_resp(agent_input), media_type="text/event-stream")

@router.get("/histories")
async def histories():
    return await get_histories()

@router.get("/history/{thread_id}")
async def history(thread_id: Annotated[str, Path(title="LangGraph thread_id")]):
    return await get_history(thread_id)