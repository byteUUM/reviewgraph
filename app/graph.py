from langgraph.graph import END, START, StateGraph

from .nodes import after_critic, after_static, critic, llm_review, make_report, static_check
from .state import ReviewState


def build_graph():
    g = StateGraph(ReviewState)
    g.add_node("static", static_check)
    g.add_node("review", llm_review)
    g.add_node("critic", critic)
    g.add_node("report", make_report)
    g.add_edge(START, "static")
    g.add_conditional_edges("static", after_static, {"review": "review", "report": "report"})
    g.add_edge("review", "critic")
    g.add_conditional_edges("critic", after_critic, {"review": "review", "report": "report"})
    g.add_edge("report", END)
    return g.compile()


graph = build_graph()
