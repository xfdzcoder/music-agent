from langfuse import Langfuse  # type: ignore
from langfuse.langchain import CallbackHandler  # type: ignore

langfuse = Langfuse()
langfuse_handler = CallbackHandler()
