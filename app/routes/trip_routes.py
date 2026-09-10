"""
trip_routes.py

Defines the /plan-trip API endpoint.
Runs the LangGraph workflow and returns the final travel plan.
"""

from fastapi import APIRouter

from app.schemas.request_schema import TripRequest
from app.schemas.response_schema import TripResponse
from app.graph import compiled_graph

router = APIRouter()


@router.post("/plan-trip", response_model=TripResponse)
def plan_trip(request: TripRequest):

    initial_state = {

        # ----------------------------------
        # User Input
        # ----------------------------------

        "source": request.source,
        "destination": request.destination,
        "start_date": request.start_date,
        "days": request.days,
        "budget": request.budget,
        "travellers": request.travellers,
        "travel_style": request.travel_style,
        "preferred_transport": request.preferred_transport,
        "hotel_type": request.hotel_type,
        "food_preference": request.food_preference,
        "interests": request.interests,
        "user_request": request.user_request,

        # ----------------------------------
        # Planner
        # ----------------------------------

        "plan": [],
        "current_step": 0,
        "next_agent": "",

        # ----------------------------------
        # Agent Outputs
        # ----------------------------------

        "transport": {},
        "hotel": {},
        "weather": {},

        # Tourist Attractions
        "places": [],

        # Restaurants
        "restaurants": [],

        # Cafes
        "cafes": [],
        
        # Shopping
        "shopping": [],

        # ----------------------------------
        # Budget
        # ----------------------------------

        "budget_summary": {},

        # ----------------------------------
        # Final Output
        # ----------------------------------

        "itinerary": [],
        "final_response": {}

    }

    final_state = compiled_graph.invoke(initial_state)

    return final_state["final_response"]