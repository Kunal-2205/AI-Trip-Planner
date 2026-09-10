"""
itinerary.py

Itinerary Agent

Uses the LLM to generate a personalized travel itinerary
using all collected information.
"""

from app.llm import get_llm, invoke_structured
from app.prompts.prompts import ITINERARY_PROMPT
from app.schemas.agent_schemas import ItineraryOutput
from app.state import TravelState


def _build_final_response(state: TravelState) -> dict:
    """
    Build final_response from whatever state is currently
    available. Both itinerary_node and budget_node call this,
    so whichever one runs last leaves final_response correct -
    without depending on a fixed graph order. Keep this in sync
    with the copy in budget.py if either changes.
    """
    return {
        "transport": state.get("transport", {}),
        "hotel": state.get("hotel", {}),
        "weather": state.get("weather", {}),
        "places": state.get("places", []),
        "budget_summary": state.get("budget_summary", {}),
        "itinerary": state.get("itinerary", []),
    }


def itinerary_node(state: TravelState) -> TravelState:

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        ItineraryOutput
    )

    # ---------------------------------------------
    # Safe lookups
    # ---------------------------------------------
    # The planner LLM decides which agents run, and it may
    # produce a plan that includes "itinerary" without having
    # run "transport", "hotel", "weather", or "places" first.
    # Using .get() with defaults here means we still produce a
    # best-effort itinerary instead of crashing with a KeyError.

    transport_info = state.get("transport", {}).get("recommended_mode") or {}
    hotel_info = state.get("hotel", {}) or {}
    weather_info = state.get("weather", {}) or {}
    places_info = state.get("places", []) or []
    restaurants_info = state.get("restaurants", []) or []
    cafes_info = state.get("cafes", []) or []
    shopping_info = state.get("shopping", []) or []

    prompt = ITINERARY_PROMPT.format(

        source=state["source"],
        destination=state["destination"],
        days=state["days"],
        budget=state["budget"],
        travel_style=state["travel_style"],
        preferred_transport=state["preferred_transport"],
        food_preference=state["food_preference"],
        interests=", ".join(state["interests"]),

        transport=transport_info,
        hotel=hotel_info,
        weather=weather_info,
        places=places_info,

        restaurants=restaurants_info,
        cafes=cafes_info,
        shopping=shopping_info

    )

    try:
        result: ItineraryOutput = invoke_structured(
            structured_llm,
            prompt
        )
        state["itinerary"] = [
            day.model_dump()
            for day in result.itinerary
        ]
    except Exception as e:
        print(f"Itinerary generation failed: {e}")
        # Fallback itinerary for the required number of days
        state["itinerary"] = [
            {
                "day": i,
                "morning": "Explore local attractions",
                "lunch": "Lunch at a recommended restaurant",
                "afternoon": "Continue sightseeing or relax",
                "evening": "Enjoy the evening atmosphere",
                "dinner": "Dinner at a local restaurant",
                "stay": hotel_info.get("name", "Recommended Hotel"),
                "estimated_cost": 2000
            }
            for i in range(1, state.get("days", 5) + 1)
        ]

    # Keep final_response in sync regardless of run order. If
    # budget_node hasn't run yet, budget_summary will just be
    # whatever's currently in state (possibly {}) - budget_node
    # will overwrite final_response with the authoritative,
    # itinerary-aware total when it runs.
    state["final_response"] = _build_final_response(state)

    state["current_step"] += 1

    return state