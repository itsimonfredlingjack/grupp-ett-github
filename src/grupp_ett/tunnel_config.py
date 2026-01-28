"""Cloudflared tunnel configuration module.

This module provides utilities for configuring and managing
cloudflared tunnels for secure access to the Flask application.

Cloudflared tunnels provide:
- TLS encryption for all traffic (AC1)
- Origin IP masking (AC2)
- No need to open inbound ports
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class TunnelConfig:
    """Configuration for cloudflared tunnel.

    Attributes:
        local_port: Port where the local Flask app is running.
        protocol: Protocol for local connection (http or https).
        tunnel_name: Name identifier for the tunnel.
    """

    local_port: int = 5000
    protocol: Literal["http", "https"] = "http"
    tunnel_name: str = "grupp-ett"

    @property
    def local_url(self) -> str:
        """Get the local URL that the tunnel will connect to.

        Returns:
            Local URL string (e.g., 'http://localhost:5000').
        """
        return f"{self.protocol}://localhost:{self.local_port}"


def create_tunnel_config(config: TunnelConfig, config_path: Path) -> None:
    """Create a cloudflared tunnel configuration file.

    Args:
        config: TunnelConfig with tunnel settings.
        config_path: Path where the config file will be written.

    The generated config uses YAML format compatible with cloudflared.
    """
    yaml_content = f"""# Cloudflared tunnel configuration
# Generated for grupp-ett Flask application
# This provides TLS encryption and IP masking

tunnel: {config.tunnel_name}
credentials-file: ~/.cloudflared/{config.tunnel_name}.json

ingress:
  - service: {config.local_url}
    originRequest:
      noTLSVerify: true

  # Catch-all rule (required by cloudflared)
  - service: http_status:404
"""

    config_path.write_text(yaml_content)


def validate_tunnel_config(config: TunnelConfig) -> tuple[bool, list[str]]:
    """Validate tunnel configuration.

    Args:
        config: TunnelConfig to validate.

    Returns:
        Tuple of (is_valid, list of error messages).
    """
    errors: list[str] = []

    # Validate port
    if config.local_port <= 0:
        errors.append("Port must be greater than 0")
    elif config.local_port > 65535:
        errors.append("Port must be less than or equal to 65535")

    # Validate protocol
    if config.protocol not in ("http", "https"):
        errors.append("Protocol must be 'http' or 'https'")

    # Validate tunnel name
    if not config.tunnel_name or config.tunnel_name.strip() == "":
        errors.append("Tunnel name cannot be empty")

    return (len(errors) == 0, errors)


def get_tunnel_url(tunnel_name: str) -> str | None:
    """Get the public URL for a running tunnel.

    Args:
        tunnel_name: Name of the tunnel to query.

    Returns:
        Public URL string if tunnel is running, None otherwise.
    """
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "info", tunnel_name],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return None

        # Parse the URL from output
        # The output format varies, but URL is typically on its own line
        output = result.stdout.strip()
        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("https://") and ".trycloudflare.com" in line:
                return line
            if line.startswith("https://") and "cloudflare" in line.lower():
                return line

        # If we got output but couldn't parse URL, return the raw output
        # This handles cases where the URL format changes
        return output if output else None

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
