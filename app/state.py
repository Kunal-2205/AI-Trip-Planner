from typing import TypedDict


class TravelState(TypedDict):

    # -------------------------------
    # User Request
    # -------------------------------
    source: str
    destination: str
    start_date: str
    days: int
    budget: int
    travellers: int
    travel_style: str
    preferred_transport: str
    hotel_type: str
    food_preference: str
    interests: list[str]
    user_request: str

    # -------------------------------
    # Planner
    # -------------------------------
    plan: list[str]
    current_step: int
    next_agent: str

    # -------------------------------
    # Agent Outputs
    # -------------------------------
    transport: dict
    hotel: dict
    weather: dict

    # Tourist Attractions
    places: list

    # Restaurants
    restaurants: list

    # Cafes
    cafes: list


    # Shopping
    shopping: list

    # -------------------------------
    # Budget
    # -------------------------------
    budget_summary: dict

    # -------------------------------
    # Final Output
    # -------------------------------
    itinerary: list
    final_response: dict