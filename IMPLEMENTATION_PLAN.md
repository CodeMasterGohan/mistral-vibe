# Implementation Plan: Cora (formerly Mistral Vibe) Transformation

This document outlines the detailed steps to transform the application into "Cora" for the 402nd SWEG, removing Mistral branding and telemetry, and configuring it for an internal "devstral2" server.

## 1. Dependencies and Command Name
- [ ] **Modify `pyproject.toml`**:
    - Remove `mistralai` from `dependencies`.
    - Change `project.scripts`: replace `vibe = "vibe.cli.entrypoint:main"` with `cora = "vibe.cli.entrypoint:main"`.
    - (Optional) Update `description` to "Minimal CLI coding agent for 402nd SWEG".
- [ ] **Update Environment**:
    - Run `uv sync` to remove the unneeded package and update the lockfile.

## 2. Code Removal (Mistral Integration)
- [ ] **Delete File**: `vibe/core/llm/backend/mistral.py`.
- [ ] **Update Factory**:
    - Edit `vibe/core/llm/backend/factory.py`.
    - Remove `Backend.MISTRAL` key and `MistralBackend` import.

## 3. Configuration Updates (`vibe/core/config.py`)
- [ ] **Remove Mistral Backend Enum**: Remove `MISTRAL` from `Backend` enum.
- [ ] **Update `DEFAULT_PROVIDERS`**:
    - Remove the "mistral" provider entry.
    - Add/Update a "devstral2" provider:
      ```python
      ProviderConfig(
          name="devstral2",
          api_base="http://localhost:8000/v1",  # Placeholder
          api_key_env_var="CORA_API_KEY",
          backend=Backend.GENERIC,
      )
      ```
- [ ] **Update `DEFAULT_MODELS`**:
    - Remove "mistral-vibe-cli-latest" and "devstral-small-latest".
    - Add "devstral-2":
      ```python
      ModelConfig(
          name="devstral-2",
          provider="devstral2",
          alias="devstral-2",
          input_price=0.0,
          output_price=0.0,
      )
      ```
    - Update `VibeConfig.active_model` default to "devstral-2".
- [ ] **Remove Validation Logic**:
    - Remove `WrongBackendError` class.
    - Remove/Update `_check_api_backend_compatibility` validator in `VibeConfig`.
- [ ] **Environment Variables**:
    - Ensure code looks for `CORA_API_KEY` instead of `MISTRAL_API_KEY`.

## 4. Branding and Strings
- [ ] **Search and Replace**:
    - **Mistral** -> **402nd SWEG**
    - **vibe** (when referring to the app name) -> **cora**
    - **Vibe** -> **Cora**
- [ ] **Target Files**:
    - `vibe/cli/entrypoint.py`:
        - Update `argparse` description.
        - Update "Hello Vibe!" in history file creation.
        - Update "Bye!" message (optional).
    - `vibe/cli/textual_ui/app.py`:
        - Update UI titles.
    - `vibe/setup/onboarding/screens/welcome.py`:
        - Update welcome message text.
        - **Keep** the ASCII art as requested.
    - `vibe/setup/onboarding/screens/api_key.py`:
        - Update prompt to ask for `CORA_API_KEY` or generic API key.
        - Update instructions to refer to the internal server.
    - `vibe/core/config.py`:
        - Update `GLOBAL_CONFIG_DIR` related constants if we want to change `.vibe` to `.cora` (Decision: **Keep `.vibe` directory** as per user request, but maybe update internal display names).
    - `README.md` (if applicable/present): Update basic info.

## 5. Documentation
- [ ] **Create `CORA_SETUP.md`**:
    - Instructions on how to set `CORA_API_KEY`.
    - Instructions on how to point to the actual internal server URL.
    - Usage of `cora` command.

## 6. Testing and Verification
- [ ] **Fix Tests**:
    - Run `uv run pytest`.
    - Identify tests failing due to missing `mistralai`.
    - Remove or adapt tests in `tests/backend/` and others.
- [ ] **Manual Verification**:
    - Run `uv run cora --help` to check the command name and description.
    - Run `uv run cora` (will likely fail connecting to localhost:8000 but should start the UI/onboarding).
