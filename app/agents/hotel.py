"""
hotel.py

Hotel Agent

Fetches available hotels and uses the RecommendationService
to choose the best hotel based on:

- Hotel Type
- Budget
- Trip Duration
- Hotel Rating
"""

from app.state import TravelState
from app.services.hotel_service import HotelService
from app.services.recommendation_service import RecommendationService

hotel_service = HotelService()
recommendation_service = RecommendationService()


def hotel_node(state: TravelState) -> TravelState:

    # ---------------------------------------------
    # Fetch Hotels
    # ---------------------------------------------
    # Note: HotelService.get_hotels() always returns at least one
    # fallback entry ("Hotel information unavailable") even when
    # Geoapify has no results, so `hotels` is never actually empty.
    # recommend_hotel() itself already handles an empty list safely
    # (returns {}), so no extra branch is needed here.

    hotels = hotel_service.get_hotels(
        state["destination"]
    )

    # ---------------------------------------------
    # Select Best Hotel
    # ---------------------------------------------

    selected_hotel = recommendation_service.recommend_hotel(

        hotels=hotels,

        hotel_type=state["hotel_type"],

        budget=state["budget"],

        days=state["days"]

    )

    state["hotel"] = selected_hotel or {}

    state["current_step"] += 1

    return state