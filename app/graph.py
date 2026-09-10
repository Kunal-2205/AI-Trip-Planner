"""
graph.py

Builds the LangGraph workflow.
"""

from langgraph.graph import StateGraph, START, END

from app.state import TravelState

from app.agents.planner import planner_node
from app.agents.router import router_node, route_decision
from app.agents.transport import transport_node
from app.agents.hotel import hotel_node
from app.agents.weather import weather_node
from app.agents.places import places_node
from app.agents.budget import budget_node
from app.agents.itinerary import itinerary_node


def build_graph():

    graph = StateGraph(TravelState)

    graph.add_node("planner", planner_node)
    graph.add_node("router", router_node)
    graph.add_node("transport", transport_node)
    graph.add_node("hotel", hotel_node)
    graph.add_node("weather", weather_node)
    graph.add_node("places", places_node)
    graph.add_node("budget", budget_node)
    graph.add_node("itinerary", itinerary_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "transport": "transport",
            "hotel": "hotel",
            "weather": "weather",
            "places": "places",
            "budget": "budget",
            "itinerary": "itinerary",
            "end": END,
        },
    )

    graph.add_edge("transport", "router")
    graph.add_edge("hotel", "router")
    graph.add_edge("weather", "router")
    graph.add_edge("places", "router")
    graph.add_edge("budget", "router")
    graph.add_edge("itinerary", "router")

    return graph.compile()


compiled_graph = build_graph()