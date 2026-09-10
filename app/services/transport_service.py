"""
transport_service.py

This service handles all transport-related operations.

Responsibilities:
1. Convert city names into coordinates using Geoapify.
2. Calculate distance using the Haversine formula.
3. Compare transport options.
"""

import math
from turtle import distance
import requests

from app.config import GEOAPIFY_API_KEY
from app.services.recommendation_service import RecommendationService

from app.schemas.transport_schema import (
    TransportOption,
    TransportResponse,
)


class TransportService:

    def __init__(self):
        self.recommendation = RecommendationService()

    # --------------------------------------------------
    # Get Coordinates
    # --------------------------------------------------

    def get_coordinates(self, city: str, country_code: str = "in"):
        """
        Convert a city name into latitude/longitude using Geoapify.

        Two safeguards are applied:

        1. `type=city` restricts matches to actual cities (not
           streets/localities).
        2. `filter=countrycode:{country_code}` anchors the search to
           India by default. Without this, a query like "Goa" can
           resolve to a same-named place in another country entirely
           (this happened with a barangay in the Philippines) even
           though Geoapify reports high confidence for that match -
           confidence reflects string-match quality, not geographic
           relevance to this app's use case.

        This app is India-focused (INR pricing, Indian source/destination
        examples), so defaulting to `country_code="in"` is safe. If
        international trips are ever supported, pass country_code=None
        to disable the filter for that call.
        """

        url = "https://api.geoapify.com/v1/geocode/search"

        params = {
            "text": city,
            "type": "city",
            "format": "json",
            "limit": 1,
            "apiKey": GEOAPIFY_API_KEY
        }

        if country_code:
            params["filter"] = f"countrycode:{country_code}"

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        # Fallback: if restricting to the country filter finds nothing
        # (e.g. a genuinely misspelled city, or a real international
        # destination), retry once without the country filter so we
        # don't just fail outright - but still keep the confidence
        # guardrail below.
        if not results and country_code:
            params.pop("filter", None)
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

        if not results:
            raise Exception(f"City '{city}' not found.")

        top = results[0]

        # -----------------------------------------
        # Confidence Guardrail
        # -----------------------------------------
        # Reject low-confidence / mismatched results instead of
        # silently continuing with the wrong coordinates.

        confidence = top.get("rank", {}).get("confidence", 0)

        if confidence < 0.5:
            raise Exception(
                f"Could not confidently resolve '{city}'. "
                f"Best match was '{top.get('formatted')}' "
                f"(confidence={confidence})."
            )

        return {
            "latitude": top["lat"],
            "longitude": top["lon"]
        }

    # --------------------------------------------------
    # Calculate Distance (Haversine)
    # --------------------------------------------------

    def haversine_distance(self, start, end):

        R = 6371

        lat1 = math.radians(start["latitude"])
        lon1 = math.radians(start["longitude"])

        lat2 = math.radians(end["latitude"])
        lon2 = math.radians(end["longitude"])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

        return round(R * c, 2)

    # --------------------------------------------------
    # Compare Transport
    # --------------------------------------------------

    def compare_transport(
            self,
            source: str,
            destination: str,
            budget: int,
            travellers: int,
            preferred_transport: str,
            travel_style: str
        ) -> TransportResponse:

        # -----------------------------------------
        # Coordinates
        # -----------------------------------------

        source_coordinates = self.get_coordinates(source)
        destination_coordinates = self.get_coordinates(destination)

        # -----------------------------------------
        # Distance
        # -----------------------------------------

        distance = self.haversine_distance(
            source_coordinates,
            destination_coordinates
        )

        driving_time = round(distance / 60, 1)

        # -----------------------------------------
        # Prices PER PERSON
        # -----------------------------------------

        flight_per_person = max(2500, round(distance * 4.5))
        train_per_person = max(400, round(distance * 0.8))
        bus_per_person = max(700, round(distance * 1.5))

        # -----------------------------------------
        # Total Ticket Prices
        # -----------------------------------------

        flight_price = flight_per_person * travellers
        train_price = train_per_person * travellers
        bus_price = bus_per_person * travellers

        # -----------------------------------------
        # Car Cost
        # Car fuel cost DOES NOT multiply by travellers.
        # -----------------------------------------

        fuel_price = 105
        mileage = 15

        fuel_needed = distance / mileage
        fuel_cost = round(fuel_needed * fuel_price)

        # -----------------------------------------
        # Duration
        # -----------------------------------------

        flight_hours = max(1, round(distance / 700))
        train_hours = max(2, round(distance / 55))
        bus_hours = max(2, round(distance / 45))

        # -----------------------------------------
        # Transport Options
        # -----------------------------------------

        options = [
            TransportOption(
                mode="Flight",
                available=True,
                estimated_price=flight_price,
                duration=f"{flight_hours}h",
                distance_km=distance,
                pros=[
                    "Fastest",
                    "Saves Time"
                ],
                cons=[
                    "Expensive"
                ]
            ),

            TransportOption(
                mode="Train",
                available=True,
                estimated_price=train_price,
                duration=f"{train_hours}h",
                distance_km=distance,
                pros=[
                    "Cheapest",
                    "Comfortable"
                ],
                cons=[
                    "Long Journey"
                ]
            ),

            TransportOption(
                mode="Bus",
                available=True,
                estimated_price=bus_price,
                duration=f"{bus_hours}h",
                distance_km=distance,
                pros=[
                    "Affordable"
                ],
                cons=[
                    "Very Long Journey"
                ]
            ),

            TransportOption(
                mode="Car",
                available=True,
                estimated_price=fuel_cost,
                duration=f"{driving_time} hr",
                distance_km=distance,
                pros=[
                    "Flexible",
                    "Door-to-Door"
                ],
                cons=[
                    "Fuel Cost",
                    "Driver Fatigue"
                ]
            )
        ]

    

        print("=" * 60)
        print("Travellers :", travellers)
        print("Flight :", flight_price)
        print("Train  :", train_price)
        print("Bus    :", bus_price)
        print("Car    :", fuel_cost)
        print("=" * 60)

        # -----------------------------------------
        # Recommendation
        # -----------------------------------------

        recommended = self.recommendation.recommend_transport(

            options=[option.model_dump() for option in options],

            preferred_transport=preferred_transport,

            travel_style=travel_style,

            budget=budget

        )

        # -----------------------------------------
        # Response
        # -----------------------------------------

        return TransportResponse(

            source=source,

            destination=destination,

            recommended_mode=recommended,

            options=options

        )