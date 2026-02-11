#!/bin/bash
# IARA Development Server Script

set -e

echo "========================================"
echo "  IARA Development Server"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Docker services are running
if ! docker compose ps | grep -q "running"; then
    echo -e "${YELLOW}Starting Docker services...${NC}"
    docker compose up -d
    sleep 3
fi

echo -e "${GREEN}Starting development server...${NC}"
echo ""
echo "The app will open automatically when ready."
echo "Hotkey: Cmd/Ctrl + Shift + Space"
echo ""

# Start the Electron app in dev mode
pnpm dev
