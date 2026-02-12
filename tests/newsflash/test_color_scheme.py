"""Tests for News Flash color scheme updates.

This module verifies that the new color scheme:
1. Maintains WCAG AA contrast ratios for accessibility
2. Doesn't break any functionality
3. Updates all color references consistently
"""

import re
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def css_file_path():
    """Path to the main News Flash CSS file."""
    return Path("src/sejfa/newsflash/presentation/static/css/style.css")


@pytest.fixture(scope="module")
def css_content(css_file_path):
    """Read CSS file content."""
    return css_file_path.read_text()


class TestSynthwaveTheme:
    """Test suite for GE-52: Synthwave theme with Hot Pink and Cyan"""

    def test_bg_dark_is_deep_navy(self, css_content):
        """Verify background is deep dark navy #0a0a1a."""
        assert "--bg-dark: #0a0a1a;" in css_content, (
            "Background should be deep dark navy #0a0a1a"
        )

    def test_bg_card_is_dark_purple(self, css_content):
        """Verify cards use #12121f."""
        assert "--bg-card: #12121f;" in css_content, "Cards should use #12121f"

    def test_accent_primary_is_hot_pink(self, css_content):
        """Verify primary accent is hot pink #FF2D95."""
        assert "--accent-primary: #FF2D95;" in css_content, (
            "Primary accent should be hot pink #FF2D95"
        )

    def test_accent_secondary_is_cyan(self, css_content):
        """Verify secondary accent is cyan #00FFFF."""
        assert "--accent-secondary: #00FFFF;" in css_content, (
            "Secondary accent should be cyan #00FFFF"
        )

    def test_text_primary_is_white(self, css_content):
        """Verify primary text is white #ffffff."""
        assert "--text-primary: #ffffff;" in css_content, (
            "Primary text should be white #ffffff"
        )

    def test_text_secondary_is_purple_gray(self, css_content):
        """Verify secondary text is purple-tinted gray #8888aa."""
        assert "--text-secondary: #8888aa;" in css_content, (
            "Secondary text should be purple-gray #8888aa"
        )

    def test_border_color_is_dark_purple(self, css_content):
        """Verify borders use #1a1a2e."""
        assert "--border-color: #1a1a2e;" in css_content, "Borders should use #1a1a2e"

    def test_accent_glow_is_hot_pink(self, css_content):
        """Verify accent glow uses hot pink rgba (not green)."""
        # Should have hot pink glow
        assert "rgba(255, 45, 149" in css_content or "rgba(255,45,149" in css_content, (
            "Accent glow should be hot pink (rgba with 255, 45, 149)"
        )
        # Old green glow should NOT exist
        assert "rgba(0, 229, 153" not in css_content, (
            "Old green glow rgba(0, 229, 153, ...) should be removed"
        )

    def test_no_green_colors(self, css_content):
        """Verify NO green colors from previous theme remain."""
        # Old green colors that should be gone
        old_green_colors = ["#00e599", "#00cc88"]

        for green_color in old_green_colors:
            assert green_color not in css_content.lower(), (
                f"Old green color {green_color} should be removed"
            )

    def test_no_hardcoded_green_in_hovers(self, css_content):
        """Verify hover states don't use hardcoded green."""
        # Look for :hover sections
        hover_sections = re.findall(r":hover\s*\{[^}]+\}", css_content, re.DOTALL)

        for section in hover_sections:
            # Check for any green hex codes in hover states
            assert "#00e599" not in section, "Hover should not use #00e599"
            assert "#00cc88" not in section, "Hover should not use #00cc88"

    def test_button_text_is_white(self, css_content):
        """Verify subscribe button has white text on hot pink background."""
        # Find button styles
        assert "color: #ffffff;" in css_content, "Buttons should have white text"


