# Meta MCP Server

![CI](https://github.com/leon/MetaMCP/actions/workflows/ci.yml/badge.svg)

A Model Context Protocol (MCP) server providing a unified interface for interacting with the Meta ecosystem: Facebook, Instagram, and WhatsApp APIs.

## Features

- **Unified Interface**: Single MCP server exposing 4 standardized tools for all Meta platforms
- **Multi-Platform Support**: Facebook Messenger, Instagram Direct/Feed, WhatsApp Business
- **Demo Mode**: Test without credentials using mock adapters
- **Production Ready**: Docker containerization, structured logging, retry logic, error handling
- **Type Safe**: Built with Pydantic models and full type hints

## Tools

### 1. `meta_send_message`
Send messages on Facebook, Instagram, or WhatsApp.

### 2. `meta_get_messages`
Retrieve conversation history (Facebook & Instagram only).

### 3. `meta_post_content`
Post to Facebook or Instagram feed.

### 4. `meta_get_analytics`
Get insights/metrics from Facebook or Instagram.

## Quick Start

### Demo Mode (No Credentials Required)

```bash
# Clone and install
git clone <repository>
cd MetaMCP
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run in demo mode
DEMO_MODE=true python -m src
```

### Production Mode

1. **Configure Environment**:

```bash
cp .env.example .env
# Edit .env with your Meta App credentials
```

2. **Run the Server**:

```bash
# Using the installed CLI
meta-mcp-server
```

### Docker Deployment

```bash
# Build
docker build -t meta-mcp .

# Run (interactive mode required for stdio)
docker run -i --env-file .env meta-mcp
```

Or use docker-compose:

```bash
docker-compose up
```

## Configuration

Required environment variables (see `.env.example`):

- `META_APP_ID` - Your Facebook App ID
- `META_APP_SECRET` - Your Facebook App Secret
- At least one platform token:
  - `FACEBOOK_PAGE_ACCESS_TOKEN`
  - `INSTAGRAM_ACCESS_TOKEN`
  - `WHATSAPP_ACCESS_TOKEN` + `WHATSAPP_PHONE_NUMBER_ID`

Optional:
- `META_API_VERSION` (default: v21.0)
- `LOG_LEVEL` (default: INFO)
- `DEMO_MODE` (default: false)

## Troubleshooting

### Authentication Errors ("403 Forbidden")
If `meta_post_content` fails with 403, you might be using a **User Token** instead of a **Page Token**.
Run the helper script to get the correct token:
```bash
python scripts/get_page_token.py
```

### "Session Expired" or "Decryption Failed"
Your token in `.env` is invalid or expired.
1. Generate a new token.
2. Update `.env`.
3. **Restart the server/container** to load the new config.

## MCP Client Configuration

Add the following configuration to your MCP client settings (e.g., Claude Desktop or others):

### Quick Setup:
```bash
# Option 1: Local (faster)
# Add to your client's config file (e.g., claude_desktop_config.json)
{
    "mcpServers": {
        "meta-mcp-server": {
            "command": "/home/[USERNAME]/projects/MetaMCP/venv/bin/meta-mcp-server",
            "args": [],
            "cwd": "/home/[USERNAME]/projects/MetaMCP"
        }
    }
}

# Option 2: Docker (isolated)
# See MCP_SETUP.md for details
```

See `MCP_SETUP.md` for detailed instructions and alternative configurations.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=src

# Lint and type check
ruff check src/ tests/
mypy src/
```

## Architecture

The server uses an **Adapter Pattern** for platform abstraction:

```
MCP Server → MetaClient → Platform Adapters (FB/IG/WA/Mock)
```

Each adapter implements the same interface, making it easy to add new platforms.

## Testing Without Real Credentials

Set `DEMO_MODE=true` to use mock adapters that return realistic fake data without hitting real APIs.

## License

MIT
