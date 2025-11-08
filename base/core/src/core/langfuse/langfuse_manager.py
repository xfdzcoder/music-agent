from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langfuse import get_client
from langfuse.langchain import CallbackHandler

langfuse = get_client()
langfuse_handler = CallbackHandler()


PROMPT_NAMES = Literal[
    "chat/chat",
    "chat/remember"
]

def get_prompt(name: PROMPT_NAMES, *, label: str | None = "latest", type: Literal["chat", "text"] = "text"):
    prompt = langfuse.get_prompt(name, label=label, type=type)  # type: ignore[arg-type]
    return ChatPromptTemplate(
        prompt.get_langchain_prompt(),
        metadata={"langfuse_prompt": prompt}
    )
