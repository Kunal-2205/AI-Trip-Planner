"""
recommendation_service.py

Central Recommendation Engine

Responsible for:

1. Selecting the best transport
2. Selecting the best hotel
3. Estimating food/local travel/activity costs
4. Generating travel tips
5. Building recommendation summary
"""


class RecommendationService:

    # --------------------------------------------------
    # Transport Recommendation
    # --------------------------------------------------

    def recommend_transport(
        self,
        options: list,
        preferred_transport: str,
        travel_style: str,
        budget: int
    ):

        preferred_transport = preferred_transport.lower().strip()
        travel_style = travel_style.lower().strip()

        # -----------------------------
        # User Preference
        # -----------------------------

        if preferred_transport != "any":

            for option in options:

                if option["mode"].lower() == preferred_transport:
                    return option

        # -----------------------------
        # Distance
        # -----------------------------

        distance = options[0]["distance_km"]

        # -----------------------------
        # Luxury Traveller
        # -----------------------------

        if travel_style == "luxury":

            if distance > 500:

                for option in options:
                    if option["mode"] == "Flight":
                        return option

            else:

                for option in options:
                    if option["mode"] == "Car":
                        return option

        # -----------------------------
        # Budget Traveller
        # -----------------------------

        if travel_style == "budget":

            affordable = [

                option

                for option in options

                if option["estimated_price"] <= budget * 0.20

            ]

            if affordable:

                return min(
                    affordable,
                    key=lambda x: x["estimated_price"]
                )

            return min(
                options,
                key=lambda x: x["estimated_price"]
            )

        # -----------------------------
        # Family Traveller
        # -----------------------------

        if travel_style == "family":

            if distance < 350:

                for option in options:
                    if option["mode"] == "Car":
                        return option

            else:

                for option in options:
                    if option["mode"] == "Train":
                        return option

        # -----------------------------
        # Adventure Traveller
        # -----------------------------

        if travel_style == "adventure":

            for mode in ["Car", "Train", "Bus"]:

                for option in options:

                    if option["mode"] == mode:
                        return option

        # -----------------------------
        # Default
        # -----------------------------

        return min(
            options,
            key=lambda x: x["estimated_price"]
        )

    # --------------------------------------------------
    # Hotel Recommendation
    # --------------------------------------------------

    def recommend_hotel(
        self,
        hotels: list,
        hotel_type: str,
        budget: int,
        days: int
    ):

        if not hotels:
            return {}

        hotel_budget = budget * 0.50
        max_price = hotel_budget / max(days, 1)

        hotel_type = hotel_type.lower().strip()

        hotel_keywords = {

            "5 star": [
                "taj",
                "hyatt",
                "marriott",
                "hilton",
                "radisson",
                "westin",
                "novotel",
                "oberoi",
                "itc",
                "leela",
                "grand",
                "sheraton"
            ],

            "4 star": [
                "fortune",
                "lemontree",
                "ramada",
                "holiday inn",
                "ginger"
            ],

            # Previously missing - hotel_type="3 Star" is a valid
            # option in request_schema.py, but with no matching
            # keywords here it silently fell through to "consider
            # every hotel" instead of respecting the user's choice.
            "3 star": [
                "fern",
                "country inn",
                "ibis",
                "sarovar",
                "regenta"
            ],

            "budget": [
                "inn",
                "guest",
                "guest house",
                "hostel",
                "residency",
                "lodge"
            ],

            "resort": [
                "resort",
                "spa",
                "beach"
            ]

        }

        candidates = hotels

        # -----------------------------
        # Filter by Hotel Type
        # -----------------------------

        if hotel_type != "any":

            keywords = hotel_keywords.get(
                hotel_type,
                []
            )

            filtered = []

            for hotel in hotels:

                name = hotel.get(
                    "name",
                    ""
                ).lower()

                if any(word in name for word in keywords):
                    filtered.append(hotel)

            if filtered:
                candidates = filtered

        # -----------------------------
        # Score Hotels
        # -----------------------------

        for hotel in candidates:

            score = 0

            rating = hotel.get(
                "rating",
                0
            )

            price = hotel.get(
                "price_per_night",
                0
            )

            # Rating

            score += rating * 20

            # Budget

            if price <= max_price:
                score += 40
            else:
                score -= 20

            # Lower price gets bonus

            score += max(
                0,
                20 - price / 500
            )

            hotel["score"] = round(score, 2)

        candidates.sort(

            key=lambda hotel: hotel["score"],

            reverse=True

        )

        return candidates[0]

    # --------------------------------------------------
    # Estimate Extra Costs
    # --------------------------------------------------

    def estimate_extra_costs(
        self,
        travel_style: str,
        days: int
    ):

        travel_style = travel_style.lower()

        if travel_style == "luxury":

            return {

                "food": 2500 * days,

                "local_transport": 1500 * days,

                "activities": 2000 * days

            }

        elif travel_style == "budget":

            return {

                "food": 600 * days,

                "local_transport": 300 * days,

                "activities": 500 * days

            }

        elif travel_style == "family":

            return {

                "food": 1500 * days,

                "local_transport": 800 * days,

                "activities": 1200 * days

            }

        return {

            "food": 1200 * days,

            "local_transport": 600 * days,

            "activities": 900 * days

        }

    # --------------------------------------------------
    # Travel Tips
    # --------------------------------------------------

    def generate_tips(
        self,
        weather: dict,
        travel_style: str
    ):

        tips = []

        condition = weather.get(
            "condition",
            ""
        ).lower()

        temp = weather.get(
            "temperature",
            25
        )

        if "rain" in condition:

            tips.append("Carry an umbrella.")

            tips.append("Wear waterproof footwear.")

        if temp > 35:

            tips.append("Stay hydrated.")

            tips.append("Avoid sightseeing during afternoon.")

        if temp < 10:

            tips.append("Carry warm clothes.")

        if travel_style.lower() == "luxury":

            tips.append(
                "Reserve premium restaurants in advance."
            )

        elif travel_style.lower() == "budget":

            tips.append(
                "Use public transport to save money."
            )

        return tips

    # --------------------------------------------------
    # Final Summary
    # --------------------------------------------------

    def build_summary(
        self,
        transport,
        hotel,
        budget_summary,
        weather,
        travel_style
    ):

        return {

            "trip_type": travel_style,

            "recommended_transport": transport.get(
                "mode"
            ),

            "estimated_transport_cost": transport.get(
                "estimated_price"
            ),

            "hotel": hotel.get(
                "name"
            ),

            "hotel_rating": hotel.get(
                "rating"
            ),

            "estimated_total": budget_summary.get(
                "total_cost"
            ),

            "remaining_budget": budget_summary.get(
                "remaining_budget"
            ),

            "travel_tips": self.generate_tips(
                weather,
                travel_style
            )

        }