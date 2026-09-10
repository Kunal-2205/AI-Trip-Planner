"""
transport.py

The Transport Agent collects transport information
between the source and destination.

It uses the TransportService instead of directly calling the LLM.
"""

from app.state import TravelState
from app.services.transport_service import TransportService

transport_service = TransportService()


def transport_node(state: TravelState) -> TravelState:
    """
    Get transport details and store them in state["transport"].
    """

    transport = transport_service.compare_transport(
        
        source=state["source"],

        destination=state["destination"],

        budget=state["budget"],

        travellers=state["travellers"],

        preferred_transport=state["preferred_transport"],

        travel_style=state["travel_style"]

    )

    state["transport"] = transport.model_dump()

    state["current_step"] += 1

    return state