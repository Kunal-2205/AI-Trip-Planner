from app.services.weather_service import WeatherService
from app.state import TravelState

weather_service = WeatherService()


def weather_node(state: TravelState) -> TravelState:
    """
    Fetch live weather from OpenWeather API.
    """

    weather = weather_service.get_weather(
        state["destination"]
    )

    state["weather"] = weather
    state["current_step"] += 1

    return state