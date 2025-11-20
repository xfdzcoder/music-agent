from typing import Literal, Any, Union

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langfuse import get_client
from langfuse.langchain import CallbackHandler

from core.llm.langfuse.prompt_param import PromptParam

langfuse = get_client()
langfuse_handler = CallbackHandler()

PROMPT_NAMES = Literal[
    "chat/chat",
    "chat/remember",
    "chat/search_music",
]


def get_prompt(name: PROMPT_NAMES,
               *,
               label: str | None = "latest",
               type: Literal["chat", "text"] = "chat", # noqa
               prompt_param: PromptParam,
               **kwargs: Union[str, Any]) -> list[BaseMessage]:
    prompt = langfuse.get_prompt(name, label=label, type=type)  # type: ignore[arg-type]
    prompt_template = ChatPromptTemplate(prompt.get_langchain_prompt(**kwargs), metadata={"langfuse_prompt": prompt})
    return prompt_template.invoke(prompt_param.model_dump()).to_messages()