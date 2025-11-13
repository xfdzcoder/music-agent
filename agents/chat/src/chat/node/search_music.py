# import uuid
# from typing import Any
#
# from ag_ui.core import TextMessageEndEvent, TextMessageContentEvent, TextMessageStartEvent, ToolCallStartEvent, \
#     ToolCallChunkEvent
# from langchain_core.messages import AIMessageChunk, message_chunk_to_message
# from langchain_core.runnables import RunnableConfig
# from langgraph.types import StreamWriter
#
# from chat.llm.tools import search_music_info_by_title
# from core.graph.graph import ChatState
# from core.langfuse.langfuse_manager import get_prompt
# from core.langfuse.prompt_param import ChatChatParam
# from core.llm.llm import deepseek
# from core.memory.async_memory import asearch
#
#
# async def search_music(
#         state: ChatState,
#         config: RunnableConfig,
#         writer: StreamWriter,
# ) -> ChatState:
#     deepseek_with_tools = deepseek.bind_tools([search_music_info_by_title])
#     langchain_prompt = get_prompt("chat/search_music", type="chat")
#     chat_chain = langchain_prompt | deepseek_with_tools
#
#     message_id = None
#     ai_message_chunk = AIMessageChunk(content="")
#     tool_buffers: dict[str, dict[str, Any]] = {}
#     last_started_tool_id: str | None = None
#     async for chunk in chat_chain.invoke(
#             ChatChatParam(
#                 input=state.messages[-1].content,
#                 messages_history=state.messages[:-1],
#                 memories=await asearch(state.messages[-1].content),
#             ).model_dump(),
#             config=config
#     ):
#         chunk: AIMessageChunk = chunk
#         message_id = init_message_id(message_id, writer)
#
#         if chunk.content:
#             writer(TextMessageContentEvent(message_id=message_id, delta=chunk.content))
#
#         if getattr(chunk, "tool_calls", None):
#             for tool_call in chunk.tool_calls:
#                 call_id = tool_call.get("id")
#                 name = tool_call.get("name")
#                 if call_id and name:
#                     tool_buffers.setdefault(call_id, {"name": name, "chunks": [], "closed": False})
#                     last_started_tool_id = call_id
#                     # 发起 start event 到前端
#                     writer(ToolCallStartEvent(tool_call_id=call_id, tool_call_name=name, parent_message_id=message_id))
#
#         # 3) 接收 tool_call_chunks（模型把 args 分片发来）
#         if getattr(chunk, "tool_call_chunks", None):
#             for tool_call_chunk in chunk.tool_call_chunks:
#                 # tcc example: {'name': 'search_music_info_by_title', 'args': '{"keyword": "于是"}', 'id': 'call_00_..', 'index': 0}
#                 arg_chunk = tool_call_chunk.get("args", "")
#                 tid = tool_call_chunk.get("id") or last_started_tool_id
#                 name = tool_call_chunk.get("name")
#
#                 buf = tool_buffers.setdefault(tid, {"name": name, "chunks": [], "closed": False})
#                 buf["chunks"].append(arg_chunk)
#
#                 writer(
#                     ToolCallChunkEvent(
#                         tool_call_id=tid, tool_call_name=buf["name"],
#                         parent_message_id=message_id,
#                         delta=arg_chunk
#                     )
#                 )
#
#         finish_reason = getattr(chunk, "finish_reason", None)
#         chunk_pos = getattr(chunk, "chunk_position", None)
#         if finish_reason == "tool_calls" or chunk_pos == "last":
#
#
#         ai_message_chunk += chunk
#
#     writer(
#         TextMessageEndEvent(
#             message_id=message_id,
#         )
#     )
#
#     return ChatState(
#         messages=[message_chunk_to_message(ai_message_chunk)]
#     ).model_dump()
#
#
# def init_message_id(message_id: str | None, writer: StreamWriter) -> str:
#     if message_id is None:
#         message_id = str(uuid.uuid4())
#         writer(TextMessageStartEvent(message_id=message_id))
#     return message_id
