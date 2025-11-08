from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from core.memory.async_memory import MemoryItem


class PromptParam(BaseModel):
    input: str


class ChatChatParam(PromptParam):
    messages_history: list[BaseMessage]
    memories: list[MemoryItem]
