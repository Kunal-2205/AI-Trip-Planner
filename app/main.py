"""
main.py

This is the entry point of our FastAPI application.
Run it with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.routes.trip_routes import router as trip_router

# Create the FastAPI app. The title/description show up in Swagger docs.
app = FastAPI(
    title="AI Multi-Agent Travel Planner",
    description="A beginner-friendly LangGraph multi-agent project "
    "that plans trips using Gemini.",
    version="1.0.0",
)

# Register our /plan-trip endpoint with the app
app.include_router(trip_router)


@app.get("/")
def read_root():
    """Simple health-check / welcome endpoint."""
    return {"message": "AI Multi-Agent Travel Planner is running. Visit /docs for Swagger UI."}
