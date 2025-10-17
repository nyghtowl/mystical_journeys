import pytest
from pydantic import ValidationError

from app.models import TravelRequest


class TestTravelRequestModel:
    """Test suite for TravelRequest Pydantic model"""

    def test_valid_travel_request(self):
        """Test creation of valid TravelRequest"""
        request = TravelRequest(
            destination="Enchanted Forest of Eldara",
            days=7,
            budget="moderate",
            interests=["magical_creatures", "mystical_forests"],
            providers=["openai", "ollama"],
        )

        assert request.destination == "Enchanted Forest of Eldara"
        assert request.days == 7
        assert request.budget == "moderate"
        assert request.interests == ["magical_creatures", "mystical_forests"]
        assert request.providers == ["openai", "ollama"]

    def test_missing_destination(self):
        """Test validation error for missing destination"""
        with pytest.raises(ValidationError) as exc_info:
            TravelRequest(days=7, budget="moderate", interests=["magical_creatures"])

        assert "destination" in str(exc_info.value)

    def test_invalid_days_type(self):
        """Test validation error for invalid days type"""
        with pytest.raises(ValidationError):
            TravelRequest(
                destination="Crystal Caverns of Mystara",
                days="seven",  # Should be int
                budget="luxury",
                interests=["treasure_hunting"],
            )

    def test_empty_interests_list(self):
        """Test that empty interests list is valid"""
        request = TravelRequest(
            destination="Dragon Peaks of Pyronia",
            days=10,
            budget="budget",
            interests=[],  # Empty list should be allowed
        )

        assert request.interests == []

    def test_multiple_interests(self):
        """Test multiple interests in the list"""
        interests = [
            "magical_creatures",
            "ancient_ruins",
            "spell_learning",
            "treasure_hunting",
            "royal_courts",
            "dark_mysteries",
        ]
        request = TravelRequest(
            destination="Floating Islands of Aetheria",
            days=14,
            budget="luxury",
            interests=interests,
        )

        assert len(request.interests) == 6
        assert all(interest in request.interests for interest in interests)

    def test_all_budget_options(self):
        """Test all valid budget options"""
        budget_options = ["budget", "moderate", "luxury"]

        for budget in budget_options:
            request = TravelRequest(
                destination="Underwater Kingdom of Aquatillia",
                days=5,
                budget=budget,
                interests=["underwater_realms"],
            )
            assert request.budget == budget

    def test_default_providers(self):
        """Test default providers are set"""
        request = TravelRequest(
            destination="Desert Oasis of Mirajia", budget="moderate"
        )
        assert request.providers == ["openai", "ollama"]
        assert request.days == 5  # Default days
        assert request.interests == []  # Default empty interests

    def test_custom_providers(self):
        """Test custom providers list"""
        providers = ["openai", "claude", "ollama"]
        request = TravelRequest(
            destination="Ice Palace of Frostheim",
            days=7,
            budget="luxury",
            interests=["sky_adventures"],
            providers=providers,
        )
        assert request.providers == providers
