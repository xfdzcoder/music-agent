from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from core.llm.memory.postgres import MemoryItem


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)
    memories: Annotated[list[MemoryItem], MemoryItem.add_memories] = Field(default_factory=list)
    summary: str = ""
    is_done: bool = False


class ChatState(State):
    should_remember: bool = False
