"""Main FastAPI application for Mystical Journeys.

This is the core web application that handles:
- Serving the fantasy-themed travel planning interface
- Processing travel requests with multiple AI providers
- Streaming real-time responses from AI oracles (OpenAI, Claude, Ollama)
- Managing concurrent API calls and error handling

The application uses a single-page interface without traditional chat UI,
instead providing a form-based approach for travel itinerary generation.
"""

import asyncio
import json
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import (
    APP_CONFIG,
    BUDGETS,
    DRAGON_TRANSLATIONS,
    INTERESTS,
    REALMS,
    get_booking_farewell_prompt,
    get_travel_itinerary_prompt,
)
from app.models import BookingRequest, TravelRequest
from app.providers import collect_provider_response, get_providers

# Load environment variables from .env file (API keys, configuration)
load_dotenv()

# Configure production-ready logging
# In production, consider using JSON logging and external log aggregation
logging.basicConfig(
    level=logging.WARNING,  # Only warnings and errors in production
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mystical_journeys.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Mystical Journeys", description="AI-Powered Fantasy Travel Planner"
)

# Mount static files (CSS, JS, images) to be served at /static/* URLs
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates for rendering HTML pages
templates = Jinja2Templates(directory="templates")

# Initialize all LLM providers (OpenAI, Claude, Ollama) and check availability
# Each provider checks for required API keys/services during initialization
providers = get_providers()
available_providers = {k: v for k, v in providers.items() if v.available}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page with all configuration data.

    This endpoint renders the single-page fantasy travel interface, including:
    - Fantasy-themed form elements (realms, budgets, interests)
    - Available AI provider information
    - Dragon language translations for the unique UI feature
    - All necessary configuration for the frontend JavaScript

    The template receives all static configuration data to minimize
    additional API calls from the frontend.
    """
    # Prepare provider information with availability status for the frontend
    provider_info = [
        {"key": k, "name": v.name, "available": v.available}
        for k, v in providers.items()
    ]

    # Render the main template with all configuration data
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "config": APP_CONFIG,
            "dragon_translations": DRAGON_TRANSLATIONS,
            "realms": REALMS,
            "budgets": BUDGETS,
            "interests": INTERESTS,
            "providers": provider_info,
        },
    )


@app.post("/generate-comparison")
async def generate_comparison(travel_request: TravelRequest):
    """Generate travel itineraries using multiple AI providers with real-time streaming.

    This is the core endpoint that:
    1. Validates the travel request and available providers
    2. Constructs optimized prompts for fantasy travel planning
    3. Initiates concurrent calls to selected AI providers (OpenAI, Claude, Ollama)
    4. Streams responses in real-time using Server-Sent Events (SSE)
    5. Handles errors gracefully with user-friendly messages

    The streaming approach allows users to see responses as they're generated,
    providing a better UX especially for slower providers.

    Args:
        travel_request: Validated Pydantic model containing destination, duration,
                       budget, interests, and selected providers

    Returns:
        StreamingResponse: SSE stream with JSON-formatted provider responses
    """
    # Convert request data into natural language for prompt generation
    duration_text = f"{travel_request.days} days"
    interests_text = (
        ", ".join(travel_request.interests)
        if travel_request.interests
        else "general adventure"
    )

    # Generate the optimized travel itinerary prompt using our template
    prompt = get_travel_itinerary_prompt(
        travel_request.destination, duration_text, travel_request.budget, interests_text
    )

    # Filter requested providers to only include available ones
    # This prevents errors when users select providers that are offline/misconfigured
    requested_providers = [
        p for p in travel_request.providers if p in providers and providers[p].available
    ]

    # Handle case where no valid providers are available
    if not requested_providers:

        async def error_stream():
            error_msg = json.dumps({"error": "No available providers selected"})
            yield f"data: {error_msg}\n\n"

        return StreamingResponse(
            error_stream(), media_type="text/event-stream"
        )

    async def comparison_stream():
        """Internal streaming generator that manages concurrent AI provider calls.

        This function implements the core streaming logic:
        1. Starts all requested providers concurrently using asyncio tasks
        2. Sends initial metadata to the frontend
        3. Polls for completed tasks and streams results as they finish
        4. Handles individual provider errors without breaking the stream
        5. Sends completion signal when all providers are done
        """
        # Start concurrent provider tasks
        tasks = {}
        for provider_key in requested_providers:
            provider = providers[provider_key]
            tasks[provider_key] = asyncio.create_task(
                collect_provider_response(provider, prompt)
            )

        # Send initial provider list to frontend for UI setup
        provider_data = json.dumps({"providers": requested_providers})
        yield f"data: {provider_data}\n\n"

        # Poll for completed tasks and stream results as they become available
        # This enables real-time display of results from different providers
        completed = set()
        while len(completed) < len(requested_providers):
            for provider_key, task in tasks.items():
                if provider_key not in completed and task.done():
                    try:
                        # Successfully completed provider task
                        result = await task
                        result_data = json.dumps(
                            {"provider": provider_key, "result": result}
                        )
                        yield f"data: {result_data}\n\n"
                    except Exception as e:
                        # Handle individual provider errors gracefully
                        # Other providers can still succeed
                        error_data = json.dumps(
                            {"provider": provider_key, "error": str(e)}
                        )
                        yield f"data: {error_data}\n\n"
                    completed.add(provider_key)

            # Small delay to prevent excessive CPU usage while polling
            await asyncio.sleep(0.1)

        # Signal completion to frontend
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        comparison_stream(), media_type="text/event-stream"
    )


@app.post("/generate-booking-response")
async def generate_booking_response(booking_request: BookingRequest):
    """Generate a whimsical response from the chosen provider about the selected quest"""
    provider_key = booking_request.provider

    if not provider_key or provider_key not in providers:
        # Return a 400 Bad Request error if the provider is invalid
        return JSONResponse(
            status_code=400, content={"error": "Invalid provider selected"}
        )

    provider = providers[provider_key]
    if not provider.available:
        # Return a 503 Service Unavailable if the provider is offline
        return JSONResponse(
            status_code=503, content={"error": "Selected provider is not available"}
        )

    # Create a simpler, more robust farewell prompt that doesn't parse the itinerary
    # This avoids server errors caused by complex HTML in the itinerary body
    farewell_prompt = get_booking_farewell_prompt()

    try:
        # Get response from the chosen provider
        response = await collect_provider_response(provider, farewell_prompt)
        return {"message": response, "provider": provider_key}
    except Exception as e:
        logger.error(
            "Booking response generation failed: provider=%s, error=%s",
            provider_key,
            str(e),
        )
        # Return a 500 Internal Server Error with a clear JSON message
        return JSONResponse(
            status_code=500,
            content={"error": "The oracle seems to have vanished into the mist..."},
        )


@app.get("/providers")
async def get_providers():
    """Get available providers and their status"""
    return {
        "providers": {
            k: {"name": v.name, "available": v.available} for k, v in providers.items()
        },
        "available_count": len(available_providers),
    }
