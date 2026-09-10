import requests

from app.config import OPENWEATHER_API_KEY


class WeatherService:

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str):

        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["main"],
                "wind_speed": data["wind"]["speed"]
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return {
                "city": city,
                "temperature": "N/A",
                "feels_like": "N/A",
                "humidity": "N/A",
                "condition": "Unknown",
                "wind_speed": "N/A"
            }