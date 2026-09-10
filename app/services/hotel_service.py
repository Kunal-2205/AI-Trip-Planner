"""
hotel_service.py

Fetch hotels using Geoapify Places API.
Geoapify does not provide hotel prices or ratings,
so we estimate them based on hotel names.
"""

import requests

from app.config import GEOAPIFY_API_KEY
from app.services.transport_service import TransportService


class HotelService:

    BASE_URL = "https://api.geoapify.com/v2/places"

    def __init__(self):
        self.transport = TransportService()

    # --------------------------------------------------
    # Estimate Hotel Price
    # --------------------------------------------------

    def estimate_price(self, hotel_name: str):

        name = hotel_name.lower()

        if any(word in name for word in [
            "taj",
            "oberoi",
            "hyatt",
            "hilton",
            "marriott",
            "radisson",
            "itc",
            "leela",
            "westin",
            "novotel",
            "intercontinental",
            "grand",
            "palace"
        ]):
            return 9000

        elif any(word in name for word in [
            "fortune",
            "ramada",
            "lemontree",
            "ginger",
            "holiday inn",
            "ibis",
            "fern",
            "country inn"
        ]):
            return 5500

        elif any(word in name for word in [
            "resort",
            "spa",
            "beach resort"
        ]):
            return 7000

        elif any(word in name for word in [
            "lodge",
            "guest",
            "guest house",
            "hostel",
            "inn",
            "residency",
            "homestay",
            "home stay"
        ]):
            return 1200

        return 3000

    # --------------------------------------------------
    # Estimate Rating
    # --------------------------------------------------

    def estimate_rating(self, hotel_name: str):

        name = hotel_name.lower()

        if any(word in name for word in [
            "taj",
            "oberoi",
            "hyatt",
            "hilton",
            "marriott",
            "radisson",
            "itc",
            "leela",
            "westin",
            "novotel",
            "intercontinental",
            "grand",
            "palace"
        ]):
            return 4.8

        elif any(word in name for word in [
            "fortune",
            "ramada",
            "lemontree",
            "ginger",
            "holiday inn",
            "ibis",
            "fern",
            "country inn"
        ]):
            return 4.5

        elif any(word in name for word in [
            "resort",
            "spa"
        ]):
            return 4.6

        elif any(word in name for word in [
            "lodge",
            "guest",
            "guest house",
            "hostel",
            "inn",
            "residency",
            "homestay"
        ]):
            return 3.7

        return 4.2

    # --------------------------------------------------
    # Fetch Hotels
    # --------------------------------------------------

    def get_hotels(self, city: str):

        location = self.transport.get_coordinates(city)

        params = {
            "categories": "accommodation.hotel",
            "filter": f"circle:{location['longitude']},{location['latitude']},30000",
            "limit": 30,
            "apiKey": GEOAPIFY_API_KEY
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        hotels = []

        seen = set()

        for feature in data.get("features", []):

            prop = feature.get("properties", {})

            hotel_name = prop.get("name", "Unknown Hotel").strip()

            if hotel_name.lower() in seen:
                continue

            seen.add(hotel_name.lower())

            hotels.append({

                "name": hotel_name,

                "address": prop.get("formatted", ""),

                "price_per_night": self.estimate_price(hotel_name),

                "rating": self.estimate_rating(hotel_name)

            })

        hotels.sort(

            key=lambda hotel: (

                -hotel["rating"],

                hotel["price_per_night"]

            )

        )

        if not hotels:

            hotels.append({

                "name": "Hotel information unavailable",

                "address": city,

                "price_per_night": 3000,

                "rating": 4.0

            })

        return hotels