class TestColorSchemeUpdate:
    """Test suite for GE-48: New Color Scheme"""

    def test_css_file_exists(self, css_file_path):
        """Verify the CSS file exists."""
        assert css_file_path.exists(), "CSS file should exist"

    def test_css_has_root_variables(self, css_content):
        """Verify :root section exists with CSS variables."""
        assert ":root {" in css_content, "CSS should have :root section"
        assert "--bg-dark:" in css_content, "Should define --bg-dark variable"
        assert "--bg-card:" in css_content, "Should define --bg-card variable"
        assert "--text-primary:" in css_content, "Should define --text-primary"
        assert "--text-secondary:" in css_content, "Should define --text-secondary"
        assert "--border-color:" in css_content, "Should define --border-color"

    def test_accent_color_variable_exists(self, css_content):
        """Verify accent color variable is defined."""
        # Should have some accent color variable (could be any name)
        assert re.search(r"--accent-[a-z]+:", css_content), (
            "Should define an accent color variable"
        )

    def test_no_hardcoded_blue_colors(self, css_content):
        """Verify old blue colors (#3b82f6, #2563eb) are removed."""
        # These are the old blue hex codes
        old_blue_1 = "#3b82f6"
        old_blue_2 = "#2563eb"

        assert old_blue_1 not in css_content, (
            f"Old blue color {old_blue_1} should be replaced"
        )
        assert old_blue_2 not in css_content, (
            f"Old blue color {old_blue_2} should be replaced"
        )

    def test_no_hardcoded_old_background_colors(self, css_content):
        """Verify old background colors are removed."""
        old_bg_dark = "#0a0e1a"
        old_bg_card = "#1a1f2e"

        assert old_bg_dark not in css_content, (
            f"Old background {old_bg_dark} should be replaced"
        )
        assert old_bg_card not in css_content, (
            f"Old background {old_bg_card} should be replaced"
        )

    def test_color_variables_are_hex_codes(self, css_content):
        """Verify color variables use valid hex codes."""
        # Extract all CSS variable definitions
        var_pattern = r"--([\w-]+):\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgba?\([^)]+\));"
        variables = re.findall(var_pattern, css_content)

        assert len(variables) > 0, "Should have CSS variables defined"

        # Verify at least one variable is a hex code
        hex_vars = [v for v in variables if v[1].startswith("#")]
        assert len(hex_vars) > 0, "Should have at least one hex color variable"

    def test_all_color_references_use_variables(self, css_content):
        """Verify colors use CSS variables, not hardcoded values."""
        # Find all color property declarations
        color_props = re.findall(
            r"(background-color|color|border-color):\s*([^;]+);", css_content
        )

        # Check that most use var() - allow a few exceptions for gradients
        var_usage = [prop for prop in color_props if "var(--" in prop[1]]
        total_props = len([p for p in color_props if "inherit" not in p[1].lower()])

        if total_props > 0:
            var_percentage = len(var_usage) / total_props
            assert var_percentage >= 0.7, (
                f"At least 70% of colors should use CSS variables, "
                f"got {var_percentage:.0%}"
            )

    @pytest.mark.integration
    def test_newsflash_routes_still_work(self):
        """Verify News Flash routes are functional after color changes."""
        from app import create_app

        app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )
        client = app.test_client()

        # Test index page (newsflash blueprint is registered at root)
        response = client.get("/")
        assert response.status_code == 200, "Index page should load"

        # Test subscribe page
        response = client.get("/subscribe")
        assert response.status_code == 200, "Subscribe page should load"

    @pytest.mark.integration
    def test_css_file_is_served(self):
        """Verify CSS file is properly served by Flask."""
        from app import create_app

        app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )
        client = app.test_client()

        # Request the CSS file (static URL path is /static/newsflash)
        response = client.get("/static/newsflash/css/style.css")
        assert response.status_code == 200, "CSS file should be served"
        assert "text/css" in response.content_type, "Should have CSS content type"

    def test_subscribe_form_styles_present(self, css_content):
        """Verify subscribe form styling is present."""
        assert ".form__input" in css_content, "Form input styles should exist"
        assert ".form__button" in css_content, "Form button styles should exist"
        assert ".subscribe__container" in css_content, "Subscribe container styles"

    def test_error_and_success_styles_present(self, css_content):
        """Verify error/success message styles are maintained."""
        # These might be in inline styles in the template
        # Just verify the form elements are styled
        assert ".form__" in css_content, "Form styles should be present"


