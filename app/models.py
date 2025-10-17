"""
Pydantic models for Mystical Journeys API
"""

from pydantic import BaseModel


class TravelRequest(BaseModel):
    """Pydantic model for validating travel itinerary generation requests.

    This model defines the structure and validation rules for all travel
    requests sent from the frontend form. FastAPI automatically validates
    incoming JSON against this schema and returns 422 errors for invalid data.

    The model includes sensible defaults and type hints to ensure data integrity
    and provide clear API documentation through FastAPI's auto-generated OpenAPI spec.

    Attributes:
        destination (str): Fantasy realm name (required, from REALMS config)
        days (int): Quest duration in days (default: 5, typically 1-30)
        budget (str): Budget tier ('budget', 'moderate', 'luxury')
        interests (list[str]): Selected adventure interests (from INTERESTS config)
        providers (list[str]): AI providers to compare (default: openai + ollama)

    Example:
        {
            "destination": "Enchanted Forest of Eldara",
            "days": 7,
            "budget": "moderate",
            "interests": ["magical_creatures", "mystical_forests"],
            "providers": ["openai", "claude"]
        }
    """

    destination: str  # Required field, no default
    days: int = 5  # Reasonable default for most travel plans
    budget: str  # Required field for cost calculations
    interests: list[str] = []  # Optional, defaults to general adventure
    providers: list[str] = ["openai", "ollama"]  # Default to fastest providers


class BookingRequest(BaseModel):
    """Pydantic model for validating booking requests.

    This model defines the structure for booking a generated itinerary.
    It ensures that the provider and the full itinerary content are
    sent to the booking endpoint.

    Attributes:
        provider (str): The AI provider that generated the itinerary.
        itinerary (str): The full text of the travel itinerary to be booked.
    """
    provider: str
    itinerary: str
