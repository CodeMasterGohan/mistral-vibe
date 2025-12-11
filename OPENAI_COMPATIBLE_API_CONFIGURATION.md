To configure an OpenAI-compatible API endpoint in Mistral Vibe, you need to modify your `config.toml` file. This file is typically located at `~/.vibe/config.toml` (global) or `.vibe/config.toml` (project-specific).

You will need to add a new **Provider** and then link a **Model** to that provider.

### 1. Add a Provider

Add a `[[providers]]` section to define your OpenAI-compatible service.

```toml
[[providers]]
name = "my_custom_provider"           # A unique internal name for this provider
api_base = "https://api.example.com/v1" # The base URL of the API
api_key_env_var = "MY_PROVIDER_API_KEY" # The name of the environment variable holding your API key
api_style = "openai"                  # Use "openai" for OpenAI-compatible APIs
```

*   **`name`**: An identifier you will use to reference this provider in the `models` configuration.
*   **`api_base`**: The full URL to the API endpoint (often ending in `/v1`).
*   **`api_key_env_var`**: The name of the environment variable where you store your API key. Vibe will look for this variable in your shell environment or in your `~/.vibe/.env` file.
*   **`api_style`**: Keeps this as `"openai"` to ensure the client formats requests correctly.

### 2. Add a Model

Add a `[[models]]` section to define a model that uses the provider you just created.

```toml
[[models]]
name = "gpt-4-turbo"                  # The model ID expected by the API
provider = "my_custom_provider"       # Must match the 'name' of the provider defined above
alias = "gpt4"                        # A short alias you can use in the CLI (e.g., --model gpt4)
input_price = 10.0                    # (Optional) Cost per million input tokens
output_price = 30.0                   # (Optional) Cost per million output tokens
```

*   **`name`**: The actual model string sent to the API (e.g., `gpt-4`, `llama-3-70b`, etc.).
*   **`provider`**: Must match the `name` field from your `[[providers]]` entry.
*   **`alias`**: A friendly name you can use to select this model in Vibe (e.g., via `vibe --model gpt4`).

### 3. (Optional) Set API Key

If you haven't already, add your API key to your `~/.vibe/.env` file or export it in your shell.

**In `~/.vibe/.env`:**
```bash
MY_PROVIDER_API_KEY=sk-your-api-key-here
```

### Example: Using LocalAI or LlamaCPP

If you are running a local inference server compatible with OpenAI (like LlamaCPP):

```toml
[[providers]]
name = "local_server"
api_base = "http://localhost:8080/v1"
api_key_env_var = "" # Leave empty if no key is required

[[models]]
name = "mistral-7b"
provider = "local_server"
alias = "local"
```

### Example: Using Groq

```toml
[[providers]]
name = "groq"
api_base = "https://api.groq.com/openai/v1"
api_key_env_var = "GROQ_API_KEY"

[[models]]
name = "llama3-70b-8192"
provider = "groq"
alias = "groq-llama3"
```

### 4. Activate the Model

To use your new model, start Vibe with the `--model` flag (or `active_model` in config):

```bash
vibe --model groq-llama3
```

Or set it as the default in your `config.toml`:

```toml
active_model = "groq-llama3"
```