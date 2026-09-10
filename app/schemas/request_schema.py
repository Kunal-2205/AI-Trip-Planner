from typing import List, Literal
from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    """
    Request received from the user.
    This contains everything needed to plan a trip.
    """

    source: str = Field(..., example="Mumbai")
    destination: str = Field(..., example="Chennai")

    start_date: str = Field(
        ...,
        example="2026-08-15",
        description="Trip start date (YYYY-MM-DD)"
    )

    days: int = Field(..., gt=0, example=5)

    budget: int = Field(..., gt=0, example=25000)

    travellers: int = Field(default=1, gt=0)

    home_currency: str = Field(default="INR", description="User's home currency code, e.g., INR, USD, EUR")

    travel_style: Literal[
        "Budget",
        "Luxury",
        "Family",
        "Adventure",
        "Business"
    ] = "Budget"

    preferred_transport: Literal[
        "Any",
        "Flight",
        "Train",
        "Bus",
        "Car"
    ] = "Any"

    hotel_type: Literal[
        "Any",
        "Budget",
        "3 Star",
        "4 Star",
        "5 Star"
    ] = "Budget"

    food_preference: Literal[
        "Any",
        "Vegetarian",
        "Non-Vegetarian",
        "Vegan"
    ] = "Any"

    interests: List[str] = Field(
        default_factory=list,
        example=[
            "Beach",
            "History",
            "Shopping"
        ]
    )

    user_request: str