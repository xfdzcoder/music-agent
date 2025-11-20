from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter
from pydantic import BaseModel, Field

from core.context.context import ContextHolder
from core.llm.graph.graph import ChatState
from core.llm.langfuse.langfuse_manager import get_prompt
from core.llm.langfuse.prompt_param import PromptParam
from core.llm.llm import deepseek
from core.llm.memory.postgres import put, MemoryItem


class ShouldRememberResult(BaseModel):
    should_remember: bool = Field(description="是否应被记忆")
    content: str = Field(description="需要被记忆的内容")


def remember(
        state: ChatState,
        config: RunnableConfig,
        writer: StreamWriter
) -> ChatState:
    messages = get_prompt("chat/remember", prompt_param=PromptParam(input=state.messages[-1].content))
    structured_agent = create_agent(deepseek, response_format=ShouldRememberResult)

    result: ShouldRememberResult | None = None
    for event in structured_agent.stream(
            { # noqa
                "messages": messages
            },
            config=config,
            context=ContextHolder.get(),
            stream_mode=["updates"]
    ):
        if not isinstance(event, tuple):
            continue
        stream_mode, chunk = event
        model = chunk["model"]
        if model:
            result = model["structured_response"]

    if result is not None and isinstance(result.should_remember, bool) and result.should_remember:
        state.should_remember = result.should_remember
        put(MemoryItem(content=result.content))
    return state
