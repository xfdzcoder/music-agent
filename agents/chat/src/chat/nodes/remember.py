from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from core.graph.graph import ChatState
from core.langfuse.langfuse_manager import get_prompt
from core.llm.llm import deepseek
from core.logger.logger import logger
from core.memory.async_memory import put_memory, MemoryItem


class ShouldRememberResult(BaseModel):
    should_remember: bool = Field(description="是否应被记忆")


async def remember(
        state: ChatState,
        config: RunnableConfig,
) -> ChatState:
    langchain_prompt = get_prompt("chat/remember", type="chat")
    structured_llm = deepseek.with_structured_output(ShouldRememberResult, method="json_mode")
    chat_chain = langchain_prompt | structured_llm

    result : ShouldRememberResult | None = None
    async for chunk in chat_chain.astream(
        {
            "input": state.messages[-1].content
        },
        config=config
    ):
        logger.info(f"Should remember: {result}")
        result = chunk

    if result is not None and isinstance(result.should_remember, bool):
        state.should_remember = result.should_remember
    if state.should_remember:
        await put_memory(MemoryItem(content=state.messages[-1].content))
    return state
