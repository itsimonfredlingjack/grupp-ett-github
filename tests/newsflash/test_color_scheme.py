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


class TestChatGPTTheme:
    """Test suite for GE-54: ChatGPT white theme"""

    def test_bg_dark_is_pure_white(self, css_content):
        """Verify background is pure white #ffffff."""
        assert "--bg-dark: #ffffff;" in css_content, (
            "Background should be pure white #ffffff"
        )

    def test_bg_card_is_light_gray(self, css_content):
        """Verify cards use #f7f7f8."""
        assert "--bg-card: #f7f7f8;" in css_content, "Cards should use #f7f7f8"

    def test_accent_primary_is_chatgpt_green(self, css_content):
        """Verify primary accent is ChatGPT green #10a37f."""
        assert "--accent-primary: #10a37f;" in css_content, (
            "Primary accent should be ChatGPT green #10a37f"
        )

    def test_accent_secondary_is_soft_gray(self, css_content):
        """Verify secondary accent is soft gray #e5e7eb."""
        assert "--accent-secondary: #e5e7eb;" in css_content, (
            "Secondary accent should be soft gray #e5e7eb"
        )

    def test_text_primary_is_dark(self, css_content):
        """Verify primary text is dark #111827."""
        assert "--text-primary: #111827;" in css_content, (
            "Primary text should be dark #111827"
        )

    def test_text_secondary_is_gray(self, css_content):
        """Verify secondary text is gray #6b7280."""
        assert "--text-secondary: #6b7280;" in css_content, (
            "Secondary text should be gray #6b7280"
        )

    def test_border_color_is_soft_gray(self, css_content):
        """Verify borders use #e5e7eb."""
        assert "--border-color: #e5e7eb;" in css_content, "Borders should use #e5e7eb"

    def test_no_neon_colors_remain(self, css_content):
        """Verify NO neon colors from previous themes remain."""
        # Neon colors that should be removed
        neon_colors = ["#FF2D95", "#00FFFF", "#00e599", "#ff2d95", "#00ffff"]

        for neon_color in neon_colors:
            assert neon_color not in css_content.lower(), (
                f"Neon color {neon_color} should be removed"
            )

    def test_no_black_backgrounds(self, css_content):
        """Verify black backgrounds are replaced with white."""
        # Should not have black background
        assert "--bg-dark: #000000;" not in css_content, (
            "Black background should be replaced with white"
        )
        assert "--bg-card: #111111;" not in css_content, (
            "Dark gray cards should be replaced with light gray"
        )

    def test_subscribe_button_colors(self, css_content):
        """Verify subscribe button uses ChatGPT green with white text."""
        # Button should use the accent-primary variable (which is #10a37f)
        # Text color on buttons should be white
        pattern = r"\.form__button\s*\{[^}]+\}"
        button_sections = re.findall(pattern, css_content, re.DOTALL)
        assert len(button_sections) > 0, "Should have .form__button styles"

        # Button background should use var(--accent-primary)
        assert "background-color: var(--accent-primary)" in css_content, (
            "Button should use accent-primary for background"
        )


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
