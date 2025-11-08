from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from chat.llm.nodes import chat
from core.graph.graph import ChatState
from core.memory import memory

_graph : CompiledStateGraph

async def init_graph():
    global _graph
    __graph_builder = StateGraph(ChatState)

    __chat___name = chat.__name__
    __graph_builder.add_node(__chat___name, chat)


    __graph_builder.add_edge(START, __chat___name)
    __graph_builder.add_edge(__chat___name, END)

    _graph = __graph_builder.compile(
        checkpointer=memory.async_checkpointer,
    )

def get_graph():
    global _graph
    return _graph