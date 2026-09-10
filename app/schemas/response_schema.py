from typing import Any
from pydantic import BaseModel


class TripResponse(BaseModel):

    transport: Any

    hotel: Any

    weather: Any

    places: Any

    budget_summary: Any

    itinerary: Any