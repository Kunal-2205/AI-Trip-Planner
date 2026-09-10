from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")