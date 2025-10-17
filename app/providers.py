"""LLM Provider implementations for Mystical Journeys"""

import asyncio
import json
import logging
import os
from datetime import datetime

import anthropic
import requests
from openai import (
    APIError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)

logger = logging.getLogger(__name__)


def parse_quest_parameters(prompt: str) -> dict:
    """Extract quest parameters from a fantasy prompt"""
    lines = prompt.split("\n")
    params = {"destination": "", "duration": "", "budget": "", "interests": ""}

    for line in lines:
        if "Mystical Realm:" in line:
            params["destination"] = line.split("Mystical Realm:")[-1].strip()
        elif "Quest Duration:" in line:
            params["duration"] = line.split("Quest Duration:")[-1].strip()
        elif "Treasury Level:" in line:
            params["budget"] = line.split("Treasury Level:")[-1].strip()
        elif "Adventuring Interests:" in line:
            params["interests"] = line.split("Adventuring Interests:")[-1].strip()

    return params


def clean_response_start(text: str) -> str:
    """Filter out AI conversational fluff while preserving valuable itinerary content.

    This function addresses a common issue with AI responses where models start
    with meta-commentary like "I'll create..." or "Here's a fantasy itinerary..."
    instead of jumping straight to the travel content users want to see.

    The filtering is conservative - it only removes obvious conversational starters
    while preserving any content that might be part of the actual itinerary.

    Args:
        text: Raw text chunk from AI provider response

    Returns:
        str: Filtered text (empty string if it's conversational fluff)

    Note:
        Currently commented out in provider implementations for testing,
        but can be re-enabled if conversational responses become problematic.
    """
    text_lower = text.lower().strip()

    # Common AI conversational starters that add no value to travel itineraries
    # These patterns indicate meta-commentary rather than actual travel content
    skip_starters = [
        "here's an irresistible",
        "i'll create",
        "let me create",
        "i'd be happy",
        "certainly!",
        "of course!",
        "great choice!",
        "here's a fantasy",
        "here's your",
        "let me craft",
        "okay, the user wants",
        "the user wants me",
        "i need to create",
        "i'm going to",
        "since this is",
        "i want to make",
    ]

    # Skip if it starts with conversational fluff
    for starter in skip_starters:
        if text_lower.startswith(starter):
            return ""

    # Always keep content that looks like itinerary structure
    itinerary_indicators = [
        "day 1",
        "day 2",
        "day 3",
        "day 4",
        "day 5",
        "day 6",
        "day 7",
        "**day",
        "morning:",
        "afternoon:",
        "evening:",
        "night:",
        "accommodation:",
        "cost:",
        "total estimated",
        "•",
        "*",
        "breakfast",
        "lunch",
        "dinner",
    ]

    # Keep structured itinerary content
    if any(indicator in text_lower for indicator in itinerary_indicators):
        return text

    # Keep content that mentions fantasy locations or activities
    fantasy_content = [
        "enchanted",
        "mystical",
        "magical",
        "dragon",
        "castle",
        "tavern",
        "forest",
        "crystal",
        "floating",
        "underwater",
        "treasure",
        "spell",
        "potion",
        "wizard",
        "fairy",
        "quest",
        "adventure",
        "gold coins",
        "artifacts",
        "creature",
        "beast",
    ]

    if any(keyword in text_lower for keyword in fantasy_content):
        return text

    # Keep short sentences that aren't obviously meta-commentary
    meta_phrases = ["i'll", "let me", "here's", "this will", "we'll"]
    if len(text.split()) < 15 and not any(meta in text_lower for meta in meta_phrases):
        return text

    # Default: skip meta-commentary
    return ""


def get_optimized_prompt(prompt: str) -> str:
    """Convert any prompt format to our standardized travel itinerary template.

    This function ensures all AI providers receive the same high-quality,
    optimized prompt regardless of the original format. It:

    1. Parses fantasy travel parameters from the input prompt
    2. Converts them to our proven travel itinerary template
    3. Falls back to original prompt if parsing fails

    The standardized prompt has been optimized through testing to produce
    better, more consistent travel itineraries across all AI providers.
    This is especially important for Ollama which may need more structured
    prompts to produce quality output.

    Args:
        prompt: Original prompt in any format

    Returns:
        str: Optimized travel itinerary prompt or original if parsing fails
    """
    # Import here to avoid circular imports with config module
    from .config import get_travel_itinerary_prompt

    # Extract structured parameters from the fantasy-themed prompt
    params = parse_quest_parameters(prompt)

    # Ensure we have minimum required information for optimization
    if not all([params["destination"], params["duration"]]):
        return prompt  # Fallback to original if parsing fails

    # Use our battle-tested travel itinerary template for consistency
    # This template has been optimized for quality across all AI providers
    return get_travel_itinerary_prompt(
        params["destination"], params["duration"], params["budget"], params["interests"]
    )


