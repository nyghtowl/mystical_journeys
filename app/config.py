"""
Configuration data for Mystical Journeys application.

This module contains all static configuration data for the fantasy travel application:
- UI text and labels in multiple languages (English + Dragon emoji language)
- Fantasy realm destinations, budget tiers, and adventure interests
- Template functions for generating optimized AI prompts

The configuration is designed to be easily maintainable and extensible.
To add new realms, interests, or budget tiers, simply update the respective
data structures in this file - no code changes required elsewhere.

The Dragon language feature provides a unique UI experience by translating
all text elements to fantasy-themed emoji combinations.
"""

# Application Configuration Data
APP_CONFIG = {
    "title": "Mystical Journeys",
    "tagline": "Gateway to Fantasy Realms",
    "languages": {
        "english": {"code": "en", "name": "English", "flag": "🇺🇸"},
        "dragon": {"code": "dr", "name": "Dragon", "flag": "🐉"},
    },
    "hero": {
        "title": "Embark on Epic Quests",
        "description": (
            "Let your AI travel oracle design the perfect escape to "
            " legendary worlds."
        ),
        "icons": ["🐉", "⚔️", "🏰", "🧙‍♂️", "🗡️"],
    },
    "form": {
        "title": "Describe Your Quest",
        "description": (
            "Tell us about your desired travel adventure "
            "and we'll weave an itinerary of wonder"
        ),
        "fields": {
            "destination": {
                "label": "Choose Your Mystical Realm",
                "placeholder": "Select a realm to explore...",
            },
            "days": {"label": "Quest Duration (Days)"},
            "budget": {
                "label": "Treasury Budget",
                "placeholder": "Select your gold coin budget...",
            },
            "interests": {"label": "Quest Interests (Select All That Apply)"},
            "providers": {"label": "Choose AI Travel Oracles to Compare"},
        },
        "submit_button": "Begin My Quest",
    },
    "loading": {
        "title": "Consulting the Travel Oracle...",
        "description": "The mystical spirits are crafting your perfect adventure",
        "icons": ["✨", "🔮", "⭐"],
    },
    "results": {
        "title": "Oracle Comparison",
        "buttons": {"modify": "Modify My Quest", "new": "Plan New Quest"},
    },
    "provider_status": {"available": "✓ Available", "unavailable": "✗ Unavailable"},
    "footer": {
        "company_name": "Mystical Journeys Ltd.",
        "tagline": "Your Premier Fantasy Travel Agency",
        "copyright": "© 2025 Mystical Journeys Ltd. All rights reserved.",
        "links": {
            "about": "About Us",
            "contact": "Contact",
            "privacy": "Privacy Policy",
            "terms": "Terms of Service",
            "careers": "Careers",
        },
        "social": {
            "twitter": "🐦 Follow Our Quests",
            "instagram": "📸 Adventure Gallery",
            "facebook": "👥 Join Our Guild",
        },
        "contact_info": {
            "email": "adventures@mystical-journeys.com",
            "phone": "+1 (555) QUEST-ME",
            "address": "123 Enchanted Way, Fantasy Realm, FR 12345",
        },
    },
}

# Dragon language translations
DRAGON_TRANSLATIONS = {
    "title": "🐉🔮✨",
    "tagline": "🏰🌟🗡️🧙‍♂️🏰",
    "hero": {"title": "🐉⚔️🏰✨🗡️", "description": "🧙‍♂️🔮🌟🏰🐉⚔️🗡️✨🌙🏆🎭🎪🎨🎯🎲"},
    "form": {
        "title": "📜🗡️🏰🐉",
        "description": "🧙‍♂️📖✨🔮🌟🏰⚔️🗡️",
        "fields": {
            "destination": {"label": "🏰🌟🐉🗡️", "placeholder": "🏰🔮✨..."},
            "days": {"label": "⏰🗡️🐉 (📅)"},
            "budget": {"label": "💰🏆✨", "placeholder": "💰🔮✨?"},
            "interests": {"label": "🗡️⚔️🎯 (🔮✨🌟)"},
            "providers": {"label": "🧙‍♂️🔮🌟⚖️"},
        },
        "submit_button": "🐉🗡️🏰✨",
    },
    "loading": {"title": "🔮🧙‍♂️✨...", "description": "🌟🎭🔮🧙‍♂️⚔️🏰✨"},
    "results": {"title": "🧙‍♂️⚖️🔮", "buttons": {"modify": "🔧🗡️🐉", "new": "🆕🗡️🏰"}},
    "footer": {
        "company_name": "🐉🏰✨ 🏢",
        "tagline": "🏰🌟🗡️🧙‍♂️🔮",
        "copyright": "© 2025 🐉🏰✨ 🏢. 🛡️⚔️🔮.",
        "links": {
            "about": "🧙‍♂️📖",
            "contact": "📞✉️",
            "privacy": "🛡️📜",
            "terms": "📋⚖️",
            "careers": "💼🗡️",
        },
        "social": {"twitter": "🐦🗡️🔮", "instagram": "📸🏰⚔️", "facebook": "👥🛡️🏰"},
        "contact_info": {
            "email": "🧙‍♂️@🐉-🏰.🔮",
            "phone": "+1 (555) 🗡️-🐉",
            "address": "123 🧙‍♂️🌟, 🏰🔮, FR 12345",
        },
    },
}

