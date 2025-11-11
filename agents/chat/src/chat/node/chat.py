import uuid

from ag_ui.core import TextMessageStartEvent, TextMessageContentEvent, TextMessageEndEvent
from langchain_core.messages import AIMessageChunk, message_chunk_to_message
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter

from core.graph.graph import ChatState
from core.langfuse.langfuse_manager import get_prompt
from core.langfuse.prompt_param import ChatChatParam
from core.llm.llm import deepseek
from core.memory.async_memory import asearch


async def chat(
        state: ChatState,
        config: RunnableConfig,
        writer: StreamWriter,
) -> ChatState:
    langchain_prompt = get_prompt("chat/chat", type="chat")
    chat_chain = langchain_prompt | deepseek

    message_id = None
    ai_message_chunk = AIMessageChunk(content="")
    async for chunk in chat_chain.astream(
            ChatChatParam(
                input=state.messages[-1].content,
                messages_history=state.messages[:-1],
                memories=await asearch(state.messages[-1].content),
            ).model_dump(),
            config=config
    ):
        chunk: AIMessageChunk = chunk

        if message_id is None:
            message_id = str(uuid.uuid4())
            writer(TextMessageStartEvent(
                message_id=message_id,
            ))

        if not chunk.content:
            continue

        writer(TextMessageContentEvent(
            message_id=message_id,
            delta=chunk.content
        ))
        ai_message_chunk += chunk

    writer(TextMessageEndEvent(
        message_id=message_id,
    ))

    return ChatState(
        messages=[message_chunk_to_message(ai_message_chunk)]
    ).model_dump()
