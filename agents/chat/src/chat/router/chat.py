from ag_ui.core import RunAgentInput
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from chat.service.chat import gen_ag_ui_chat_resp

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@router.post("")
async def chat(agent_input: RunAgentInput):
    return StreamingResponse(gen_ag_ui_chat_resp(agent_input), media_type="text/event-stream")