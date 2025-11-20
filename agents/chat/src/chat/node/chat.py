import uuid

from ag_ui.core import TextMessageStartEvent, TextMessageContentEvent, TextMessageEndEvent, ToolCallResultEvent
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage, convert_to_openai_messages
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter

from chat.llm.tools import search_music_info_by_title
from core.context.context import ContextHolder
from core.llm.graph.graph import ChatState
from core.llm.langfuse.langfuse_manager import get_prompt
from core.llm.langfuse.prompt_param import PromptParam
from core.llm.llm import deepseek
from core.llm.memory.postgres import search


def chat(
        state: ChatState,
        config: RunnableConfig,
        writer: StreamWriter,
) -> ChatState:
    tools_agent = create_agent(deepseek, [search_music_info_by_title])
    messages = get_prompt(
        "chat/chat",
        prompt_param=PromptParam(input=state.messages[-1].content),
        messages_history=convert_to_openai_messages(state.messages[:-1]),
        memories=search(state.messages[-1].content)
    )

    message_id = None
    new_ai_message = None
    print(messages)
    for event in tools_agent.stream(
            input={ # noqa
                "messages": messages
            },
            config=config,
            context=ContextHolder.get(),
            stream_mode=["messages", "updates"]
    ):
        print(event)
        if not isinstance(event, tuple):
            continue
        stream_mode = event[0]
        chunk = event[1]
        if stream_mode == "messages":
            ai_message_chunk = chunk[0]
            if message_id is None:
                message_id = str(uuid.uuid4())
                writer(TextMessageStartEvent(
                    message_id=message_id,
                ))
            if not ai_message_chunk.content:
                continue
            writer(TextMessageContentEvent(
                message_id=message_id,
                delta=ai_message_chunk.content
            ))
        elif stream_mode == "updates":
            if "model" in chunk:
                new_ai_message = chunk["model"]["messages"][-1]
            elif "tools" in chunk:
                tool_message : ToolMessage = chunk["tools"]["messages"][-1]
                writer(ToolCallResultEvent(
                    message_id=message_id,
                    tool_call_id=tool_message.tool_call_id,
                    content=str(tool_message.content)
                ))

    writer(TextMessageEndEvent(
        message_id=message_id,
    ))

    return ChatState(
        messages=[new_ai_message]
    ).model_dump()
