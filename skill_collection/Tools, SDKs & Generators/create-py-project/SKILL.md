---
name: "create-py-project"
description: "Create, set up, bootstrap, or scaffold modern Python projects with best-in-class tooling. Use when users want to initialize Python projects, create FastAPI apps, build CLI tools, or set up project tooling (poetry, uv, ruff, mypy, pytest, pre-commit)."
---

# Create Python Project

Create, set up, bootstrap, or scaffold modern Python projects with best-in-class tooling.

**ALWAYS use this skill when the user wants to:**

- Set up, initialize, configure, or create ANY Python project from scratch
- Create FastAPI applications, APIs, microservices, web services, or REST APIs
- Build CLI tools, command-line utilities, or terminal applications
- Initialize Python packages, libraries, or modules
- Configure project tooling (poetry, uv, ruff, mypy, pytest, pre-commit)
- Start a new Python codebase or repository
- Scaffold project structure with proper configuration files

**Trigger on these phrases and contexts:**

- "set up", "setup", "initialize", "init", "scaffold", "bootstrap", "configure"
- "create project", "new project", "start project", "from scratch"
- "FastAPI", "API", "microservice", "web service", "REST API", "backend"
- "CLI tool", "command line", "terminal app", "script"
- "project structure", "project setup", "tooling", "configuration"
- Any mention of starting a new Python codebase with specific requirements

**Use this skill even if the user:**

- Doesn't explicitly say "bootstrap" or "initialize"
- Just describes what they want to build (e.g., "I need an API for X")
- Mentions the current directory/project needs Python setup
- Asks about project structure or best practices for a new project

This skill generates complete, working projects with pyproject.toml, main.py, package structure,
router setup (for FastAPI), pre-commit hooks, linting/formatting config, and all starter files.
It intelligently extracts requirements from user requests and auto-executes when intent is clear.

## Company Python Conventions

All agents must follow these architectural conventions when generating projects:

### Directory Structure

- **`shared/`** - Cross-cutting shared modules and **weak models**
  - Clients (API clients, database clients, external service wrappers)
  - Utilities and helpers
  - Weak models (DTOs, data transfer objects, simple data structures)
  - Infrastructure concerns (logging, config, observability)
- **`modules/`** - **Strong models** and domain services
  - Domain models with business logic
  - Services that utilize underlying `shared/` clients
  - Business logic and domain operations
  - Use cases and application services

### Architecture Principles

Follow these principles when generating code and structure:

