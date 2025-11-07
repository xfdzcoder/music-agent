from ag_ui.core import RunAgentInput
from langchain_core.runnables import RunnableConfig

from chat.llm.graph import graph
from core.langfuse.langfuse_manager import langfuse_handler
from core.logger.logger import logger
from core.utils import ag_ui


async def gen_ag_ui_chat_resp(agent_input: RunAgentInput):
    yield ag_ui.run_start(agent_input)


    async for chunk in graph.astream(
        input={
            "messages": [message.model_dump() for message in agent_input.messages],
        },
        config=RunnableConfig(
            callbacks=[langfuse_handler],
            configurable={
                "thread_id": agent_input.thread_id
            }
        ),
        stream_mode=["custom"]
    ):
        logger.info(chunk)
        if isinstance(chunk, tuple):
            yield ag_ui.base(chunk[1])