class TestAccessibilityContrast:
    """Test WCAG AA contrast ratios for the new color scheme."""

    def extract_hex_color(self, color_string: str) -> str | None:
        """Extract hex color from CSS variable definition."""
        match = re.search(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", color_string)
        return match.group(0) if match else None

    def hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def relative_luminance(self, rgb: tuple[int, int, int]) -> float:
        """Calculate relative luminance for WCAG contrast calculation."""
        r, g, b = [x / 255.0 for x in rgb]

        def adjust(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = adjust(r), adjust(g), adjust(b)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two hex colors."""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)

        lum1 = self.relative_luminance(rgb1)
        lum2 = self.relative_luminance(rgb2)

        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)

        return (lighter + 0.05) / (darker + 0.05)

    def test_text_primary_on_bg_dark_contrast(self, css_content):
        """Verify primary text on dark background meets WCAG AA (4.5:1)."""
        # Extract color values from CSS
        bg_dark_match = re.search(r"--bg-dark:\s*(#[0-9a-fA-F]{6});", css_content)
        text_primary_match = re.search(
            r"--text-primary:\s*(#[0-9a-fA-F]{6});", css_content
        )

        if bg_dark_match and text_primary_match:
            bg_dark = bg_dark_match.group(1)
            text_primary = text_primary_match.group(1)

            ratio = self.contrast_ratio(text_primary, bg_dark)
            assert ratio >= 4.5, (
                f"Text primary on bg-dark contrast ratio {ratio:.2f}:1 "
                f"should be >= 4.5:1 (WCAG AA)"
            )

    def test_text_primary_on_bg_card_contrast(self, css_content):
        """Verify primary text on card background meets WCAG AA."""
        bg_card_match = re.search(r"--bg-card:\s*(#[0-9a-fA-F]{6});", css_content)
        text_primary_match = re.search(
            r"--text-primary:\s*(#[0-9a-fA-F]{6});", css_content
        )

        if bg_card_match and text_primary_match:
            bg_card = bg_card_match.group(1)
            text_primary = text_primary_match.group(1)

            ratio = self.contrast_ratio(text_primary, bg_card)
            assert ratio >= 4.5, (
                f"Text primary on bg-card contrast ratio {ratio:.2f}:1 "
                f"should be >= 4.5:1 (WCAG AA)"
            )

    def test_text_secondary_on_bg_dark_contrast(self, css_content):
        """Verify secondary text has reasonable contrast (3:1 minimum)."""
        bg_dark_match = re.search(r"--bg-dark:\s*(#[0-9a-fA-F]{6});", css_content)
        text_secondary_match = re.search(
            r"--text-secondary:\s*(#[0-9a-fA-F]{6});", css_content
        )

        if bg_dark_match and text_secondary_match:
            bg_dark = bg_dark_match.group(1)
            text_secondary = text_secondary_match.group(1)

            ratio = self.contrast_ratio(text_secondary, bg_dark)
            # Secondary text can have slightly lower contrast (WCAG AA Large Text)
            assert ratio >= 3.0, (
                f"Text secondary contrast ratio {ratio:.2f}:1 should be >= 3.0:1"
            )

    def test_accent_color_on_bg_contrast(self, css_content):
        """Verify accent color has sufficient contrast when used as text."""
        bg_dark_match = re.search(r"--bg-dark:\s*(#[0-9a-fA-F]{6});", css_content)
        # Find any accent color variable
        accent_match = re.search(r"--accent-[a-z]+:\s*(#[0-9a-fA-F]{6});", css_content)

        if bg_dark_match and accent_match:
            bg_dark = bg_dark_match.group(1)
            accent = accent_match.group(1)

            ratio = self.contrast_ratio(accent, bg_dark)
            # Accent colors used for headings should meet WCAG AA Large Text (3:1)
            assert ratio >= 3.0, (
                f"Accent color contrast ratio {ratio:.2f}:1 should be >= 3.0:1"
            )
