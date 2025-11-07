from langgraph.constants import START, END
from langgraph.graph import StateGraph

from chat.llm.nodes import chat
from core.graph.graph import ChatState

__graph_builder = StateGraph(ChatState)

__chat___name = chat.__name__
__graph_builder.add_node(__chat___name, chat)


__graph_builder.add_edge(START, __chat___name)
__graph_builder.add_edge(__chat___name, END)

graph = __graph_builder.compile()
