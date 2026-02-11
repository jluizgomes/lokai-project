# Lokai

Lokai is a desktop AI assistant that runs 100% locally on your machine. It combines natural language processing with OS automation to help you with development tasks, file management, terminal commands, and more.

## Features

- **Natural Language Interface**: Talk to your computer in plain English
- **100% Local**: All processing happens on your machine - complete privacy
- **OS Automation**: Manage files, run commands, control applications
- **Learning**: Lokai learns from your patterns to provide smarter suggestions
- **Cross-Platform**: Works on macOS and Linux

## Tech Stack

### Frontend
- Electron 28
- React 18
- TypeScript 5.3
- TailwindCSS + shadcn/ui
- Zustand for state management

### Backend
- Python 3.11+
- LangChain + LangGraph
- Ollama for local LLMs

### Databases
- PostgreSQL (action logs, preferences)
- Qdrant (vector embeddings)
- Neo4j (knowledge graph)

## Prerequisites

- Node.js 20+
- pnpm 8+
- Python 3.11+
- Poetry 1.7+
- Docker & Docker Compose
- Ollama

## Quick Start

1. **Clone and install**:
   ```bash
   git clone <repository-url>
   cd lokai-project
   ./scripts/setup.sh
   ```

2. **Install Ollama models**:
   ```bash
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```

3. **Start development server**:
   ```bash
   pnpm dev
   ```

4. **Use the hotkey**: `Cmd/Ctrl + Shift + Space` to open Lokai

## Project Structure

```
lokai-project/
├── apps/desktop/          # Electron desktop app
│   ├── src/main/          # Electron main process
│   ├── src/preload/       # Preload scripts
│   └── src/renderer/      # React UI
├── packages/
│   ├── shared/            # Shared types and constants
│   └── database/          # Database schemas
├── agent/                 # Python AI agent
│   └── src/lokai_agent/   # Agent code
│       ├── graph/         # LangGraph state machine
│       ├── tools/         # LangChain tools
│       ├── llm/           # LLM clients
│       └── database/      # Database clients
├── scripts/               # Development scripts
└── docker-compose.yml     # Local databases
```

## Development

### Commands

| Command | Description |
|---------|-------------|
| `pnpm install` | Install dependencies |
| `pnpm dev` | Start development server |
| `pnpm build` | Build for production |
| `pnpm typecheck` | Run TypeScript type check |
| `pnpm lint` | Run ESLint |
| `docker compose up -d` | Start databases |
| `docker compose down` | Stop databases |

### Python Agent

```bash
cd agent
poetry install
poetry run python -m lokai_agent.main
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
# Ollama
OLLAMA_HOST=http://localhost:11439
OLLAMA_MODEL=llama3.2:3b

# Databases
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

## Safety

Lokai is designed with safety in mind:

- **Permission System**: Actions are classified by risk level
- **Approval Required**: Destructive actions require user confirmation
- **Sandboxing**: File operations restricted to allowed directories
- **Audit Logging**: All actions are logged

## License

MIT
