from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestFrontendElements:
    """Test suite for frontend elements and functionality"""

    def test_html_structure(self):
        """Test basic HTML structure elements"""
        response = client.get("/")
        html_content = response.text

        # Check for essential HTML elements
        assert "<!DOCTYPE html>" in html_content
        assert '<html lang="en">' in html_content
        assert "<head>" in html_content
        assert "<body" in html_content  # Body tag with CSS classes
        assert "</html>" in html_content

    def test_meta_tags(self):
        """Test presence of important meta tags"""
        response = client.get("/")
        html_content = response.text

        assert 'charset="UTF-8"' in html_content
        assert 'name="viewport"' in html_content
        assert 'content="width=device-width, initial-scale=1.0"' in html_content

    def test_page_title(self):
        """Test page title"""
        response = client.get("/")
        html_content = response.text

        assert (
            "<title>Mystical Journeys - Fantasy Realm Travel Agency</title>"
            in html_content
        )

    def test_external_resources(self):
        """Test loading of external CSS and font resources"""
        response = client.get("/")
        html_content = response.text

        # Check for Tailwind CSS
        assert "tailwindcss" in html_content
        # Check for Font Awesome
        assert "font-awesome" in html_content

    def test_form_structure(self):
        """Test travel form structure"""
        response = client.get("/")
        html_content = response.text

        # Check for form element
        assert '<form id="travelForm"' in html_content

        # Check for all form fields
        assert 'id="destination"' in html_content
        assert 'id="days"' in html_content
        assert 'id="budget"' in html_content
        assert 'name="interests"' in html_content
        assert 'name="providers"' in html_content

        # Check for submit button
        assert 'type="submit"' in html_content

    def test_interest_options(self):
        """Test all interest checkbox options are present"""
        response = client.get("/")
        html_content = response.text

        expected_interests = [
            "magical_creatures",
            "mystical_forests",
            "treasure_hunting",
            "spell_learning",
            "tavern_culture",
            "royal_courts",
            "underwater_realms",
            "sky_adventures",
            "dark_mysteries",
        ]

        for interest in expected_interests:
            assert f'value="{interest}"' in html_content

    def test_days_input_field(self):
        """Test days input field is present"""
        response = client.get("/")
        html_content = response.text

        assert 'type="number"' in html_content
        assert 'id="days"' in html_content
        assert 'value="5"' in html_content  # Default value
        assert 'min="1"' in html_content
        assert 'max="30"' in html_content

    def test_budget_options(self):
        """Test budget select options"""
        response = client.get("/")
        html_content = response.text

        expected_budgets = ["budget", "moderate", "luxury"]

        for budget in expected_budgets:
            assert f'value="{budget}"' in html_content

    def test_provider_selection(self):
        """Test AI oracle provider checkboxes"""
        response = client.get("/")
        html_content = response.text

        # Should have provider selection
        assert 'name="providers"' in html_content
        assert "Choose AI Oracles" in html_content or "providers" in html_content

    def test_results_panel(self):
        """Test results panel structure"""
        response = client.get("/")
        html_content = response.text

        assert 'id="loading"' in html_content
        assert 'id="results"' in html_content
        assert 'id="comparison-container"' in html_content

    def test_fantasy_themed_content(self):
        """Test fantasy-themed content and language"""
        response = client.get("/")
        html_content = response.text

        fantasy_terms = [
            "Mystical Journeys",
            "Embark on",
            "Epic Quests",
            "Let your AI travel oracle",
            "Quest Duration",
            "Treasury Budget",
            "Oracle Comparison",
        ]

        for term in fantasy_terms:
            assert term in html_content

    def test_config_driven_content(self):
        """Test that content is driven by config rather than hardcoded"""
        response = client.get("/")
        html_content = response.text

        # Test that realm options from config are present
        assert "Enchanted Forest of Eldara" in html_content
        assert "Crystal Caverns of Mystara" in html_content

    def test_javascript_integration(self):
        """Test JavaScript file integration"""
        response = client.get("/")
        html_content = response.text

        assert '<script src="/static/app.js"></script>' in html_content

    def test_responsive_design_classes(self):
        """Test presence of responsive design elements"""
        response = client.get("/")
        html_content = response.text

        # Check for Tailwind CSS classes
        assert "tailwindcss" in html_content
        # Check for responsive meta tag
        assert "viewport" in html_content
        # Check for hidden class used in results
        assert "hidden" in html_content
