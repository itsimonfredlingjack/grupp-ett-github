#!/bin/bash
# Run Flask app with cloudflared tunnel
#
# This script starts the Flask app and exposes it via cloudflared tunnel.
# The tunnel provides:
# - TLS encryption (AC1: protect user data)
# - IP masking (AC2: hide origin IP)
#
# Usage:
#   ./scripts/run_with_tunnel.sh           # Quick tunnel (random URL)
#   ./scripts/run_with_tunnel.sh named     # Named tunnel (requires setup)
#
# Prerequisites:
#   - cloudflared installed: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
#   - Python venv activated
#
# Security guarantees:
#   - All traffic encrypted via Cloudflare edge
#   - Origin server IP never exposed
#   - No inbound ports required

set -e

# Configuration
FLASK_PORT="${FLASK_PORT:-5000}"
TUNNEL_NAME="${TUNNEL_NAME:-grupp-ett}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Flask app with cloudflared tunnel${NC}"
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo -e "${RED}Error: cloudflared is not installed${NC}"
    echo "Install from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
    exit 1
fi

# Check if Flask app exists
if [ ! -f "app.py" ]; then
    echo -e "${RED}Error: app.py not found. Run from project root.${NC}"
    exit 1
fi

# Activate venv if not active
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}Warning: No virtual environment found${NC}"
    fi
fi

# Kill any existing processes on cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    kill $FLASK_PID 2>/dev/null || true
    kill $TUNNEL_PID 2>/dev/null || true
    echo -e "${GREEN}Cleanup complete${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Flask in background
echo -e "${GREEN}Starting Flask app on port $FLASK_PORT...${NC}"
python app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 2

# Check if Flask is running
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo -e "${RED}Error: Flask failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}Flask running with PID $FLASK_PID${NC}"

# Start cloudflared tunnel
if [ "$1" = "named" ]; then
    # Named tunnel (requires cloudflared login and tunnel creation)
    echo -e "${GREEN}Starting named tunnel: $TUNNEL_NAME${NC}"
    echo -e "${YELLOW}Note: Named tunnel requires prior setup with 'cloudflared tunnel create $TUNNEL_NAME'${NC}"

    cloudflared tunnel run --url http://localhost:$FLASK_PORT $TUNNEL_NAME &
    TUNNEL_PID=$!
else
    # Quick tunnel (no setup required, random URL)
    echo -e "${GREEN}Starting quick tunnel (random URL)...${NC}"
    echo ""
    echo -e "${YELLOW}Security information:${NC}"
    echo -e "  - All traffic is TLS encrypted by Cloudflare"
    echo -e "  - Your origin IP is hidden (visitors see Cloudflare IPs)"
    echo -e "  - No firewall ports need to be opened"
    echo ""

    cloudflared tunnel --url http://localhost:$FLASK_PORT &
    TUNNEL_PID=$!
fi

# Wait a moment for tunnel to establish
sleep 3

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Services running:${NC}"
echo -e "  Flask app:   http://localhost:$FLASK_PORT"
echo -e "  Tunnel:      Check above for public URL"
echo -e ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Wait for processes
wait $FLASK_PID $TUNNEL_PID
