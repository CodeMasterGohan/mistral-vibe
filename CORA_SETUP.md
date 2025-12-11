# Cora Setup Guide

## Overview

Cora (formerly Mistral Vibe) has been customized for the 402nd SWEG. It is configured to connect to an internal "devstral2" server instead of Mistral's public API.

## Installation

Run the following command to update your environment:

```bash
uv sync
```

## Configuration

Cora uses a local configuration directory at `~/.vibe` (this directory name is preserved for compatibility).

### 1. API Key

You need to set the `CORA_API_KEY` environment variable. You can do this in your shell or by creating a `.env` file in `~/.vibe/.env`.

```bash
export CORA_API_KEY="your-internal-api-key"
```

If you don't have a key, contact the Internal Server Admin.

### 2. Internal Server URL

By default, Cora is configured to connect to `http://localhost:8000/v1`.

To change this to the actual internal server URL, edit `~/.vibe/config.toml`:

```toml
[[providers]]
name = "devstral2"
api_base = "http://your-internal-server:port/v1"
api_key_env_var = "CORA_API_KEY"
backend = "generic"
```

## Running Cora

To start the CLI:

```bash
uv run cora
```

To run in programmatic mode:

```bash
uv run cora -p "Create a python script to calculate fibonacci"
```

## Troubleshooting

- **Connection Error**: Ensure you are connected to the internal network and the URL in `config.toml` is correct.
- **Missing API Key**: Ensure `CORA_API_KEY` is set.
