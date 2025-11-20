from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from chat.node.chat import chat
from chat.node.remember import remember
from chat.node.summary_title import summary_title
from core.llm.graph.graph import ChatState
from core.llm.memory import postgres

_graph : CompiledStateGraph

def init_graph():
    global _graph
    graph_builder = StateGraph(ChatState)

    graph_builder.add_node(chat.__name__, chat)
    graph_builder.add_node(remember.__name__, remember)
    graph_builder.add_node(summary_title.__name__, summary_title)

    graph_builder.add_edge(START, remember.__name__)
    graph_builder.add_edge(remember.__name__, chat.__name__)
    graph_builder.add_edge(chat.__name__, summary_title.__name__)
    graph_builder.add_edge(summary_title.__name__, END)

    _graph = graph_builder.compile(
        checkpointer=postgres.get_checkpointer(),
        store=postgres.get_store()
    )

def get_graph():
    global _graph
    return _graph