from ag_ui.core import RunAgentInput
from fastapi import APIRouter

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@router.post
async def chat(agent_input: RunAgentInput):
    pass