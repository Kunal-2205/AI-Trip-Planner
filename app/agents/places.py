"""
places.py

Places Agent

Fetches real places from Geoapify.
Uses safe API calls so one invalid category
does not crash the planner.
"""

from app.llm import get_llm, invoke_structured
from app.prompts.prompts import PLACES_PROMPT
from app.schemas.agent_schemas import PlacesOutput
from app.state import TravelState
from app.services.places_service import PlacesService

places_service = PlacesService()


def remove_duplicates(items):

    unique = []
    seen = set()

    for item in items:

        if not item.get("name"):
            continue

        key = item["name"].lower()

        if key not in seen:

            seen.add(key)
            unique.append(item)

    return unique


def safe_get_places(destination: str, category: str):

    """
    Fetch places safely.

    If Geoapify returns an error,
    return an empty list instead of crashing.
    """

    try:

        return places_service.get_places(
            city=destination,
            category=category
        )

    except Exception as e:

        print(f"[WARNING] {category} -> {e}")

        return []


def places_node(state: TravelState) -> TravelState:

    print("=" * 70)
    print("PLACES AGENT")

    destination = state["destination"]

    interests = [i.lower() for i in state["interests"]]

    # ---------------------------------------------------
    # Fetch categories
    # ---------------------------------------------------

    tourist_places = safe_get_places(
        destination,
        "tourism.sights"
    )

    restaurants = safe_get_places(
        destination,
        "catering.restaurant"
    )

    cafes = safe_get_places(
        destination,
        "catering.cafe"
    )

    shopping = safe_get_places(
        destination,
        "commercial.shopping_mall"
    )

    # Geoapify currently has no reliable nightclub category
    clubs = []

    # ---------------------------------------------------
    # Interest specific categories
    # ---------------------------------------------------

    if "beach" in interests:

        tourist_places.extend(

            safe_get_places(
                destination,
                "natural.beach"
            )

        )

    if "history" in interests:

        tourist_places.extend(

            safe_get_places(
                destination,
                "entertainment.museum"
            )

        )

    if "adventure" in interests:

        tourist_places.extend(

            safe_get_places(
                destination,
                "leisure.park"
            )

        )

    # ---------------------------------------------------
    # Remove duplicates
    # ---------------------------------------------------

    tourist_places = remove_duplicates(tourist_places)
    restaurants = remove_duplicates(restaurants)
    cafes = remove_duplicates(cafes)
    shopping = remove_duplicates(shopping)
    clubs = remove_duplicates(clubs)

    print(f"Tourist Places : {len(tourist_places)}")
    print(f"Restaurants    : {len(restaurants)}")
    print(f"Cafes          : {len(cafes)}")
    print(f"Shopping       : {len(shopping)}")
    print(f"Clubs          : {len(clubs)}")

    # ---------------------------------------------------
    # Ask LLM to select best attractions
    # ---------------------------------------------------

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        PlacesOutput
    )

    prompt = PLACES_PROMPT.format(

        destination=destination,

        interests=", ".join(state["interests"]),

        travel_style=state["travel_style"],

        places=tourist_places

    )

    result = invoke_structured(

        structured_llm,

        prompt

    )

    state["places"] = [

        place.model_dump()

        for place in result.places

    ]

    state["restaurants"] = restaurants
    state["cafes"] = cafes
    state["shopping"] = shopping

    state["current_step"] += 1

    print("=" * 70)

    return state