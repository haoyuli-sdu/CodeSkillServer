---
name: "qa-vitest-writer"
description: "Generate Vitest unit and integration tests for TypeScript projects with ESM-native support, Vite integration, and Jest-compatible API."
---

# QA Vitest Writer

## Purpose

Write Vitest unit and integration tests from test case specifications. Transform structured test cases (from qa-testcase-from-docs, qa-manual-test-designer, or specs) into executable Vitest code with proper mocking, fixtures, and assertions.

## Trigger Phrases

- "Write Vitest tests for [module/feature]"
- "Generate Vitest unit tests from test cases"
- "Create Vitest integration tests"
- "Add Vitest tests for [spec/requirements]"
- "Migrate Jest tests to Vitest"
- "Vitest tests with mocks and fixtures"
- "In-source Vitest tests for [component]"
- "Parameterized Vitest tests (test.each)"

## Key Advantages

| Advantage | Description |
| --------- | ----------- |
| **ESM-native** | No CommonJS transformation; native `import`/`export` |
| **Vite integration** | Uses Vite for fast transforms, HMR, and config |
| **Watch mode** | Instant re-runs on file changes |
| **Jest-compatible API** | `describe`/`it`/`test`, `expect`, `vi` (like `jest`) |
| **In-source testing** | Co-locate tests with source (`__tests__` or `*.test.ts`) |
| **Workspace support** | Monorepo config with project-level overrides |

## Workflow

1. **Read test cases** — From specs, requirements, or manual test designs
2. **Analyze code** — Inspect module under test: exports, dependencies, types
3. **Generate tests** — Produce `describe`/`it` blocks with assertions
4. **Add mocks/fixtures** — Use `vi.mock`, `vi.fn`, `vi.spyOn`, fixtures as needed
5. **Verify** — Ensure tests run and pass; fix any config or import issues

## Context7 MCP

Use **Context7 MCP** for current Vitest documentation when:
- API signatures or options are uncertain
- New Vitest features (e.g., `vi.hoisted`, workspace config) need verification
- Migration from Jest requires up-to-date compatibility notes

## Key Patterns

| Pattern | Usage |
| ------- | ----- |
| `describe` / `it` / `test` | Test structure (Jest-compatible) |
| `vi.mock()` | Module substitution; hoisted before imports |
| `vi.fn()` | Mock function with call tracking |
| `vi.spyOn()` | Spy on existing method; optionally replace |
| `vi.hoisted()` | Run code before imports (ESM mocking) |
| In-source testing | `__tests__/` or `{module}.test.ts` / `{module}.spec.ts` |
| Snapshot testing | `expect(obj).toMatchSnapshot()` |
| Parameterized | `test.each([...])` / `it.each([...])` |
| Concurrent | `it.concurrent` / `test.concurrent` |

See `references/patterns.md` for detailed patterns.

## Configuration

- **Config file:** `vitest.config.ts` or `vite.config.ts` with `test` block
- **Workspace:** `vitest.workspace.ts` for monorepos
- **Coverage:** `v8` or `istanbul` via `@vitest/coverage-v8` / `@vitest/coverage-istanbul`

See `references/config.md` for configuration patterns.

## Migration from Jest

| Jest | Vitest | Notes |
| ---- | ------ | ----- |
| `jest.mock()` | `vi.mock()` | Same semantics; hoisted |
| `jest.fn()` | `vi.fn()` | Same API |
| `jest.spyOn()` | `vi.spyOn()` | Same API |
| `jest.useFakeTimers()` | `vi.useFakeTimers()` | Same API |
| `beforeAll` / `afterAll` | Same | Unchanged |
| `beforeEach` / `afterEach` | Same | Unchanged |

ESM: Use `vi.hoisted()` when variables must be available in `vi.mock` factory. See `references/best-practices.md`.

## File Naming

- `{module}.test.ts` — Preferred for unit tests
- `{module}.spec.ts` — Alternative; common for integration tests
- `__tests__/{module}.test.ts` — Co-located in source directory

## Scope

**Can do (autonomous):**
- Generate Vitest unit and integration tests from test cases
- Add mocks (`vi.mock`, `vi.fn`, `vi.spyOn`), fixtures, and setup/teardown
- Use `test.each` for parameterized tests; `it.concurrent` for parallel runs
- Configure `vitest.config.ts` and coverage
- Migrate Jest tests to Vitest (syntax and API mapping)
- Call qa-diagram-generator for test flow diagrams if needed

**Cannot do (requires confirmation):**
- Change production code to satisfy tests
- Add tests for requirements not in source documents
- Override project-level Vitest/Vite config without approval

**Will not do (out of scope):**
- Execute tests (user runs `vitest` or `npm test`)
- Write Playwright/Cypress E2E tests (use qa-playwright-ts-writer)
- Modify CI/CD pipelines

## References

- `references/patterns.md` — ESM mocking, in-source testing, concurrent tests, workspace
- `references/assertions.md` — Vitest/Chai assertion reference
- `references/config.md` — vitest.config.ts, coverage, workspace, plugins
- `references/best-practices.md` — Best practices, Jest migration patterns

## Quality Checklist

- [ ] Tests match test case steps and expected results
- [ ] Mocks are properly scoped (per test or per describe)
- [ ] No hardcoded secrets or sensitive data
- [ ] Assertions are specific (avoid only `toBeTruthy` where value matters)
- [ ] `beforeEach`/`afterEach` restore state; mocks reset where needed
- [ ] File naming follows project convention (`*.test.ts` or `*.spec.ts`)
- [ ] Imports use ESM (`import`); no `require` unless required by dependency
- [ ] Coverage targets considered if specified in requirements

## Troubleshooting

| Symptom | Likely Cause | Fix |
| ------- | ------------ | --- |
| `vi.mock` not working | ESM hoisting; variable not in scope | Use `vi.hoisted()` to define variables before imports |
| Mock returns undefined | Factory not returning correct shape | Ensure factory returns object matching module exports |
| Tests pass individually, fail together | Shared mutable state | Reset mocks in `beforeEach`; use `vi.clearAllMocks()` |
| `import.meta.env` wrong in tests | Env not set for test | Use `vi.stubEnv()` with `unstubEnvs: true` in config |
| Coverage not collected | Reporter not configured | Add `@vitest/coverage-v8`, set `coverage.reporter` |
| Slow test runs | No workspace or wrong config | Use `vitest.workspace.ts`; exclude node_modules |
| Type errors in mocks | Mock shape doesn't match types | Use `vi.mocked()` or type assertions; match export shape |
