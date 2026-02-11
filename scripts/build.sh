#!/bin/bash
# Lokai Build Script

set -e

echo "========================================"
echo "  Lokai Production Build"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Clean previous builds
echo "Cleaning previous builds..."
pnpm clean 2>/dev/null || true

# Type check
echo "Running type check..."
pnpm typecheck
if [ $? -ne 0 ]; then
    echo -e "${RED}Type check failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Type check passed"

# Build Python agent
echo ""
echo "Building Python agent..."
cd agent
poetry build
cd ..
echo -e "${GREEN}✓${NC} Python agent built"

# Build Electron app
echo ""
echo "Building Electron app..."
pnpm build
echo -e "${GREEN}✓${NC} Electron app built"

echo ""
echo "========================================"
echo -e "${GREEN}  Build complete!${NC}"
echo "========================================"
echo ""
echo "Output directory: apps/desktop/release/"
echo ""
