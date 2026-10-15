---
name: "chasqui-create-module"
description: "INVOKE when adding a capability to a Chasqui agent — a new tool the LLM can call, or a Tool Module (tools + tables + admin config). This is how you give the agent abilities (price lookups, lead capture, bookings, integrations). Covers `chasqui generate module`, the module contract, and the 'docstring IS the prompt' rule. In Chasqui, adding a tool means writing/extending a Tool Module — there is no separate tool registry to edit."
---

# Create a Tool Module (add a capability)

The **Tool Registry** is Chasqui's differentiating piece: agent capabilities are
delivered as **Tool Modules** the core auto-discovers — self-contained packages
bundling tools, optional tables, admin config forms, and routes. Adding a tool =
writing (or extending) a module. Operators enable/disable each tool at runtime in
the panel (`/tools`); no deploy.

> Source of truth — read before writing:
> - **How to write a module** (scaffold, contract, tool rules, tables, admin, tests):
>   https://raw.githubusercontent.com/chasqui-stack/chasqui/v0.4.0/docs/MODULES.md
> - **Architecture §8** (Tool Registry — §8.1 how a tool is defined, §8.2 the
>   module contract, §8.3 the reusable archetype):
>   https://raw.githubusercontent.com/chasqui-stack/chasqui/v0.4.0/docs/ARCHITECTURE.md
> - **Worked example:** https://raw.githubusercontent.com/chasqui-stack/chasqui/v0.4.0/docs/design/module-example-commercial-locations.md

## Scaffold

```bash
chasqui generate module price_check                # tools + config + test
chasqui generate module price_check --with-models  # + a SQLModel table
chasqui generate module price_check --with-admin   # + /admin/modules/price_check routes
```

(See the `chasqui-cli` skill for the CLI overall.) Drop the package in
`core/app/modules/` and restart — discovery is automatic.

## The contract (what to implement)

A module is a package exposing a module-level `module` attribute with:

- `name` + `config_key`
- `register_tools()` — **required**, returns the LangChain tools
- `register_models()` — optional, module-owned SQLModel tables
- `register_admin_routes(router)` — optional, `/admin/modules/<name>/*`
- `config_schema()` — optional, admin-editable knobs (a form for free)

Read MODULES.md §"The contract" for the exact shape; don't reproduce it from
memory.

## The rule that bites: the docstring IS the prompt

Tools are LangChain `@tool` async functions taking `ToolRuntime[TurnContext]`. The
**docstring is what the LLM reads** to decide when to call the tool — write it for
the model, in **English** (the system prompt localizes the user-facing reply).

- Return serializable data (a string is best). Tool exceptions become error
  `ToolMessage`s automatically — don't catch-and-hide.
- A tool needing more data returns *instructions to ask for it* (the model relays
  the question and calls again) — see the `lead_capture` pattern in MODULES.md.
- `runtime.context` gives `ctx.session` (AsyncSession), `ctx.contact`,
  `ctx.conversation`, `ctx.config`.

## After you write it

- `--with-models`? Generate the migration:
  `cd core && make makemigrations m="add price_check tables" && make migrate`
  (Alembic, not create_all).
- Enable the tool in the admin panel (`/tools`) and fill the config form.
- Tests: mirror an existing module's test (MODULES.md §Testing).
- Run the MODULES.md ship checklist before opening the PR.

## Anti-patterns

- ❌ Looking for a central "tool registry" file to edit — there isn't one; write a
  module, discovery is automatic.
- ❌ A docstring written for humans — it's the model's only signal to call the tool.
- ❌ Business logic outside `core/` — modules live in `core/app/modules/`.
- ❌ Spanish (or any non-English) tool docstrings/names — English-only codebase.
