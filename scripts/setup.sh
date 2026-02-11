#!/bin/bash
# IARA Project Setup Script

set -e

echo "========================================"
echo "  IARA Project Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} $1 found"
}

echo "Checking required tools..."
check_command node
check_command pnpm
check_command conda
check_command docker

echo ""
echo "Checking Node.js version..."
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo -e "${RED}Error: Node.js 20+ is required (found v$NODE_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js version is adequate"

echo ""
echo "========================================"
echo "  Installing Node.js dependencies"
echo "========================================"
pnpm install

echo ""
echo "========================================"
echo "  Setting up Python environment (Conda + uv)"
echo "========================================"

CONDA_ENV_NAME="iara-agent"

# Check if conda environment already exists
if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    echo -e "${YELLOW}!${NC} Conda environment '${CONDA_ENV_NAME}' already exists"
    echo "Updating environment..."
    conda env update -f agent/environment.yml --prune
else
    echo "Creating conda environment '${CONDA_ENV_NAME}'..."
    conda env create -f agent/environment.yml
fi

echo ""
echo "Activating conda environment and installing Python dependencies with uv..."

# Source conda for script usage
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"

# Activate the environment
conda activate ${CONDA_ENV_NAME}

echo -e "${GREEN}✓${NC} Conda environment activated"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

# Install dependencies using uv
cd agent

echo "Installing Python dependencies with uv..."
uv pip install -e ".[dev]"

echo -e "${GREEN}✓${NC} Python dependencies installed"

cd ..

echo ""
echo "========================================"
echo "  Setting up environment"
echo "========================================"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file from .env.example"
else
    echo -e "${YELLOW}!${NC} .env file already exists, skipping"
fi

echo ""
echo "========================================"
echo "  Starting Docker services"
echo "========================================"
docker compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check if Ollama is available
echo ""
echo "========================================"
echo "  Checking Ollama"
echo "========================================"
if curl -s http://localhost:11439/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ollama is running"

    # Check for required models
    if ! curl -s http://localhost:11439/api/tags | grep -q "llama3.2:3b"; then
        echo -e "${YELLOW}!${NC} llama3.2:3b model not found. Install with:"
        echo "    ollama pull llama3.2:3b"
    fi

    if ! curl -s http://localhost:11439/api/tags | grep -q "nomic-embed-text"; then
        echo -e "${YELLOW}!${NC} nomic-embed-text model not found. Install with:"
        echo "    ollama pull nomic-embed-text"
    fi
else
    echo -e "${YELLOW}!${NC} Ollama is not running. Please install and start Ollama:"
    echo "    https://ollama.ai"
fi

echo ""
echo "========================================"
echo -e "${GREEN}  Setup complete!${NC}"
echo "========================================"
echo ""
echo "Python environment:"
echo "  Activate with: conda activate ${CONDA_ENV_NAME}"
echo ""
echo "Next steps:"
echo "  1. Activate conda: conda activate ${CONDA_ENV_NAME}"
echo "  2. Start the development server: pnpm dev"
echo "  3. Or start with docker: docker compose up"
echo ""
echo "Hotkey: Cmd/Ctrl + Shift + Space"
echo ""
