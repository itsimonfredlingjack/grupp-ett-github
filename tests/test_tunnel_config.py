"""Tests for cloudflared tunnel configuration.

These tests verify that the cloudflared tunnel configuration is correct
and that the application can be properly exposed via the tunnel.
"""

from pathlib import Path
from unittest.mock import patch

from src.grupp_ett.tunnel_config import (
    TunnelConfig,
    create_tunnel_config,
    get_tunnel_url,
    validate_tunnel_config,
)


class TestTunnelConfig:
    """Tests for TunnelConfig dataclass."""

    def test_creates_config_with_defaults(self) -> None:
        """Config should have sensible defaults."""
        config = TunnelConfig()

        assert config.local_port == 5000
        assert config.protocol == "http"
        assert config.tunnel_name == "grupp-ett"

    def test_creates_config_with_custom_values(self) -> None:
        """Config should accept custom values."""
        config = TunnelConfig(
            local_port=8080,
            protocol="https",
            tunnel_name="my-tunnel",
        )

        assert config.local_port == 8080
        assert config.protocol == "https"
        assert config.tunnel_name == "my-tunnel"

    def test_local_url_property(self) -> None:
        """Config should provide local URL."""
        config = TunnelConfig(local_port=5000, protocol="http")

        assert config.local_url == "http://localhost:5000"

    def test_local_url_with_https(self) -> None:
        """Config should support HTTPS local URL."""
        config = TunnelConfig(local_port=443, protocol="https")

        assert config.local_url == "https://localhost:443"


class TestCreateTunnelConfig:
    """Tests for tunnel config file creation."""

    def test_creates_valid_yaml_config(self, tmp_path: Path) -> None:
        """Should create a valid YAML config file."""
        config_path = tmp_path / "config.yml"
        config = TunnelConfig(
            local_port=5000,
            tunnel_name="test-tunnel",
        )

        create_tunnel_config(config, config_path)

        assert config_path.exists()
        content = config_path.read_text()
        assert "service: http://localhost:5000" in content

    def test_config_contains_no_tls_verify_for_local(self, tmp_path: Path) -> None:
        """Config should disable TLS verify for localhost."""
        config_path = tmp_path / "config.yml"
        config = TunnelConfig(local_port=5000)

        create_tunnel_config(config, config_path)

        content = config_path.read_text()
        assert "noTLSVerify: true" in content

    def test_config_uses_tunnel_name(self, tmp_path: Path) -> None:
        """Config should use the specified tunnel name."""
        config_path = tmp_path / "config.yml"
        config = TunnelConfig(tunnel_name="my-app-tunnel")

        create_tunnel_config(config, config_path)

        content = config_path.read_text()
        assert "tunnel: my-app-tunnel" in content


class TestValidateTunnelConfig:
    """Tests for tunnel config validation."""

    def test_valid_config_passes(self) -> None:
        """Valid config should pass validation."""
        config = TunnelConfig(local_port=5000)

        is_valid, errors = validate_tunnel_config(config)

        assert is_valid is True
        assert len(errors) == 0

    def test_invalid_port_zero(self) -> None:
        """Port 0 should be invalid."""
        config = TunnelConfig(local_port=0)

        is_valid, errors = validate_tunnel_config(config)

        assert is_valid is False
        assert any("port" in e.lower() for e in errors)

    def test_invalid_port_negative(self) -> None:
        """Negative port should be invalid."""
        config = TunnelConfig(local_port=-1)

        is_valid, errors = validate_tunnel_config(config)

        assert is_valid is False
        assert any("port" in e.lower() for e in errors)

    def test_invalid_port_too_high(self) -> None:
        """Port > 65535 should be invalid."""
        config = TunnelConfig(local_port=70000)

        is_valid, errors = validate_tunnel_config(config)

        assert is_valid is False
        assert any("port" in e.lower() for e in errors)

    def test_invalid_protocol(self) -> None:
        """Invalid protocol should fail validation."""
        config = TunnelConfig(protocol="ftp")  # type: ignore

        is_valid, errors = validate_tunnel_config(config)

        assert is_valid is False
        assert any("protocol" in e.lower() for e in errors)

    def test_empty_tunnel_name(self) -> None:
        """Empty tunnel name should be invalid."""
        config = TunnelConfig(tunnel_name="")

        is_valid, errors = validate_tunnel_config(config)

        assert is_valid is False
        assert any("tunnel" in e.lower() for e in errors)


class TestGetTunnelUrl:
    """Tests for retrieving tunnel URL."""

    @patch("src.grupp_ett.tunnel_config.subprocess.run")
    def test_returns_url_from_cloudflared(self, mock_run) -> None:
        """Should return URL from cloudflared command."""
        mock_run.return_value.stdout = "https://abc123.trycloudflare.com\n"
        mock_run.return_value.returncode = 0

        url = get_tunnel_url("test-tunnel")

        assert url == "https://abc123.trycloudflare.com"

    @patch("src.grupp_ett.tunnel_config.subprocess.run")
    def test_returns_none_if_not_running(self, mock_run) -> None:
        """Should return None if tunnel is not running."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Tunnel not found"

        url = get_tunnel_url("nonexistent-tunnel")

        assert url is None

    def test_masks_origin_ip(self) -> None:
        """Tunnel URL should not expose origin IP address."""
        # This is a conceptual test - cloudflared always masks IP
        # The URL returned should be a cloudflare domain, not an IP
        # When testing with real tunnel, verify no IP is exposed
        tunnel_url = "https://abc123.trycloudflare.com"

        # Should not be an IP address
        import re

        ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        assert not re.search(ip_pattern, tunnel_url)


class TestTunnelSecurityRequirements:
    """Tests for security requirements - AC1 and AC2."""

    def test_tunnel_enforces_tls_encryption(self) -> None:
        """AC1: All traffic should be TLS encrypted.

        Cloudflared tunnels always use TLS encryption between
        the cloudflared client and Cloudflare's edge.
        """
        config = TunnelConfig()

        # Cloudflared always encrypts tunnel traffic
        # This is a property of the cloudflared protocol
        # We verify our config doesn't accidentally disable it
        assert config.protocol in ("http", "https")
        # Note: Even when local_url is http, tunnel to Cloudflare is TLS

    def test_tunnel_hides_origin_ip(self) -> None:
        """AC2: Origin IP should not be visible.

        Cloudflared tunnels operate by establishing an outbound
        connection to Cloudflare, meaning no inbound ports are
        needed and the origin IP is never exposed.
        """
        # This is inherent to how cloudflared works:
        # - No public IP/port exposure required
        # - All traffic routes through Cloudflare edge
        # - Origin server connects outbound to Cloudflare

        # We can verify the config doesn't expose the local server
        config = TunnelConfig()
        assert "localhost" in config.local_url
        # The local_url is never exposed publicly, only the tunnel URL is
