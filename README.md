# AI Trip Planner

AI Trip Planner is a multi-agent travel-planning application that turns trip preferences into a personalised itinerary. Its FastAPI backend orchestrates specialised LangGraph agents for transport, hotels, weather, places, budgets, and day-by-day itinerary creation. A Streamlit frontend provides the **Wayfarer** planning experience.

## Features

- Creates trip plans from origin, destination, dates, budget, travellers, interests, food preference, and travel style.
- Coordinates dedicated agents for transport, accommodation, weather, local places, budgeting, and itinerary generation.
- Uses Groq-hosted LLMs for structured planning output.
- Uses Geoapify for places, hotels, and transport data, and OpenWeather for weather data.
- Exposes a documented REST API through FastAPI and an interactive Streamlit UI.

## Architecture

```text
Streamlit UI → FastAPI /plan-trip → LangGraph workflow
                                      ├─ Transport agent
                                      ├─ Hotel agent
                                      ├─ Weather agent
                                      ├─ Places agent
                                      ├─ Budget agent
                                      └─ Itinerary agent
```

The planner agent prepares the work plan, while the router agent sends execution through each specialised agent before returning the final structured trip response.

## Prerequisites

- Python 3.10 or newer
- A [Groq API key](https://console.groq.com/keys)
- A [Geoapify API key](https://myprojects.geoapify.com/)
- An [OpenWeather API key](https://openweathermap.org/api)

## Setup

1. Clone the repository and open it:

   ```bash
   git clone https://github.com/Kunal-2205/AI-Trip-Planner.git
   cd AI-Trip-Planner
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   # macOS / Linux
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt streamlit requests
   ```

4. Create a `.env` file in the project root:

   ```env
   GROQ_API_KEY=your_groq_api_key
   GEOAPIFY_API_KEY=your_geoapify_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

   `.env` is deliberately ignored by Git—never commit API keys.

## Run the application

Start the API server in one terminal:

```bash
uvicorn app.main:app --reload
```

Then start the frontend in another terminal:

```bash
streamlit run streamlit_app.py
```

Open the Streamlit URL shown in the terminal (normally `http://localhost:8501`). The FastAPI docs are available at `http://localhost:8000/docs`.

To point the UI at a backend hosted elsewhere, set `TRAVEL_PLANNER_API_URL` before launching Streamlit:

```powershell
$env:TRAVEL_PLANNER_API_URL="https://your-api.example.com"
streamlit run streamlit_app.py
```

## API usage

`POST /plan-trip` accepts a trip request and returns transport, hotel, weather, places, budget, and itinerary recommendations.

```bash
curl -X POST "http://localhost:8000/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "Mumbai",
    "destination": "Chennai",
    "start_date": "2026-10-15",
    "days": 5,
    "budget": 25000,
    "travellers": 2,
    "travel_style": "Budget",
    "preferred_transport": "Flight",
    "hotel_type": "Budget",
    "food_preference": "Vegetarian",
    "interests": ["Beach", "History", "Shopping"],
    "user_request": "Plan a relaxed five-day trip with local food."
  }'
```

## Project structure

```text
app/
├── agents/       # Specialised LangGraph nodes
├── routes/       # FastAPI endpoints
├── schemas/      # Request and response models
├── services/     # Geoapify and OpenWeather integrations
├── graph.py      # Workflow definition
└── main.py       # FastAPI application
streamlit_app.py  # Wayfarer frontend
```

## Testing

The repository includes small scripts for checking individual planner components:

```bash
python test.py
python test_hotel.py
python test_route.py
python test_transport.py
```

## License

No license has been specified yet. Add one before distributing or reusing the project publicly.
