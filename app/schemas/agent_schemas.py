"""
agent_schemas.py

Structured outputs for LangGraph agents.
"""

from typing import List
from pydantic import BaseModel, Field


# --------------------------------------------------
# Planner
# --------------------------------------------------

class PlannerOutput(BaseModel):

    tasks: List[str] = Field(
        description="Ordered list of agents to execute."
    )


# --------------------------------------------------
# Places
# --------------------------------------------------

class Place(BaseModel):

    name: str = Field(
        description="Tourist attraction name"
    )

    reason: str = Field(
        description="Why this attraction matches the user's interests"
    )


class PlacesOutput(BaseModel):

    places: List[Place] = Field(
        description="Top recommended tourist attractions"
    )


# --------------------------------------------------
# Itinerary
# --------------------------------------------------

class DayPlan(BaseModel):

    day: int = Field(
        description="Day number"
    )

    breakfast: str = Field(
        description="Recommended breakfast restaurant"
    )

    morning: str = Field(
        description="Morning sightseeing or activity"
    )

    lunch: str = Field(
        description="Recommended lunch restaurant"
    )

    afternoon: str = Field(
        description="Afternoon activity"
    )

    evening: str = Field(
        description="Evening activity"
    )

    dinner: str = Field(
        description="Recommended dinner restaurant"
    )

    stay: str = Field(
        description="Hotel for the night"
    )

    estimated_cost: int = Field(
        description="Estimated cost for the day in INR"
    )


class ItineraryOutput(BaseModel):

    itinerary: List[DayPlan] = Field(
        description="Complete day-wise travel itinerary"
    )