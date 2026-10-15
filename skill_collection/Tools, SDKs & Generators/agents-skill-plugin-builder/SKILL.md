---
name: "agents-skill-plugin-builder"
description: "Create Cowork/Claude Code knowledge-work plugins from user requirements through a guided design process. Use when asked to \"create a plugin\", \"build a plugin\", \"make a plugin\", \"scaffold a plugin\", \"new plugin\", \"plugin template\", or when packaging skills, commands, and connectors into a distributable plugin for a specific role or workflow. Walks users through requirements gathering, component design, and generates the complete plugin directory structure."
---

# Plugin Builder

Build complete knowledge-work plugins through a guided requirements and design process. Plugins turn Claude into a specialist for a specific role, team, or workflow by bundling skills, slash commands, and connectors (MCP servers) into a single distributable package.

Plugins are built for [Claude Cowork](https://claude.com/product/cowork) and are also compatible with [Claude Code](https://claude.com/product/claude-code). Every component is file-based — markdown and JSON, no code, no infrastructure, no build steps.

The package format follows the [Agent Plugins specification](https://agent-plugins.org/) (v1.0.0), a vendor-neutral standard for portable plugin packages. The spec defines two portable component types — Agent Skills and MCP servers — plus a reverse-domain namespace mechanism for client-specific extensions such as Claude's slash commands, which are not part of the portable core.

## How Plugins Work

Every plugin follows the same structure:

```
plugin-name/
├── plugin.json                  # Manifest (spec-defined, plugin root)
├── mcp.json                     # Tool connections (connectors, spec-defined)
├── com.anthropic.claude/        # Client extension namespace
│   └── commands/                 # Slash commands users invoke explicitly
│       └── command-name.md
├── skills/                      # Domain knowledge Claude draws on automatically
│   └── skill-name/
│       └── SKILL.md
├── CONNECTORS.md                # Documents tool categories and options
└── README.md                    # Usage documentation
```

**Three component types:**

- **Skills** encode domain expertise, best practices, and step-by-step workflows. Claude draws on them automatically when relevant. Each skill is a directory containing a `SKILL.md` file, discovered from the spec-defined `skills/` directory at the plugin root.
- **Commands** are explicit slash commands users trigger (e.g., `/plugin-name:review-contract`). The Agent Plugins spec does not define slash commands as a portable component, so command files live under the `com.anthropic.claude/` client extension namespace, in `com.anthropic.claude/commands/`.
- **Connectors** wire Claude to external tools via MCP servers, declared in the spec-defined `mcp.json`. Plugin files use `~~category` placeholders (e.g., `~~CRM`, `~~chat`) to stay tool-agnostic. `mcp.json` pre-configures specific servers, and `CONNECTORS.md` documents available options.

## Plugin Creation Process

### Phase 1: Discovery — Understand the Plugin's Purpose

Ask the user to describe what the plugin should do. Gather answers to these questions:

1. **Role or function**: "What role or job function is this plugin for? (e.g., sales, legal, finance, customer support, product management, engineering)"
2. **Core capabilities**: "What are the 3-5 key things this plugin should help with?"
3. **Target audience**: "Who will use this — just you, your team, or the community?"
4. **External tools**: "What tools does this role depend on? (e.g., Slack, Jira, Salesforce, Snowflake)"
5. **Example scenarios**: "Give 2-3 examples of how someone would use this plugin day-to-day."

Map the plugin to the governing taxonomy while the purpose is still fluid. Use a user-supplied taxonomy when available; otherwise load `references/agent-taxonomy.md`.
- Select the closest domain/category for the plugin's primary role or workflow.
- Use that placement to guide plugin naming, skill grouping, README language, and marketplace categorization.
- If the plugin creates reusable skills intended for this repository's `skills/` catalog, those skills must use the selected taxonomy category prefix or another valid prefix from the taxonomy.
- If the plugin creates private plugin-local skills, short names are allowed, but still record the taxonomy home in the design summary so related agents stay organized consistently.

Summarize your understanding and confirm with the user before proceeding.

### Phase 2: Component Inventory — Determine What Goes in the Plugin

Walk through each component type and collaborate with the user to design them.

#### Skills

Skills are domain knowledge Claude draws on automatically when relevant. They encode expertise, best practices, and workflows — the "how your team does things" knowledge.

Ask:
- "What domain expertise should Claude have for this role?"
- "What workflows, best practices, or processes should Claude follow?"
- "Are there any specialized analysis methods, frameworks, or standards?"

For each skill, capture:
- **Name** (kebab-case, 1-64 chars)
- **Description** (what it covers and when Claude should use it)
- **Taxonomy home** (domain/category from the governing taxonomy; reusable catalog skills must use the category prefix)
- **Key content areas** (the domain knowledge, workflows, templates)
- **Customization points** — identify tool-specific references that should use `~~category` placeholders for portability

Good skill examples from existing plugins:

| Plugin | Skill | What It Covers |
|---|---|---|
| sales | `account-research` | Research methodology, source prioritization, intel synthesis |
| legal | `contract-review` | Playbook-based clause analysis, risk flagging, redline generation |
| data | `sql-queries` | SQL best practices across dialects, common patterns, optimization |
| customer-support | `ticket-triage` | Category taxonomy, priority framework, routing rules |
| marketing | `brand-voice` | Voice documentation, tone adaptation, style guide enforcement |

#### Commands

Commands are explicit slash commands users invoke (e.g., `/plugin-name:command-name`). They define a specific workflow that runs when triggered. Commands are a Claude-specific extension, not a portable Agent Plugins component, so they live under `com.anthropic.claude/commands/`.

Ask:
- "What explicit actions should users be able to trigger with a slash command?"
- "For each command: What inputs does it need? What does it produce? What's the step-by-step workflow?"

For each command, capture:
- **Name** (becomes `/plugin-name:command-name`)
- **Description** (one-line summary)
- **Workflow** (step-by-step process)
- **Inputs** (what the user provides)
- **Output format** (what gets produced)

Command markdown files should include:
- Trigger description
- Connectors note: `> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).`
- Workflow steps
- Output format
- Example usage

Good command examples:

| Plugin | Command | What It Does |
|---|---|---|
| sales | `/call-summary` | Process call notes, extract action items, draft follow-up |
| data | `/analyze` | Answer data questions from quick lookups to full analyses |
| legal | `/review-contract` | Review contract against playbook, flag deviations, generate redlines |
| product-management | `/write-spec` | Generate PRD from problem statement |
| marketing | `/draft-content` | Draft blog posts, social media, emails, landing pages |

#### Connectors (MCP Servers)

Connectors wire Claude to the external tools the role depends on via MCP servers, declared in the spec-defined `mcp.json`.

Ask:
- "What external tools should this plugin connect to?"
- "For each tool category: What's the primary tool? What are alternatives?"
- "Does the server run as a remote endpoint (`streamable-http`) or a local subprocess (`stdio`)?"

For each connector, capture:
- **Category** (e.g., CRM, chat, project tracker, data warehouse)
- **Placeholder** (the `~~category` reference used in skill/command files)
- **Primary/included servers** (pre-configured in `mcp.json`, with transport type)
- **Alternative options** (other tools in same category)

Connector categories commonly used across plugins:

| Category | Placeholder | Common tools |
|---|---|---|
| Chat | `~~chat` | Slack, Microsoft Teams, Discord |
| Email | `~~email` | Microsoft 365, Gmail |
| CRM | `~~CRM` | HubSpot, Salesforce, Close, Pipedrive |
| Project tracker | `~~project tracker` | Jira, Linear, Asana, Monday, ClickUp |
| Knowledge base | `~~knowledge base` | Notion, Confluence, Guru |
| Data warehouse | `~~data warehouse` | Snowflake, BigQuery, Databricks |
| Cloud storage | `~~cloud storage` | Box, Egnyte, Dropbox, Microsoft 365 |
| Analytics/BI | `~~analytics` | Amplitude, Tableau, Looker |
| Design | `~~design` | Figma, Canva |
| Office suite | `~~office suite` | Microsoft 365, Google Workspace |

**Important**: Plugin files should be tool-agnostic — use `~~category` placeholders instead of hardcoding specific tool names. This makes the plugin work regardless of which specific tool the user connects.

### Phase 3: Design Review — Refine Before Building

Present a complete design summary showing:

1. **Plugin metadata**: name, description, version, target role
2. **Taxonomy mapping**: plugin domain/category, plus each reusable skill's taxonomy prefix or private-skill exception
3. **Skills table**: each skill with name and what it covers
4. **Commands table**: each command with name and what it does
5. **Connectors table**: each category with placeholder, transport type, included servers, and alternatives
6. **Example workflows**: 2-3 realistic usage scenarios showing skills and commands in action
7. **Directory tree**: the planned file structure

Ask the user:
- "Does this look right? Anything to add, remove, or change?"
- "Are the tool categories correct? Any tools missing?"
- "Do the example workflows cover your most common scenarios?"

Iterate until the user approves the design.

### Phase 4: Implementation — Generate the Plugin

Build the plugin following the standard structure. See [references/plugin-reference.md](references/plugin-reference.md) for the complete schema and conventions.

#### Directory structure

```
plugin-name/
├── plugin.json
├── mcp.json
├── com.anthropic.claude/
│   └── commands/
│       ├── command-one.md
│       └── command-two.md
├── skills/
│   ├── skill-one/
│   │   ├── SKILL.md
│   │   └── references/          # Optional, for large reference docs
│   └── skill-two/
│       └── SKILL.md
├── CONNECTORS.md
└── README.md
```

**Critical rules:**
- `plugin.json` and `mcp.json` live at the plugin root — there is no `.claude-plugin/` wrapper directory
- `skills/` is a spec-defined portable component and lives at the plugin root
- Commands are a Claude-specific extension and live under `com.anthropic.claude/commands/`, not at the plugin root
- Use `~~category` placeholders for tool references, not specific tool names
- Use the governing taxonomy to classify the plugin and any reusable skills; enforce taxonomy prefixes for skills meant to live in a reusable catalog
- Every component is markdown or JSON — no code required
- Keep SKILL.md files under 500 lines; split large content into `references/`
- All paths must resolve inside the plugin root; do not use symlinks or paths that escape it

#### Generate plugin.json

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Brief plugin description",
  "extensions": {
    "com.anthropic.claude": {}
  }
}
```

`$schema` and `name` are required. `name` must be 1-64 characters, lowercase alphanumeric with hyphens or periods only, no leading/trailing hyphen or period, and no `--` or `..` runs. `name` becomes the command namespace (e.g., `/plugin-name:command`). The schema is closed — do not add fields beyond `$schema`, `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `extensions`. If `author` is present it must be an object (`{"name": ..., "email": ..., "url": ...}`), not a plain string. Client-specific settings go under `extensions.<reverse-domain-namespace>`, e.g. `extensions["com.anthropic.claude"]`.

#### Generate Skills

Each skill gets a `skills/<skill-name>/SKILL.md` file:

```markdown
---
name: skill-name
description: 'What domain knowledge this covers. Claude uses this automatically when relevant.'
---

# Skill Title

[Domain expertise, workflows, best practices, templates, and frameworks]
```

Skills should:
- Encode "how we do things" knowledge — processes, standards, frameworks
- Use `~~category` for tool references (e.g., "Check ~~project tracker for...")
- Include actionable workflows, not just descriptions
- Provide templates and examples where helpful

Skill naming rules:
- **Plugin-local skills**: use concise kebab-case names like `account-research` because the plugin namespace provides context.
- **Reusable catalog skills**: use `<taxonomy-category-prefix>-<descriptor>` from the governing taxonomy, with folder name and frontmatter `name` matching exactly.
- Do not introduce stray prefixes such as `agent-*`, `prompt-*`, or `tech-*`; map them to `agents-*`, `ai-prompt-*`, `engineering-*`, or another valid taxonomy prefix.

Skills are discovered one level deep only: each immediate child of `skills/` that contains a file named exactly `SKILL.md` is treated as one skill. Do not nest a skill inside another subdirectory of `skills/`.

#### Generate Commands

Each command gets a `com.anthropic.claude/commands/<command-name>.md` file:

```markdown
---
description: One-line summary of what this command does
---

# /command-name

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

[Brief description of purpose]

## Workflow

1. [Step one — gather inputs]
2. [Step two — analyze/process]
3. [Step three — generate output]

## Output Format

[Describe the expected output structure]

## Examples

[Show 1-2 example interactions]
```

#### Generate CONNECTORS.md

```markdown
# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. For example, `~~CRM` might mean Salesforce, HubSpot, or any other CRM with an MCP server.

Plugins are **tool-agnostic** — they describe workflows in terms of categories (CRM, chat, email, etc.) rather than specific products. `mcp.json` pre-configures specific MCP servers, but any MCP server in that category works.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options |
|----------|-------------|-----------------|---------------|
| Chat | `~~chat` | Slack | Microsoft Teams |
| ... | ... | ... | ... |
```

#### Generate mcp.json

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "server-name": {
      "type": "streamable-http",
      "url": "https://mcp-server-url.example.com"
    }
  }
}
```

`$schema` and `mcpServers` are required. Each server entry needs a `type` of `stdio`, `streamable-http`, or `sse`:
- `streamable-http` (preferred for remote servers): requires `url` (absolute, no fragment; HTTPS required unless the host is loopback); `headers` optional.
- `sse`: same shape as `streamable-http`, for legacy servers only.
- `stdio` (local subprocess): requires `command` (a single executable token or a `./`-relative path); `args` and `env` optional, and `cwd` optional (plugin root by default). `args`, `env` values, and `cwd` may use `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` placeholders; `env` keys must not be named `PLUGIN_ROOT` or `PLUGIN_DATA`.

For servers not yet configured, include a comment-style placeholder or note in CONNECTORS.md that the URL is not yet configured.

#### Generate README.md

Follow the standard pattern used by knowledge-work plugins:

````markdown
# Plugin Name

A [role] plugin primarily designed for [Cowork](https://claude.com/product/cowork), Anthropic's agentic desktop application — though it also works in Claude Code. [Brief description of capabilities].

## Installation

```
claude plugins add marketplace/plugin-name
```

## What It Does

[Bulleted list of key capabilities with brief descriptions]

## Commands

| Command | Description |
|---------|-------------|
| `/command-one` | ... |
| `/command-two` | ... |

## Skills

| Skill | Description |
|-------|-------------|
| `skill-one` | ... |
| `skill-two` | ... |

## Example Workflows

### Scenario Name

```
You: /command-name [input]
Claude: [What Claude does step by step]
```

## Data Sources / MCP Integration

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](CONNECTORS.md).

[Describe what tools enhance the plugin and how to connect them]
````

### Phase 5: Customization Points — Make It Adaptable

Review all generated files and ensure tool references use `~~category` placeholders. This pattern allows teams to customize the plugin for their specific tools without rewriting workflows.

For each `~~category` placeholder:
- Verify it appears in CONNECTORS.md with included servers and alternatives
- Ensure skill/command files reference tools generically (e.g., "Check ~~project tracker" not "Check Jira")
- Consider what organization-specific values might need customization

### Phase 6: Validation — Verify the Plugin

Run through this checklist:

- [ ] `plugin.json` exists at the plugin root (not inside a `.claude-plugin/` directory) with valid JSON
- [ ] `plugin.json` has `$schema` set to `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` and a `name` field
- [ ] `name` matches the spec pattern: lowercase alphanumeric, hyphens/periods only, no leading/trailing separator, no `--` or `..`
- [ ] `plugin.json` has no fields beyond the closed schema's allowed set; `author`, if present, is an object, not a string
- [ ] Each skill folder is an immediate child of `skills/` and contains a `SKILL.md` with `name` and `description` in frontmatter
- [ ] Taxonomy mapping is documented; reusable catalog skills use a valid prefix from the governing taxonomy
- [ ] Command files live under `com.anthropic.claude/commands/`, not at the plugin root; each has a `description` in frontmatter
- [ ] All tool references use `~~category` placeholders, not hardcoded tool names
- [ ] `CONNECTORS.md` documents every `~~category` used in the plugin
- [ ] `mcp.json` exists at the plugin root with `$schema` set to `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json` and pre-configures at least the primary connectors
- [ ] Every `mcp.json` server entry uses `type: stdio`, `type: streamable-http`, or `type: sse` — never a bare `"http"`
- [ ] `README.md` includes Installation, What It Does, Commands, Skills, Example Workflows, and Data Sources
- [ ] Skill files are under 500 lines
- [ ] Everything is markdown and JSON — no code, no build steps
- [ ] No file path in the plugin (including symlink targets) resolves outside the plugin root

Present the checklist results. Fix any issues found.

### Phase 7: Testing & Next Steps

Provide the user with testing and distribution guidance:

**Testing locally (Claude Code):**
```bash
claude --plugin-dir ./plugin-name
```

**Installing via marketplace (Claude Code):**
```bash
claude plugin marketplace add <marketplace-source>
claude plugin install plugin-name@marketplace-name
```

**Installing via Cowork:**
Install from [claude.com/plugins](https://claude.com/plugins/).

**Customizing for your team:**
- Edit `mcp.json` to point at your specific tool stack
- Add company context to skill files (terminology, processes, standards)
- Modify workflows to match how your team actually works
- Replace `~~category` placeholders with your specific tools using the `cowork-plugin-customizer` skill

## Troubleshooting

| Issue | Solution |
|---|---|
| Plugin not loading | Validate JSON syntax in `plugin.json`; confirm it sits at the plugin root, not in a `.claude-plugin/` subdirectory |
| Commands not appearing | Ensure command files are under `com.anthropic.claude/commands/` |
| Skills not triggering | Check `description` field is detailed enough for Claude to match |
| Connectors not working | Verify `mcp.json` format, that each server `type` is `stdio`/`streamable-http`/`sse`, and MCP server URLs |
| Namespace wrong | Update `name` field in `plugin.json` |
| Placeholders still showing | Run customization to replace `~~category` values |

## Reference

For complete technical details, load these resources:
- **Plugin structure & conventions**: See [references/plugin-reference.md](references/plugin-reference.md)
- **Real-world examples**: See [references/plugin-examples.md](references/plugin-examples.md)
- **Portable taxonomy**: See `references/agent-taxonomy.md` before naming reusable skills or classifying plugin capabilities when the user does not provide a project taxonomy
- **Agent Plugins specification**: https://agent-plugins.org/
- **Existing plugins**: Browse https://github.com/anthropics/knowledge-work-plugins
