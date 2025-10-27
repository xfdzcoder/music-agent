from langgraph.constants import START
from langgraph.graph import StateGraph

from base.core.src.graph import State
from llm.nodes import suggest

__graph_builder = StateGraph(State)

__suggest_name = suggest.__name__

__graph_builder.add_node(__suggest_name, suggest)

__graph_builder.add_edge(START, __suggest_name)

graph = __graph_builder.compile()