REALMS = [
    {"value": "Enchanted Forest of Eldara", "label": "🌲 Enchanted Forest of Eldara"},
    {"value": "Crystal Caverns of Mystara", "label": "💎 Crystal Caverns of Mystara"},
    {
        "value": "Floating Islands of Aetheria",
        "label": "☁️ Floating Islands of Aetheria",
    },
    {"value": "Dragon Peaks of Pyronia", "label": "🏔️ Dragon Peaks of Pyronia"},
    {
        "value": "Underwater Kingdom of Aquatillia",
        "label": "🌊 Underwater Kingdom of Aquatillia",
    },
    {"value": "Desert Oasis of Mirajia", "label": "🏜️ Desert Oasis of Mirajia"},
    {"value": "Steampunk City of Gearzonia", "label": "⚙️ Steampunk City of Gearzonia"},
    {"value": "Ice Palace of Frostheim", "label": "❄️ Ice Palace of Frostheim"},
]

# Days input will be handled in the template directly

BUDGETS = [
    {"value": "budget", "label": "💰 Budget Quest (500-1,500 Gold Coins)"},
    {"value": "moderate", "label": "💎 Moderate Adventure (1,500-5,000 Gold Coins)"},
    {"value": "luxury", "label": "👑 Royal Experience (5,000+ Gold Coins)"},
]

INTERESTS = [
    {"value": "magical_creatures", "label": "🐉 Magical Creatures & Beasts"},
    {"value": "mystical_forests", "label": "🌲 Mystical Forests & Nature"},
    {"value": "treasure_hunting", "label": "💎 Treasure Hunting & Artifacts"},
    {"value": "spell_learning", "label": "🔮 Spell Learning & Magic Arts"},
    {"value": "tavern_culture", "label": "🍺 Tavern Culture & Local Cuisine"},
    {"value": "royal_courts", "label": "👑 Royal Courts & Politics"},
    {"value": "underwater_realms", "label": "🌊 Underwater Exploration"},
    {"value": "sky_adventures", "label": "☁️ Sky Cities & Flying Mounts"},
    {"value": "dark_mysteries", "label": "🌙 Dark Mysteries & Secrets"},
]


def get_travel_itinerary_prompt(
    destination: str, duration: str, budget: str, interests: str
) -> str:
    """Generate an optimized travel itinerary prompt for AI providers.

    This function creates a carefully crafted prompt that has been optimized
    through testing to produce high-quality, consistent travel itineraries
    across different AI models (OpenAI, Claude, Ollama).

    Key prompt engineering techniques used:
    - Clear role definition (fantasy travel agent)
    - Specific output format requirements
    - Budget constraints with realistic ranges
    - Enthusiasm and engagement directives
    - Structured day-by-day format specification

    Args:
        destination: Fantasy realm name from user selection
        duration: Trip length in natural language (e.g., "5 days")
        budget: Budget tier (budget/moderate/luxury)
        interests: Comma-separated adventure interests

    Returns:
        str: Complete optimized prompt ready for AI provider
    """
    # The "--- ONLY RESULTS ---" directive helps some providers (especially Ollama)
    # focus on generating content rather than meta-commentary
    return f"""--- ONLY RESULTS ---
    
You are an expert fantasy travel agent at Mystical Journeys Ltd.,
the premier magical realm travel agency. You specialize in creating
unforgettable adventures that perfectly match each traveler's interests
and budget. Do not add any commentary or explanation.


A client has requested a {duration} adventure to {destination} with a
{budget} budget, focusing on {interests}.

Create an irresistible day-by-day itinerary that will make them want to
book immediately. Write as an enthusiastic travel professional who knows
all the secret spots and exclusive experiences.

**Instructions:** 
*   Do not add any intro text.
*   Do not include explanation on how you are developing the results.
*   Match interests explicitly to activities and experiences throughout.
*   Make each day unique with different themes (e.g., Day 1: Arrival & Ruins, Day 2: Underworld Exploration).
*   Ensure cost fits the {budget} category range.

Format your response as (to be followed precisely):

**Day 1: [Exciting Theme Name]**
• Morning: [Specific magical activity in {destination}]
• Afternoon: [Adventure that matches their {interests}]
• Evening: [Memorable experience with local culture]
• Accommodation: [Unique lodging with character]

**Day 2: [Another Exciting Theme]**
• Morning: [Different amazing activity]
• Afternoon: [Something they can't do anywhere else]
• Evening: [Perfect way to end the day]
• Accommodation: [Another special place to stay]

[Continue for each day of {duration}]

**Total Estimated Cost:** [Amount within the {budget} range - Budget Quest:
500-1,500 gold coins, Moderate Adventure: 1,500-5,000 gold coins,
Royal Experience: 5,000+ gold coins]

IMPORTANT: The total cost MUST fall within the selected {budget} category
range. Choose a realistic amount that fits their budget tier and duration.

Make each activity sound thrilling and exclusive. Focus on why this
specific combination of {destination} and {interests} creates once-in-a-
lifetime experiences. Write like you're personally excited to send them
on this adventure."""


def get_booking_farewell_prompt() -> str:
    """Generate a whimsical farewell prompt for the chosen AI oracle.

    This function creates a prompt asking the winning AI provider to give
    a final whimsical send-off to the traveler who chose their itinerary.
    The response should be brief, magical, and on-theme.

    Returns:
        str: Optimized prompt for generating whimsical oracle farewell
    """
    return """--- ONLY RESULTS ---
    
    The traveler has chosen your itinerary for their quest! 

As their chosen AI travel oracle, give them a brief (2-3 sentences) whimsical farewell message. Do not add any commentary or explanation.

**Instructions:** 
*   Do not add any intro text.
*   Do not include explanation on how you are developing the results.

Your response can either:
- Offer mystical well-wishes for their journey
- Playfully warn them of magical dangers you didn't mention in the itinerary
- Share a final piece of enchanted travel wisdom
- Express excitement about their chosen adventure

Keep it fantasy-themed, magical, and delightfully mysterious. End with a magical blessing or warning!"""
