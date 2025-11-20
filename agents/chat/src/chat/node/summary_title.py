from langchain.agents import create_agent
from langchain_core.messages import convert_to_openai_messages, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter
from pydantic import BaseModel, Field

from core.context.context import ContextHolder
from core.db.models.user_thread import add_or_update_thread, get_name_by_thread_id
from core.llm.graph.graph import ChatState
from core.llm.langfuse.langfuse_manager import get_prompt
from core.llm.langfuse.prompt_param import CurrentTitleParam
from core.llm.llm import deepseek


class SummaryTitle(BaseModel):
    title: str = Field(description="对话标题", max_length=10, min_length=2)


def summary_title(
        state: ChatState,
        config: RunnableConfig,
        writer: StreamWriter,
):
    structured_agent = create_agent(deepseek, response_format=SummaryTitle)
    messages = get_prompt(
        "chat/summary_title",
        prompt_param=CurrentTitleParam(current_title=get_name_by_thread_id()),
        messages_history=convert_to_openai_messages(state.messages),
    )

    result : SummaryTitle | None = None
    for event in structured_agent.stream(
            input={  # noqa
                "messages": messages
            },
            config=config,
            context=ContextHolder.get(),
            stream_mode=["updates"]
    ):
        if not isinstance(event, tuple):
            continue
        stream_mode = event[0]
        chunk = event[1]
        if stream_mode == "updates":
            if "model" in chunk:
                result = chunk["model"]["structured_response"]

    if result and result.title:
        add_or_update_thread(
            ContextHolder.thread_id(),
            result.title
        )
