---
name: "aidlc-build-and-test"
description: "AI-DLC Build & Test only — generate comprehensive build, unit-test, integration-test, and (if applicable) performance / contract / e2e test instructions for an existing codebase under `aidlc-docs/construction/build-and-test/`. Use when the code already exists (whether AIDLC-generated or pre-existing) and the user wants build & test scaffolding documented. Trigger on phrases like \"set up build and test for this project\", \"generate build instructions\", \"I need test instructions for the units\", \"produce build-instructions.md and test-instructions.md\", \"document how to build and test this\", \"create CI-ready test plans\". For full Construction (per-unit design + code gen + build & test), use `aidlc-construction`. For just code generation, use `aidlc-code-generation`."
---

# AI-DLC Build & Test (Standalone)

This skill runs the Build & Test stage only — it analyzes existing code and produces a set of instruction files under `aidlc-docs/construction/build-and-test/` covering build, unit tests, integration tests, and any applicable performance / contract / e2e tests. It does NOT execute the tests itself; it produces the documented instructions other engineers (or CI) can follow.

## How this skill loads rule details

Detail files live in the sibling `aidlc` skill at `../aidlc/references/`. Read on demand.

**Always load at start**:
- `common/content-validation.md`
- `construction/build-and-test.md` — the core stage rules (this skill's main script)

**Extensions**: Check `aidlc-docs/aidlc-state.md` for enabled extensions. If property-based testing or security baseline are enabled, their rules likely impose specific test types — load and enforce them.

## Prerequisite check (lightweight)

Build & Test is the most context-tolerant of the AIDLC stages — it works on any existing codebase, not just AIDLC-generated code. But still:

1. Verify there is actual code to build/test in the workspace. If the workspace is empty, stop and tell the user this skill needs an existing implementation.
2. If `aidlc-docs/aidlc-state.md` exists and lists units of work, use them to scope per-unit build / test instructions. Otherwise, infer scope from the workspace's project structure (one unit by default).
3. If `aidlc-docs/inception/reverse-engineering/` exists for an unfamiliar codebase, load `architecture.md`, `code-structure.md`, `technology-stack.md` for grounding. If not and the codebase is unfamiliar, briefly suggest `aidlc-reverse-engineering` first — but do NOT block; proceed if the user wants build/test docs anyway.

## Execute

Follow `construction/build-and-test.md`:

1. Log user's request in `aidlc-docs/audit.md`.
2. Generate the instruction files under `aidlc-docs/construction/build-and-test/`:
   - `build-instructions.md` — how to build all units / the project (per-unit if multi-unit)
   - `unit-test-instructions.md` — how to execute unit tests
   - `integration-test-instructions.md` — interactions between units / external integrations
   - `performance-test-instructions.md` — only if performance NFRs apply
   - Additional instruction files as needed: `contract-test-instructions.md`, `security-test-instructions.md`, `e2e-test-instructions.md`
   - `build-and-test-summary.md` — index/overview of all the above
3. Validate any diagrams (Mermaid / ASCII) per `common/content-validation.md`.
4. Update `aidlc-docs/aidlc-state.md`.
5. **Wait for explicit user approval** with the prompt from `construction/build-and-test.md`: "**Build and test instructions complete. Ready to proceed to Operations stage?**" — but in this standalone context, the answer is essentially "the workflow ends here for now." Adapt the closing message accordingly:

```markdown
# 🧪 Build & Test Instructions Complete

Instructions: `aidlc-docs/construction/build-and-test/`

> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** — Iterate on the instructions.
> ▶️ **Run the Tests** — Follow the instructions to actually build and run tests (this skill produces docs, not test execution).
> 🛑 **Stop Here** — The Operations phase is currently a placeholder upstream.
```

## What NOT to do

- **Do NOT execute the build or tests.** This skill produces *instructions*. If the user wants you to actually run them, that's a separate task — be explicit about the boundary.
- **Do NOT generate code or design docs.** Other skills own those stages.
- **Do NOT skip the per-unit breakdown** if the project has multiple units of work — each unit's instructions should reference its specific build steps and test scope.

## Governance (inherited)

Audit trail, approval gates, content validation, state tracking — all inherited from the main workflow rules.
