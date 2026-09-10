"""
budget.py

Budget Agent

Calculates the total trip cost using the recommended
transport, selected hotel, and day-to-day extras
(food, local transport, activities).

Source of truth for extras:
- If the itinerary has already been generated, its own
  per-day `estimated_cost` values are summed and used as
  the authoritative extras total. The itinerary LLM has
  visibility into the actual restaurants/activities chosen,
  so its estimate is more accurate than a flat formula - and
  critically, using it here means the number shown in
  budget_summary can never contradict the sum of the
  itinerary's own daily costs (which was happening before).
- If the itinerary hasn't run yet (e.g. planner ordered
  budget before itinerary, or itinerary was skipped
  entirely), we fall back to the flat per-day formula from
  RecommendationService so budget still produces a sane
  number on its own.

This makes budget_node correct regardless of what order the
planner LLM decides to run agents in.
"""

from app.state import TravelState
from app.services.recommendation_service import RecommendationService

recommendation_service = RecommendationService()


def _build_final_response(state: TravelState) -> dict:
    """
    Build final_response from whatever state is currently
    available. Both budget_node and itinerary_node call this,
    so whichever one runs last leaves final_response correct -
    without depending on a fixed graph order.
    """
    return {
        "transport": state.get("transport", {}),
        "hotel": state.get("hotel", {}),
        "weather": state.get("weather", {}),
        "places": state.get("places", []),
        "budget_summary": state.get("budget_summary", {}),
        "itinerary": state.get("itinerary", []),
    }


def budget_node(state: TravelState) -> TravelState:

    # ----------------------------------------
    # Transport Cost
    # ----------------------------------------

    transport = state.get("transport", {}).get("recommended_mode") or {}

    transport_cost = transport.get(
        "estimated_price",
        0
    )

    # ----------------------------------------
    # Hotel Cost
    # ----------------------------------------

    hotel = state.get("hotel", {}) or {}

    hotel_price = hotel.get(
        "price_per_night",
        0
    )

    hotel_cost = hotel_price * state["days"]

    # ----------------------------------------
    # Extra Costs (Food / Local Transport / Activities)
    # ----------------------------------------

    # Always compute the formula-based breakdown - useful as an
    # informational split even when the itinerary total overrides
    # the grand total below.
    formula_extras = recommendation_service.estimate_extra_costs(
        travel_style=state["travel_style"],
        days=state["days"]
    )

    food_cost = formula_extras.get("food", 0)
    local_transport_cost = formula_extras.get("local_transport", 0)
    activities_cost = formula_extras.get("activities", 0)
    formula_extras_total = food_cost + local_transport_cost + activities_cost

    itinerary = state.get("itinerary") or []

    if itinerary:
        # Single source of truth: sum the itinerary's own daily
        # estimated_cost values instead of trusting the flat formula.
        itinerary_extras_total = sum(
            day.get("estimated_cost", 0) for day in itinerary
        )
        extras_total = itinerary_extras_total
        extras_source = "itinerary"
    else:
        extras_total = formula_extras_total
        extras_source = "formula"

    # ----------------------------------------
    # Total Cost
    # ----------------------------------------

    total_cost = transport_cost + hotel_cost + extras_total

    remaining_budget = state["budget"] - total_cost

    # ----------------------------------------
    # Save Summary
    # ----------------------------------------

    state["budget_summary"] = {

        "transport_cost": transport_cost,

        "hotel_cost": hotel_cost,

        # Informational breakdown - always from the formula, even
        # when the itinerary total is used as the authoritative
        # figure below, since we don't get a food/activities/local
        # split back from the itinerary LLM.
        "food_cost": food_cost,

        "local_transport_cost": local_transport_cost,

        "activities_cost": activities_cost,

        # Authoritative total - matches the itinerary's own daily
        # costs when an itinerary exists, so the two numbers can
        # never disagree.
        "extras_total": extras_total,

        "extras_source": extras_source,

        "total_cost": total_cost,

        "remaining_budget": remaining_budget

    }

    # Keep final_response in sync regardless of run order.
    state["final_response"] = _build_final_response(state)

    state["current_step"] += 1

    return state