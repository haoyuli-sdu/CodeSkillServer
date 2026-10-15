---
name: "build-copilot-plugin"
description: "End-to-end orchestrator that converts any codebase into a complete Copilot CLI plugin. Runs all 5 phases in sequence — analyze, map, generate, MCP server, validate. Use this as the main entry point when asked to \"build a plugin\", \"convert code to a plugin\", \"generate a copilot cli plugin\", or \"turn this into a plugin\"."
---

# Build Copilot CLI Plugin — Full Pipeline

Converts any codebase into a complete, installable Copilot CLI plugin by running all 5 phases in sequence. Each phase produces output that feeds into the next.

## Key Principle: Thin MCP, No Backend LLM

The generated plugin must follow the **thin MCP** pattern:
- **MCP server** = pure data layer (read/write to backends, nothing more)
- **Agents and skills** = all reasoning, decision-making, and prompt logic
- **No separate AI API keys** — the user's existing Copilot CLI subscription handles all LLM reasoning
- If the source codebase has backend LLM calls or prompt templates, those become **agent instructions** and **skill steps**, not MCP server code

This avoids double API costs, keeps backends stateless, and means the plugin works with just the user's Copilot CLI.

## Before You Start

Ask the user for:
1. **Source folder path** — the codebase to convert (default: `reference_code/`)
2. **Output folder path** — where to write the generated plugin (default: `generated-plugin/`)
3. **Plugin name** — what to call it (default: derived from the source folder)

## Pipeline

Execute these phases **in order**. Do not skip phases. Each phase uses its corresponding skill.

### Phase 1: Analyze Codebase
**Run**: `/analyze-codebase`

- Input: source folder path
- Output: **Codebase Analysis Report** (architecture, capabilities, integrations, policies)
- This report is the foundation — everything downstream depends on its accuracy

### Phase 2: Map Capabilities
**Run**: `/map-capabilities`

- Input: Codebase Analysis Report from Phase 1
- Output: **Capability Mapping Document** (which features become MCP tools, skills, agents, hooks, scripts)
- Present the mapping to the user for review before proceeding — this is where design decisions are made

**Checkpoint**: Show the user the mapping and ask if they want to adjust anything before generation.

### Phase 3: Generate Plugin Files
**Run**: `/generate-plugin`

- Input: Capability Mapping Document from Phase 2
- Output: All plugin files — `plugin.json`, agents, skills, hooks, scripts, custom instructions

### Phase 4: Generate MCP Server
**Run**: `/generate-mcp-server`

- Input: Capability Mapping Document from Phase 2 (specifically the MCP tools section)
- Output: `mcp-server/` directory with a stdio-based MCP server and `.mcp.json` config

### Phase 5: Validate
**Run**: `/validate-plugin`

- Input: the generated plugin directory
- Output: validation report — pass/fail for each component

If validation finds issues, fix them immediately before reporting success.

## Completion

After all 5 phases, present:

1. **File tree** of the generated plugin
2. **Component summary**: N agents, N skills, N MCP tools, N scripts, N hooks
3. **Install command**: `copilot plugin install ./path-to-plugin`
4. **Available commands**: list all slash commands and agents the user now has
5. **Setup required**: any environment variables, CLI tools, or auth needed

## Error Recovery

- If a phase fails, report what went wrong and which phase failed
- Do not proceed to the next phase until the current phase succeeds
- If the source folder is empty or invalid, stop at Phase 1 and ask for a valid path