- **KISS** (Keep It Simple, Stupid) - Prefer simple, straightforward solutions
- **YAGNI** (You Aren't Gonna Need It) - Don't add functionality until needed
- **DevEx** (Developer Experience) - Optimize for developer productivity and clarity
- **Clean Architecture** - Separate concerns, dependency inversion, domain-centric
- **Orthogonal** - Components should be independent and composable
- **Practical** - Pragmatic solutions over theoretical purity
- **DDD** (Domain-Driven Design) - Model the domain, ubiquitous language, bounded contexts

### Import Conventions

**CRITICAL: Avoid `from __future__ import ...` statements**

Organize projects to be orthogonal and prevent circular imports instead:

- Use proper layering: `modules/` depends on `shared/`, never the reverse
- Avoid circular dependencies by extracting shared logic to `shared/`
- Use dependency inversion: define interfaces/protocols in `shared/`, implement in `modules/`
- Use modern Python type hints directly (e.g., `list[str]`, `dict[str, Any]`)
- Orthogonal design eliminates the need for `__future__` imports

### Application to Generated Projects

**When generating FastAPI projects:**

- **`shared/`** - Create actual implementation files:
  - `shared/config.py` - Settings/configuration using pydantic-settings
  - `shared/{domain}_client.py` - API clients for external services
  - `shared/router.py` - FastAPI routers (can be split into multiple files)
  - `shared/models.py` - DTOs, request/response models (weak models)
- **`modules/`** - Create domain services that use shared clients:
  - `modules/{domain}_service.py` - Business logic that uses clients from shared/
  - `modules/models.py` - Domain models with business logic (strong models)
- **`{package_name}/`** - Keep minimal (usually just `__init__.py`)
- **Routers** can import from both `shared/` (for clients, config) and `modules/` (for services)

**When generating CLI projects:**

- **`shared/`** - Create utilities and helpers:
  - `shared/file_utils.py` - File I/O operations
  - `shared/api_client.py` - External API clients if needed
  - `shared/config.py` - Configuration management
- **`modules/`** - Create core business logic:
  - `modules/{domain}_processor.py` - Business logic that uses shared utilities
  - `modules/models.py` - Domain models
- **`{package_name}/`** - Keep minimal (usually just `__init__.py`)

#### Example: FastAPI Project Structure

```text
my-api/
├── main.py                      # FastAPI app, includes routers
├── pyproject.toml
├── my_api/                      # Package (minimal)
│   └── __init__.py
├── shared/                      # Infrastructure layer
│   ├── __init__.py
│   ├── config.py               # Settings (API keys, URLs, etc.)
│   ├── {domain}_client.py      # HTTP client for external API
│   └── router.py               # FastAPI routes
└── modules/                     # Domain layer
    ├── __init__.py
    ├── {domain}_service.py     # Business logic using client from shared/
    └── models.py               # Domain models
```

## What Gets Generated

**Core Files (Always):**

- **`pyproject.toml`** - Full project config with dependencies and tool settings
- **`main.py`** - Entry point (CLI or FastAPI with lifespan)
- **`.pre-commit-config.yaml`** - Git hooks configured for your type checker choice
- **`.gitignore`** - Python-specific ignores
- **`.env.example`** - Environment template with relevant variables for your project
- **`README.md`** - Complete documentation with accurate commands
- **`Justfile`** - Task runner with common commands
- **`.python-version`** - Python version (if pyenv detected)

**Package Structure (Always):**

- **`{package_name}/__init__.py`** - Package initialization (usually minimal/empty)
- **`shared/__init__.py`** - Shared modules directory (cross-cutting concerns, weak models)
- **`modules/__init__.py`** - Modules directory (domain models, business services)

**Additional Files Based on Project Type:**

- **FastAPI projects**: Create actual implementation files in `shared/` (clients, config, routers)
- **CLI projects**: Create actual implementation files in `shared/` (utilities, helpers) and `modules/` (business logic)

**All files contain working, customized content** - not placeholder text or generic templates.

**CRITICAL: Directory structure follows company conventions:**

- `shared/` for infrastructure, clients, utilities, weak models - **ALWAYS CREATE WITH ACTUAL FILES**
- `modules/` for domain logic, business services, strong models - **ALWAYS CREATE, populate based on domain**
- `{package_name}/` is typically minimal (just `__init__.py`) - **NOT the main code location**

## Tool Stack

- **Package Manager**: `poetry` (default) or `uv`
- **Linter/Formatter**: `ruff` (replaces black, flake8, isort, pydocstyle)
- **Type Checker**: `mypy` (default) or `ty`
- **Testing**: `pytest`
- **Git Hooks**: `pre-commit`

## Ruff Configuration

Uses the proven rule set from production projects:

- **Select**: E, F, W (flake8), I (isort), UP (pyupgrade), PL (pylint), B (bugbear), S (bandit), C90 (mccabe), D (pydocstyle)
- **Line length**: 88 (black-compatible)
- **Target Python**: Matches project version
- **Per-file ignores**: Tests, scripts, alembic

## Workflow

1. **Preflight Confirmation**: Ask whether to use all defaults
1. **Gather Requirements**: Collect user preferences and nuanced requirements
1. **Dynamic Generation**: File Generator agent creates customized, working files
1. **Validation**: Project Validator ensures correctness and completeness
1. **Fix Loop (if needed)**: Coordinate fixes until validation passes
1. **Initialize Environment**: Install dependencies with chosen package manager
1. **Runtime Validation**: Run linting/formatting to verify setup
1. **Next Steps**: Provide tailored guidance for the specific project

## Agent-Driven Architecture

This skill uses three specialized agents working together:

### 1. Setup Coordinator (Orchestrator)

- Gathers user requirements and preferences
- Interprets nuanced customization requests
- Delegates to File Generator and Project Validator
- Coordinates fix loops until validation passes
- Manages environment setup and tooling

### 2. File Generator (Content Creator)

- Generates all project files with appropriate, working content
- Adapts to user's specific needs (not rigid templates)
- Ensures all code is syntactically correct and complete
- Customizes based on project type, dependencies, and user intent
- Examples:
  - User mentions "Redis" → adds Redis deps, connection code, env vars
  - User mentions "auth" → adds JWT deps, auth routes, security examples
  - User mentions "database" → adds ORM deps, connection setup, migration hints

### 3. Project Validator (Quality Assurance)

- Validates all generated files for correctness
- Checks syntax, imports, configuration consistency
- Ensures no placeholder text remains
- Verifies type hints match Python version
- Reports findings without editing files

## Agents

This skill includes specialized agents for different tasks:

### Setup Coordinator (`agents/setup-coordinator.md`)

**Purpose**: Orchestrate the entire bootstrap process with flexible customization.

**Responsibilities**:

- Gather user requirements (8 configuration questions with smart defaults)
- Interpret nuanced customization requests
- Delegate file generation to File Generator agent
- Coordinate validation with Project Validator agent
- Handle edge cases (existing files, missing tools, version conflicts)
- Manage environment setup and dependency installation
- Provide tailored next steps

**Key Feature**: Understands nuanced user intent and passes it to File Generator for customization.

### File Generator (`agents/file-generator.md`)

**Purpose**: Dynamically generate all project files with appropriate, working content.

**Responsibilities**:

- Generate pyproject.toml with correct dependencies and configuration
- Create main.py with working entry point (CLI or FastAPI)
- Generate package structure with proper imports
- Create pre-commit config matching type checker choice
- Generate .env.example with relevant variables
- Create comprehensive README.md with accurate commands
- Generate Justfile with correct task definitions

**Key Feature**: Adapts content based on user's specific needs, not rigid templates.

**Customization Examples**:

- "API with Redis caching" → adds httpx, redis deps; Redis connection in lifespan; domain-specific routes
- "CLI for data processing" → adds pandas, argparse setup; file I/O examples
- "Strict type checking" → configures mypy strictest settings; 100% coverage requirement

### Project Validator (`agents/project-validator.md`)

**Purpose**: Comprehensively validate generated project files.

**Validation Checks**:

- All required files exist
- pyproject.toml is valid TOML with correct dependencies
- Python files have valid syntax (AST parseable)
- All imports are available in dependencies or stdlib
- YAML files are valid
- Package structure is correct
- Configuration is consistent across files
- No placeholder text remains
- Type hints match Python version
- README commands match package manager

**Key Feature**: Reports findings only; Setup Coordinator coordinates fixes.

______________________________________________________________________

## Step 1: Gather Requirements

### 1.0 Smart Preflight Decision

**Before asking any questions, analyze the user's request to determine if requirements are explicit.**

#### Auto-Execute Conditions (minimal or no questions)

If the user's request contains **explicit project requirements**, immediately proceed to file generation. Extract settings from their request and infer reasonable defaults for anything not specified.

**When to auto-execute without questions:**

- Request is clear and unambiguous
- All critical settings can be confidently inferred
- No conflicting requirements

**When to use `ask_user_question` for quick clarification (even in auto-execute mode):**

- Ambiguous project name (use `ask_user_question` with text input)
- Unclear if FastAPI or CLI when both could fit
- Multiple valid interpretations of tech stack
- User mentions both poetry and uv

**Explicit requirement indicators:**

- Project type mentioned: "FastAPI", "API", "microservice", "web service", "CLI tool", "package"
- Specific purpose/domain: "data processing", "authentication service", "API integration"
- Technology stack mentioned: "Redis", "PostgreSQL", "JWT", "database"
- Package manager mentioned: "poetry", "uv"

**Examples that should auto-execute:**

- "Set up a FastAPI microservice for {specific purpose}" → auto-execute, no questions
- "Create a CLI tool for data processing with pandas" → auto-execute, no questions
- "Bootstrap an API with Redis caching" → auto-execute, no questions
- "Initialize a Python package for authentication with JWT" → auto-execute, no questions

**Inferred settings for auto-execute:**

- FastAPI/API/microservice/web service → `is_fastapi=true`
- CLI/tool/package → `is_fastapi=false`
- Mentioned tech → add to dependencies
- Package manager mentioned → use that tool, otherwise `poetry`
- Python version → `3.13` (unless specified)
- Type checker → `mypy` (unless specified)
- Description → derive from user's stated purpose
- Project name → derive from directory name or purpose if clear

#### Interactive Mode (use ask_user_question)

If the user's request is **vague or generic**, enter interactive mode and use `ask_user_question` for all questions. If the user's request don't cover one of the specific questions required for generating a project, then use `ask_user_question` to ask for that information (one question at a time), if `ask_user_question` type tooling is not available (check), then ask via chat.

**Vague request examples:**

- "Set up a Python project"
- "Bootstrap this project"
- "Initialize Python tooling"
- "Create a new project"

**Interactive flow:**

1. **Check if `ask_user_question` is available** (it should be in Windsurf/Cascade)
1. **Ask preflight question** using `ask_user_question`:
   - Question: `Use default bootstrap settings?`
   - Options: `["yes", "no"]`
   - Default: `"yes"`
1. **If user says "yes"**: Proceed with defaults, show config preview
1. **If user says "no"**: Run full requirement-gathering flow using `ask_user_question` for all questions (see section 1.1 below)

**Default settings:**

- Package manager: `poetry`
- Python version: `3.13`
- Type checker: `mypy`
- FastAPI: `no`
- Description: `A Python project`
- Dependencies: none
- Dev dependencies: none (beyond built-in defaults)

**Tool usage:**

- In Windsurf/Cascade, **ALWAYS use `ask_user_question`** for requirement gathering
- Treat it as the primary interaction path for this skill in IDE environments
- Only fall back to plain chat questions if `ask_user_question` is truly unavailable or returns a tool-not-found/error

### If `ask_user_question` is available

Use `ask_user_question` in menu/select mode for questions with ≤4 discrete options. This reduces friction and prevents typing errors.

#### Questions to ask via menu

1. **Package manager** (menu): `poetry` (default) vs `uv`
1. **Python version** (menu): `3.12`, `3.13` (default), or `Other`
1. **Type checker** (menu): `mypy` (default), `ty`, or `none`
1. **FastAPI project?** (menu): `no` (default), `yes`

#### Questions to ask via text (free-form input)

1. **Project name**: Free text (derive from directory if empty)
1. **Description**: Free text (default: "A Python project")
1. **Dependencies**: Comma-separated list
1. **Dev dependencies**: Comma-separated list

### If `ask_user_question` is not available

Ask questions **sequentially, one at a time** to reduce communication friction. Do not present all questions at once.

#### Flow

1. Ask `Use default bootstrap settings? [Y/n]` first.
1. If yes, proceed with defaults and show a config preview before generation.
1. If no, ask first setup question → Wait for answer.
1. Ask second setup question → Wait for answer.
1. Continue until all 8 setup questions are answered.

This sequential approach prevents the user from feeling overwhelmed and allows for context-specific follow-ups.

### Questions Reference

| Question         | Default            | Options              | Input Type   |
| ---------------- | ------------------ | -------------------- | ------------ |
| Package manager  | `poetry`           | `poetry`, `uv`       | Menu or text |
| Python version   | `3.13`             | `3.12`, `3.13`       | Menu or text |
| Project name     | Directory name     | Any valid name       | Text         |
| Description      | "A Python project" | Free text            | Text         |
| Type checker     | `mypy`             | `mypy`, `ty`, `none` | Menu or text |
| FastAPI project? | `no`               | `yes`, `no`          | Menu or text |
| Dependencies     | (none)             | Comma-separated      | Text         |
| Dev dependencies | (none)             | Comma-separated      | Text         |

**Default dev dependencies always included:**

- `pytest`
- `pytest-asyncio`
- `ruff`
- `pre-commit`

**Additional defaults if type checker selected:**

- `mypy` or `ty` (based on choice)

**Additional defaults if FastAPI:**

- `fastapi[standard]`
- `uvicorn`
- `pydantic`

______________________________________________________________________

## Step 2: Generate Files

### 2.1 Read Templates

Read the appropriate templates from the skill's `templates/` directory based on user choices:

```text
templates/
├── pyproject-poetry.toml
├── pyproject-uv.toml
├── main-simple.py
├── main-fastapi.py
├── package_init.py
├── shared_router.py
├── pre-commit.yaml
├── gitignore
├── env.example
├── readme.md
└── justfile
```

### 2.2 Render Templates

Substitute these variables into templates using simple string replacement (`{{ variable }}`):

| Variable                  | Value                                       | Example                                   |
| ------------------------- | ------------------------------------------- | ----------------------------------------- |
| `tool`                    | `"poetry"` or `"uv"`                        | `poetry`                                  |
| `python_version`          | Python version                              | `3.13`                                    |
| `python_version_nodot`    | Version without dots                        | `313`                                     |
| `project_name`            | Package name (kebab-case)                   | `my-project`                              |
| `project_name_underscore` | Package name (snake_case)                   | `my_project`                              |
| `project_description`     | User's description                          | `A CLI tool`                              |
| `tool_name`               | Tool display name                           | `Poetry` or `uv`                          |
| `dependencies`            | Formatted dependency lines                  | `"requests",\n    "click",`               |
| `dev_dependencies`        | Formatted dev dependency lines              | `httpx = "*"` (poetry) or `"httpx",` (uv) |
| `fastapi_deps`            | FastAPI deps if enabled                     | `"fastapi[standard]",\n    "uvicorn",`    |
| `type_checker_dep`        | Type checker dependency line                | `mypy = "*"` or `"mypy",`                 |
| `mypy_config`             | mypy config section or empty                | `[tool.mypy]\nstrict = true`              |
| `mypy_precommit`          | mypy pre-commit hook or empty               | Full yaml block                           |
| `fastapi_env`             | FastAPI env vars or empty                   | `APP_HOST=127.0.0.1`                      |
| `install_cmd`             | Install command                             | `poetry install`                          |
| `activate_cmd`            | Activate command                            | `poetry shell`                            |
| `run_cmd`                 | Run command                                 | `poetry run python main.py`               |
| `ruff_check_cmd`          | Ruff check command                          | `poetry run ruff check .`                 |
| `ruff_format_cmd`         | Ruff format command                         | `poetry run ruff format .`                |
| `run_verbose_cmd`         | Run verbose command                         | `poetry run python main.py --verbose`     |
| `ruff_check_fix_cmd`      | Ruff check with fix                         | `poetry run ruff check --fix .`           |
| `setup_cmd`               | Setup environment                           | `poetry install`                          |
| `update_cmd`              | Update dependencies                         | `poetry update`                           |
| `add_dep_cmd`             | Add dependency                              | `poetry add`                              |
| `add_dev_cmd`             | Add dev dependency                          | `poetry add --group dev`                  |
| `project_structure`       | Project structure diagram                   | Directory tree                            |
| `is_fastapi`              | `true` or `false` (for file selection only) | -                                         |
| `use_pyenv`               | `true` if pyenv detected                    | `true` or `false`                         |

### 2.3 Write Files

Write these files to the target directory:

| File                         | Template                              | Condition                |
| ---------------------------- | ------------------------------------- | ------------------------ |
| `pyproject.toml`             | `pyproject-{tool}.toml`               | Always                   |
| `main.py`                    | `main-fastapi.py` or `main-simple.py` | Based on `is_fastapi`    |
| `{project_name}/__init__.py` | `package_init.py`                     | Always                   |
| `shared/__init__.py`         | Empty                                 | If `is_fastapi`          |
| `shared/router.py`           | `shared_router.py`                    | If `is_fastapi`          |
| `.pre-commit-config.yaml`    | `pre-commit.yaml`                     | Always                   |
| `.gitignore`                 | `gitignore`                           | Always                   |
| `.env.example`               | `env.example`                         | Always                   |
| `README.md`                  | `readme.md`                           | Always                   |
| `Justfile`                   | `justfile`                            | Always                   |
| `.python-version`            | Literal                               | If `use_pyenv` is `true` |

______________________________________________________________________

## Step 3: Initialize Environment

Prerequisite:

- Project Validator must have returned `valid: true`.

Run the appropriate commands based on tool choice:

### If Poetry

```bash
poetry install
```

### If uv

```bash
uv venv
uv pip install -e ".[dev]"
```

______________________________________________________________________

## Step 4: Validate Setup

Run initial formatting and linting:

### If Poetry (validation)

```bash
poetry run ruff check --fix .
poetry run ruff format .
```

### If uv (validation)

```bash
uv run ruff check --fix .
uv run ruff format .
```

Note:

- This step validates runtime tooling (ruff/formatting) after structural validation has already passed.

______________________________________________________________________

## Step 5: Live Test (Optional)

After validation passes, offer to run a live test of the application:

1. **Use `ask_user_question`** to ask:

   - Question: "Would you like me to run a live test of the application?"
   - Options: `["yes", "no"]`
   - Default: `"yes"`

1. **If user says "yes":**

   **For FastAPI projects:**

   - Start the server in the background: `poetry run python main.py` or `uv run python main.py`

   - Wait for server startup (check for "Application startup complete" or similar)

   - Test endpoints with `curl`:

     ```bash
     # Test health endpoint
     curl -s http://localhost:8000/health || echo "Health check failed"

     # Test root endpoint
     curl -s http://localhost:8000/ || echo "Root endpoint failed"

     # For APIs with specific routes, test those too
     # Example: curl -s http://localhost:8000/api/weather/current?city=Seattle&state=WA
     ```

   - Report results to user (success/failure for each endpoint)

   - Stop the server (send SIGTERM or use process management)

   **For CLI projects:**

   - Run the CLI with `--help` to verify it works: `poetry run python main.py --help`
   - If applicable, run a quick test with sample inputs
   - Report results to user

1. **If user says "no":**

   - Skip to Step 6

______________________________________________________________________

## Step 6: Print Next Steps

Show the user:

```text
✅ Project "{project_name}" bootstrapped successfully!

📁 Files created:
   - pyproject.toml (project config)
   - main.py (entry point)
   {shared/router.py if FastAPI}
   - .pre-commit-config.yaml (git hooks)
   - .gitignore
   - .env.example
   - README.md

🚀 Next steps:
   1. cd {directory}
   2. {poetry shell / source .venv/bin/activate}
   3. cp .env.example .env  # Edit with your values
   4. {poetry run python main.py / uv run python main.py}

📦 To add dependencies:
   {poetry add <package> / uv add <package>}

🔧 Tools configured:
   - ruff: linting & formatting (run: {poetry run ruff check . / uv run ruff check .})
   - {mypy/ty}: type checking (run: {poetry run mypy . / uv run mypy .})
   - pytest: testing (run: {poetry run pytest / uv run pytest})
   - pre-commit: git hooks (run: pre-commit install)
```

______________________________________________________________________

## Template Reference

### pyproject.toml Structure (Poetry)

```toml
[project]
name = "{project_name}"
version = "0.1.0"
description = "{project_description}"
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    # User-specified dependencies
]

[project.scripts]
{project_name} = "{project_name}.main:main"

[tool.poetry]
packages = [{include = "{project_name}"}]

[tool.poetry.group.dev.dependencies]
pytest = "*"
pytest-asyncio = "*"
ruff = "*"
pre-commit = "*"
# Type checker if selected
# User-specified dev dependencies

[tool.ruff]
line-length = 88
target-version = "py{python_version_nodot}"

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true

[tool.ruff.lint]
ignore = [
    "E203",
    "S110",
    "D100",
    "D104",
    "D107",
    "D203",
    "D213",
    "D105",
]
select = [
    "E", "F", "W",
    "I",
    "UP",
    "PL",
    "B",
    "S",
    "C90",
    "D"
]

[tool.ruff.lint.per-file-ignores]
"**/tests/**" = ["S101", "PLR2004"]
"**/test_*.py" = ["S101"]

[tool.ruff.lint.pylint]
max-args = 6

[tool.ruff.lint.mccabe]
max-complexity = 13

[tool.mypy]
# If mypy selected
strict = true
warn_return_any = true
warn_unused_ignores = true

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### main.py (FastAPI)

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import uvicorn
from fastapi import FastAPI

from shared.router import router as api_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler."""
    # Startup
    yield
    # Shutdown


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Hello from {project_name}!"}


app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

### shared/router.py

```python
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(content={"status": "healthy"}, status_code=status.HTTP_200_OK)
```

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.14.11
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.15.0
    hooks:
      - id: mypy
        args: [--strict]
```
