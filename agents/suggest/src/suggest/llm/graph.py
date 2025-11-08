from langgraph.constants import START, END
from langgraph.graph import StateGraph

from core.graph.graph import SuggestState
from suggest.llm.nodes import suggest, filter_existing

__graph_builder = StateGraph(SuggestState)

__suggest___name = suggest.__name__
__graph_builder.add_node(__suggest___name, suggest)

__filter_existing___name = filter_existing.__name__
__graph_builder.add_node(__filter_existing___name, filter_existing)

__graph_builder.add_edge(START, __suggest___name)
__graph_builder.add_edge(__suggest___name, __filter_existing___name)
__graph_builder.add_conditional_edges(
    __filter_existing___name,
    lambda state: "END" if state.is_done else __suggest___name,
    {
        __suggest___name: __suggest___name,
        "END": END
    }
)

_graph = __graph_builder.compile()
