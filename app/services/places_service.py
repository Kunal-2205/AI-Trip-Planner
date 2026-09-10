"""
places_service.py

Fetch real places from Geoapify.
"""

import requests

from app.config import GEOAPIFY_API_KEY
from app.services.transport_service import TransportService


class PlacesService:

    BASE_URL = "https://api.geoapify.com/v2/places"

    def __init__(self):
        self.transport = TransportService()

    def get_places(
        self,
        city: str,
        category: str,
        radius: int = 30000,
        limit: int = 20
    ):

        location = self.transport.get_coordinates(city)

        params = {

            "categories": category,

            "filter": f"circle:{location['longitude']},{location['latitude']},{radius}",

            "limit": limit,

            "apiKey": GEOAPIFY_API_KEY

        }

        response = requests.get(

            self.BASE_URL,

            params=params,

            timeout=30

        )

        response.raise_for_status()

        data = response.json()

        places = []

        seen = set()

        for feature in data.get("features", []):

            prop = feature.get("properties", {})

            name = prop.get("name")

            if not name:
                continue

            if name.lower() in seen:
                continue

            seen.add(name.lower())

            places.append({

                "name": name,

                "address": prop.get("formatted", "")

            })

        return places