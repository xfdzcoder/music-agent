from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from chat.nodes.chat import chat
from chat.nodes.remember import remember
from core.graph.graph import ChatState
from core.memory import async_memory

_graph : CompiledStateGraph

async def init_graph():
    global _graph
    graph_builder = StateGraph(ChatState)

    graph_builder.add_node(chat.__name__, chat)
    graph_builder.add_node(remember.__name__, remember)

    graph_builder.add_edge(START, remember.__name__)
    graph_builder.add_edge(remember.__name__, chat.__name__)
    graph_builder.add_edge(chat.__name__, END)

    _graph = graph_builder.compile(
        checkpointer=async_memory.checkpointer,
        store=async_memory.store
    )

def get_graph():
    global _graph
    return _graph