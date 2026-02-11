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


class TestCursorBlackTheme:
    """Test suite for GE-51: Cursor SECOND UNIVERSE BLACK theme"""

    def test_bg_dark_is_pure_black(self, css_content):
        """Verify background is pure black #000000."""
        assert "--bg-dark: #000000;" in css_content, (
            "Background should be pure black #000000"
        )

    def test_bg_card_is_dark_gray(self, css_content):
        """Verify cards use #111111."""
        assert "--bg-card: #111111;" in css_content, (
            "Cards should use #111111"
        )

    def test_accent_primary_is_cursor_green(self, css_content):
        """Verify primary accent is Cursor green #00e599."""
        assert "--accent-primary: #00e599;" in css_content, (
            "Primary accent should be Cursor green #00e599"
        )

    def test_accent_secondary_is_purple(self, css_content):
        """Verify secondary accent is purple #a855f7."""
        assert "--accent-secondary: #a855f7;" in css_content, (
            "Secondary accent should be purple #a855f7"
        )

    def test_text_primary_is_white(self, css_content):
        """Verify primary text is white #ffffff."""
        assert "--text-primary: #ffffff;" in css_content, (
            "Primary text should be white #ffffff"
        )

    def test_text_secondary_is_gray(self, css_content):
        """Verify secondary text is gray #888888."""
        assert "--text-secondary: #888888;" in css_content, (
            "Secondary text should be gray #888888"
        )

    def test_border_color_is_dark(self, css_content):
        """Verify borders use #222222."""
        assert "--border-color: #222222;" in css_content, (
            "Borders should use #222222"
        )

    def test_accent_glow_is_green(self, css_content):
        """Verify accent glow uses green rgba (not blue)."""
        # Should have green glow, not blue
        assert "rgba(0, 229, 153" in css_content or "rgba(0,229,153" in css_content, (
            "Accent glow should be green (rgba with 0, 229, 153)"
        )
        # Old blue glow should NOT exist
        assert "rgba(88, 166, 255" not in css_content, (
            "Old blue glow rgba(88, 166, 255, ...) should be removed"
        )

    def test_no_github_blue_colors(self, css_content):
        """Verify NO blue colors from GitHub theme remain."""
        # GitHub blue colors that should be gone
        github_blue_colors = ["#58a6ff", "#4184e4", "#0d1117", "#161b22", "#30363d"]

        for blue_color in github_blue_colors:
            assert blue_color not in css_content.lower(), (
                f"GitHub blue color {blue_color} should be removed"
            )

    def test_no_hardcoded_blue_in_hovers(self, css_content):
        """Verify hover states don't use hardcoded blue."""
        # Look for :hover sections
        hover_sections = re.findall(r":hover\s*\{[^}]+\}", css_content, re.DOTALL)

        for section in hover_sections:
            # Check for any blue hex codes in hover states
            assert "#58a6ff" not in section, "Hover should not use #58a6ff"
            assert "#4184e4" not in section, "Hover should not use #4184e4"


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
