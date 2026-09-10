"""
llm.py

This file creates our Groq chat model, and provides a small helper
to reliably call it for structured output.

Every agent uses these same functions so the model (and its
retry behavior) is configured in exactly one place.
"""

from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY


def get_llm() -> ChatGroq:
    """
    Create and return a Groq chat model.

    We use temperature=0 so the model gives consistent,
    predictable answers (good for structured data).
    """
    return ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0,
        api_key=GROQ_API_KEY,
    )


def invoke_structured(structured_llm, prompt: str, retries: int = 3):
    """
    Call a structured-output LLM and retry if it fails.

    Sometimes the model returns slightly malformed JSON when asked
    for a complex/nested structure (like a multi-day itinerary).
    Retrying almost always fixes it, since the model rarely makes
    the same mistake twice in a row.
    """
    last_error = None

    for attempt in range(retries):
        try:
            return structured_llm.invoke(prompt)
        except Exception as error:
            last_error = error
            print(f"Structured output failed (attempt {attempt + 1}/{retries}): {error}")

    # If every attempt failed, raise the last error so FastAPI
    # still returns a clear 500 error instead of hanging silently.
    raise last_error