class LLMProvider:
    """Base class for all AI provider implementations.

    This abstract base class defines the common interface for all LLM providers
    (OpenAI, Claude, Ollama). Each provider must implement:

    - Availability checking during initialization (API keys, service status)
    - Streaming response generation with proper error handling
    - Consistent response format for the frontend

    The provider architecture allows easy addition of new AI services
    while maintaining a consistent interface for the main application.

    Attributes:
        name (str): Display name for the provider (shown in UI)
        available (bool): Whether the provider is properly configured and accessible
    """

    def __init__(self, name: str):
        """Initialize provider with display name and default availability.

        Args:
            name: Human-readable name displayed in the UI
        """
        self.name = name
        self.available = False  # Set to True by subclasses if properly configured

    async def generate_stream(self, prompt: str):
        """Generate streaming response for the given prompt.

        This method must be implemented by all provider subclasses.
        Should yield dictionaries with 'content', 'error', or 'done' keys
        to maintain consistent interface with the frontend.

        Args:
            prompt: The travel itinerary prompt to process

        Yields:
            dict: Streaming response chunks with consistent format
        """
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 provider with streaming support"""

    def __init__(self):
        super().__init__("OpenAI GPT-3.5 Turbo")
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            try:
                self.client = OpenAI(api_key=api_key)
                self.available = True
            except Exception:
                self.client = None

    async def generate_stream(self, prompt: str):
        # Mock response if no API key is provided
        if not os.getenv("OPENAI_API_KEY"):
            yield {"content": "🧠 (Mocked) AI response for testing."}
            yield {"done": True}
            return

        if not self.available:
            # Log configuration issues for monitoring
            logger.warning("OpenAI provider unavailable: API key not configured")
            user_msg = (
                "🔑 OpenAI is not configured. " "Please add your API key to continue."
            )
            yield {"error": user_msg}
            yield {"done": True}
            return

        try:
            # Track request start time for timeout handling
            start_time = datetime.now()
            # Reset response tracking for this new request
            self._response_started = False

            # Use our optimized travel-focused prompt template
            # This ensures consistent, high-quality responses
            optimized_prompt = get_optimized_prompt(prompt)

            # Create the stream with timeout handling
            stream = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": optimized_prompt}],
                stream=True,
                max_tokens=2000,
                temperature=0.8,
            )

            # Track whether we receive any actual content (not just metadata)
            content_received = False
            for chunk in stream:
                # Implement client-side timeout protection (3 minutes)
                # This prevents hanging requests that could tie up resources
                if (datetime.now() - start_time).seconds > 180:
                    logger.error("OpenAI request timeout: exceeded 180 seconds")
                    timeout_msg = (
                        "⏰ The AI oracle is taking too long to respond. "
                        "Please try again with a shorter request."
                    )
                    yield {"error": timeout_msg}
                    yield {"done": True}
                    return

                # Process actual content chunks from the streaming response
                if chunk.choices[0].delta.content is not None:
                    content_received = True
                    content_chunk = chunk.choices[0].delta.content

                    # Content filtering is currently disabled for testing
                    # Can be re-enabled if AI responses include too much meta-commentary
                    # if not hasattr(self, '_response_started'):
                    #     content_chunk = clean_response_start(content_chunk)
                    #     self._response_started = True

                    # Stream content chunk to frontend immediately
                    yield {"content": content_chunk}
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.01)

            if content_received:
                # Request completed successfully - no logging needed
                yield {"done": True}
            else:
                logger.warning("OpenAI provider returned empty response")
                empty_msg = (
                    "🤔 The AI oracle returned an empty response. "
                    "Please try rephrasing your request."
                )
                yield {"error": empty_msg}

        except AuthenticationError as e:
            logger.error("OpenAI authentication failed: %s", str(e))
            error_msg = (
                "🔐 Invalid OpenAI API key. "
                "Please check your credentials in the .env file."
            )
            yield {"error": error_msg}
            yield {"done": True}
        except RateLimitError as e:
            logger.error("OpenAI rate limit exceeded: %s", str(e))
            error_msg = (
                "🚦 Too many requests to OpenAI right now! "
                "Try waiting a moment, or switch to Ollama or Claude for "
                "instant results. ✨ All our AI oracles craft equally "
                "magical adventures!"
            )
            yield {"error": error_msg}
            yield {"done": True}
        except APITimeoutError as e:
            logger.error("OpenAI request timeout: %s", str(e))
            error_msg = "⏰ OpenAI request timed out. Please try again."
            yield {"error": error_msg}
            yield {"done": True}
        except NotFoundError as e:
            logger.error("OpenAI model not found: %s", str(e))
            error_msg = (
                "🤖 The AI model is currently unavailable. " "Please try again later."
            )
            yield {"error": error_msg}
            yield {"done": True}
        except APIError as e:
            # Handle quota and other API errors
            if "insufficient_quota" in str(e) or "quota" in str(e).lower():
                error_msg = (
                    "💳 OpenAI account has reached its usage limit. "
                    "Please check your billing settings or try another "
                    "provider."
                )
            else:
                error_msg = (
                    "❌ OpenAI API encountered an issue. "
                    "Please try again or use another AI oracle."
                )
            logger.error("OpenAI API error: %s", str(e))
            yield {"error": error_msg}
            yield {"done": True}
        except Exception as e:
            logger.error("OpenAI unexpected error: %s", str(e))
            error_msg = (
                "❌ The AI oracle encountered an unexpected issue. "
                "Please try again or contact support if the problem persists."
            )
            yield {"error": error_msg}
            yield {"done": True}


class OllamaProvider(LLMProvider):
    """Ollama local AI provider with streaming support"""

    def __init__(self):
        super().__init__("Ollama DeepSeek-R1")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.available = True
        except Exception:
            self.available = False

    async def generate_stream(self, prompt: str):
        if not self.available:
            user_msg = (
                "🏠 Ollama is not running locally. "
                "Start it with 'ollama serve' to enable local AI."
            )
            logger.warning("Ollama provider unavailable: service not running")
            yield {"error": user_msg}
            return

        try:
            logger.info(f"Starting Ollama generation with model {self.model}")
            start_time = datetime.now()
            # Reset response tracking
            self._response_started = False

            # Use optimized travel-focused prompt
            optimized_prompt = get_optimized_prompt(prompt)

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": optimized_prompt,
                    "stream": True,
                },
                stream=True,
                timeout=180,  # 3-minute timeout
            )

            if response.status_code != 200:
                if response.status_code == 404:
                    error_msg = (
                        "🤖 The local AI model is not available. "
                        "Please make sure the model is installed and Ollama "
                        "is running."
                    )
                else:
                    error_msg = (
                        "🚫 Local AI service is experiencing issues. "
                        "Please restart Ollama and try again."
                    )
                logger.error(
                    "Ollama HTTP error: status=%d, response=%s",
                    response.status_code,
                    response.text[:100],  # Truncate response for logging
                )
                yield {"error": error_msg}
                return

            content_received = False
            full_response = ""
            for line in response.iter_lines():
                # Check for timeout
                if (datetime.now() - start_time).seconds > 180:
                    logger.error("Ollama request timeout: exceeded 180 seconds")
                    timeout_msg = (
                        "⏰ Local AI is taking too long to respond. "
                        "Try a shorter request or restart Ollama."
                    )
                    yield {"error": timeout_msg}
                    yield {"done": True}
                    return

                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data and data["response"]:
                            content_received = True
                            response_chunk = data["response"]
                            full_response += response_chunk

                            # Filtering commented out for testing
                            # if not hasattr(self, '_response_started'):
                            #     response_chunk = clean_response_start(
                            #         response_chunk)
                            #     self._response_started = True
                            yield {"content": response_chunk}
                            await asyncio.sleep(0.01)
                        if data.get("done", False):
                            if content_received:
                                # Request completed successfully - no logging needed
                                yield {"done": True}
                            else:
                                logger.warning("Ollama provider returned no content")
                                empty_msg = (
                                    "🤔 Local AI completed but returned "
                                    "no content. Try rephrasing your request."
                                )
                                yield {"error": empty_msg}
                            break
                    except json.JSONDecodeError:
                        # Skip malformed JSON lines silently - common with streaming
                        continue

        except requests.exceptions.Timeout as e:
            logger.error("Ollama request timeout: %s", str(e))
            error_msg = (
                "⏰ Local AI is taking too long to respond. "
                "Try a shorter request or restart the local AI service."
            )
            yield {"error": error_msg}
            yield {"done": True}
        except requests.exceptions.ConnectionError as e:
            logger.error("Ollama connection error: %s", str(e))
            error_msg = (
                "🔌 Cannot connect to local AI service. "
                "Please make sure Ollama is running."
            )
            yield {"error": error_msg}
            yield {"done": True}
        except Exception as e:
            logger.error("Ollama unexpected error: %s", str(e))
            error_msg = (
                "❌ Local AI encountered an unexpected issue. "
                "Please try restarting the service or contact support."
            )
            yield {"error": error_msg}
            yield {"done": True}


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider with streaming support"""

    def __init__(self):
        super().__init__("Claude 3.5 Sonnet")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and api_key != "your_anthropic_api_key_here":
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.available = True
            except Exception:
                self.client = None

    async def generate_stream(self, prompt: str):
        if not self.available:
            user_msg = (
                "🔑 Claude is not configured. Please add your Anthropic "
                "API key to enable Claude comparison."
            )
            logger.warning("Claude provider not available - API key not configured")
            yield {"error": user_msg}
            return

        try:
            logger.info("Starting Claude generation")
            start_time = datetime.now()
            # Reset response tracking
            self._response_started = False

            # Use optimized travel-focused prompt
            optimized_prompt = get_optimized_prompt(prompt)

            # Wrap in asyncio.wait_for for timeout
            try:
                stream = await asyncio.wait_for(
                    self.client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": optimized_prompt}],
                        stream=True,
                    ),
                    timeout=180,  # 3-minute timeout
                )
            except asyncio.TimeoutError:
                logger.error("Claude request timeout: exceeded 180 seconds")
                timeout_msg = (
                    "⏰ Claude is taking too long to respond. "
                    "Please try again with a shorter request."
                )
                yield {"error": timeout_msg}
                yield {"done": True}
                return

            content_received = False
            async for chunk in stream:
                # Check for timeout during streaming
                if (datetime.now() - start_time).seconds > 180:
                    logger.error("Claude streaming timeout: exceeded 180 seconds")
                    timeout_msg = "⏰ Claude response timed out. Please try again."
                    yield {"error": timeout_msg}
                    return

                if chunk.type == "content_block_delta":
                    if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                        if chunk.delta.text:
                            content_received = True
                            content_chunk = chunk.delta.text
                            # Filtering commented out for testing
                            # if not hasattr(self, '_response_started'):
                            #     content_chunk = clean_response_start(
                            #         content_chunk)
                            #     self._response_started = True
                            yield {"content": content_chunk}
                            await asyncio.sleep(0.01)
                elif chunk.type == "message_stop":
                    if content_received:
                        # Request completed successfully - no logging needed
                        yield {"done": True}
                    else:
                        logger.warning("Claude provider returned no content")
                        empty_msg = (
                            "🤔 Claude completed but returned no content. "
                            "Try rephrasing your request."
                        )
                        yield {"error": empty_msg}

        except anthropic.AuthenticationError as e:
            logger.error("Claude authentication failed: %s", str(e))
            error_msg = (
                "🔐 Invalid Claude API key. "
                "Please check your Anthropic credentials in the .env file."
            )
            yield {"error": error_msg}
            yield {"done": True}
        except anthropic.RateLimitError as e:
            logger.error("Claude rate limit exceeded: %s", str(e))
            error_msg = (
                "🚦 Too many requests to Claude. " "Please wait a moment and try again."
            )
            yield {"error": error_msg}
            yield {"done": True}
        except Exception as e:
            logger.error("Claude unexpected error: %s", str(e))
            error_msg = (
                "❌ Claude AI encountered an unexpected issue. "
                "Please try again or contact support if the problem persists."
            )
            yield {"error": error_msg}
            yield {"done": True}


# Initialize providers
def get_providers():
    """Initialize and return all available providers"""
    return {
        "openai": OpenAIProvider(),
        "ollama": OllamaProvider(),
        "claude": ClaudeProvider(),
    }


async def collect_provider_response(provider: LLMProvider, prompt: str) -> str:
    """Collect complete response from a provider"""
    content_parts = []
    async for chunk in provider.generate_stream(prompt):
        if "content" in chunk:
            content_parts.append(chunk["content"])
        elif "error" in chunk:
            return f"Error: {chunk['error']}"
        elif chunk.get("done"):
            break

    return "".join(content_parts)
