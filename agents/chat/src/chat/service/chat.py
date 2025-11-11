from ag_ui.core import RunAgentInput
from langchain_core.runnables import RunnableConfig

from chat.llm.graph import get_graph
from chat.repository.user_thread import add_or_update_thread, list_thread
from core.context.context import ContextHolder
from core.langfuse.langfuse_manager import langfuse_handler
from core.utils import ag_ui


async def gen_ag_ui_chat_resp(agent_input: RunAgentInput):
    yield ag_ui.run_start(agent_input)

    async for event in get_graph().astream(
            input={
                "messages": [message.model_dump() for message in agent_input.messages],
            },
            context=ContextHolder.get(),
            config=RunnableConfig(
                callbacks=[langfuse_handler],
                configurable={
                    "thread_id": agent_input.thread_id,
                    "user_id": "temp"
                }
            ),
            stream_mode=["custom"]
    ):
        if not isinstance(event, tuple):
            continue
        event_type = event[0]
        event_content = event[1]
        if event_type == "custom":
            yield ag_ui.base(event_content)

async def add_thread_history(thread_id: str):
    await add_or_update_thread(thread_id)

async def get_histories():
    return await list_thread()

async def get_history(thread_id: str):
    state = await get_graph().aget_state(RunnableConfig(configurable={"thread_id": thread_id, }))
    return state.values["messages"] or []
