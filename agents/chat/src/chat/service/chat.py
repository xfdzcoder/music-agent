from ag_ui.core import RunAgentInput
from langchain_core.runnables import RunnableConfig

from chat.llm.graph import get_graph
from core.langfuse.langfuse_manager import langfuse_handler
from core.utils import ag_ui


async def gen_ag_ui_chat_resp(agent_input: RunAgentInput):
    yield ag_ui.run_start(agent_input)


    async for event in get_graph().astream(
        input={
            "messages": [message.model_dump() for message in agent_input.messages],
        },
        config=RunnableConfig(
            callbacks=[langfuse_handler],
            configurable={
                "thread_id": agent_input.thread_id,
                # FIXME 2025/11/8 xfdzcoder: 暂时没有用户这个维度，默认为 temp
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
