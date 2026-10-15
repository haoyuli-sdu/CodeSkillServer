---
name: "qa-pytest-writer"
description: "Generate pytest unit and integration tests for Python with fixtures, parametrize, markers, conftest patterns, and plugin ecosystem support."
---

# QA Pytest Writer

## Purpose

Write pytest unit and integration tests from test case specifications. Transform structured test cases (from qa-testcase-from-docs, qa-manual-test-designer, or specs) into executable pytest code with fixtures, parametrization, markers, and conftest patterns.

## Trigger Phrases

- "Write pytest tests for [module/function]"
- "Generate pytest unit tests from test cases"
- "Create pytest integration tests"
- "Add pytest tests with fixtures for [feature]"
- "Pytest parametrized tests for [function]"
- "Pytest tests with conftest fixtures"
- "Pytest async tests for [API handler]"
- "Pytest tests with mocking (monkeypatch/patch)"

## Key Features

| Feature | Description |
| ------- | ----------- |
| **Fixtures** | Scope: function, class, module, session; autouse, yield for teardown |
| **@pytest.mark.parametrize** | Data-driven tests with multiple input/output sets |
| **Markers** | skip, skipif, xfail, custom markers for categorization |
| **conftest.py** | Shared fixtures across test modules/directories |
| **Plugin ecosystem** | pytest-cov, pytest-xdist, pytest-asyncio, pytest-html, pytest-factoryboy |
| **Assertion introspection** | Rich failure output; plain `assert` statements |

## Workflow

1. **Read test cases** — From specs, requirements, or manual test designs
2. **Analyze Python code** — Inspect module under test: functions, classes, dependencies
3. **Generate test files** — Produce `test_{module}.py` with test functions
4. **Add fixtures/conftest** — Shared setup, teardown, parametrization
5. **Run** — User runs `pytest` to execute tests

## Context7 MCP

Use **Context7 MCP** for current pytest documentation when:
- Fixture scope or parametrize syntax is uncertain
- Plugin APIs (pytest-asyncio, pytest-cov) need verification
- Marker or configuration options require up-to-date reference

## Key Patterns

| Pattern | Usage |
| ------- | ----- |
| `test_` prefix | Test functions: `def test_something():` |
| `assert` | Plain assertions; no special API needed |
| Fixtures | `def fixture_name():` with scope, autouse, yield |
| `@pytest.mark.parametrize` | Data-driven tests |
| Markers | `@pytest.mark.skip`, `@pytest.mark.skipif`, `@pytest.mark.xfail` |
| conftest.py | Shared fixtures in package/directory |
| monkeypatch | Built-in for patching attributes/env |
| tmp_path | Built-in temporary directory fixture |
| unittest.mock | `patch`, `MagicMock` for mocking |

## Mocking

| Approach | Use Case |
| -------- | -------- |
| **unittest.mock.patch** | Patch modules, classes, functions |
| **unittest.mock.MagicMock** | Create mock objects with configurable behavior |
| **pytest-mock (mocker)** | `mocker` fixture wraps patch; cleaner syntax |
| **monkeypatch** | Built-in; patch attributes, env vars, sys.path |

## Configuration

- **pytest.ini** — Legacy config (markers, addopts, testpaths)
- **pyproject.toml** — Modern config under `[tool.pytest.ini_options]`
- **conftest.py** — Fixtures, hooks, plugin config

See `references/config.md` for configuration patterns.

## Plugin Recommendations

| Plugin | Purpose |
| ------ | ------- |
| pytest-cov | Code coverage reporting |
| pytest-xdist | Parallel test execution |
| pytest-asyncio | Async test support |
| pytest-html | HTML test reports |
| pytest-factoryboy | Factory fixtures for models |

## File Naming

- `test_{module}.py` — Preferred (e.g., `test_calculator.py`)
- Place in `tests/` or colocated with source per project convention

## Scope

**Can do (autonomous):**
- Generate pytest unit and integration tests from test case specs
- Add fixtures (function/class/module/session scope), conftest.py
- Use @pytest.mark.parametrize for data-driven tests
- Apply markers (skip, skipif, xfail, custom)
- Mock with patch, MagicMock, monkeypatch, pytest-mock
- Configure pytest.ini / pyproject.toml
- Call qa-diagram-generator for test flow diagrams if needed

**Cannot do (requires confirmation):**
- Change production code to satisfy tests
- Add tests for requirements not in source documents
- Override project-level pytest config without approval

**Will not do (out of scope):**
- Execute tests (user runs `pytest`)
- Write Playwright/Selenium E2E tests (use qa-playwright-ts-writer or Python E2E skills)
- Modify CI/CD pipelines

## References

- `references/patterns.md` — Fixtures, parametrize, conftest, async testing, mocking
- `references/assertions.md` — Assertion patterns: comparison, exceptions, warnings, approximate
- `references/config.md` — pyproject.toml, pytest.ini, conftest.py, markers, plugins
- `references/best-practices.md` — Fixture scope, naming, organization, test isolation, coverage

## Quality Checklist

- [ ] Tests match test case steps and expected results
- [ ] Fixtures are properly scoped (function vs session)
- [ ] No hardcoded secrets or sensitive data
- [ ] Assertions are specific (avoid only truthiness where value matters)
- [ ] Teardown via yield in fixtures where resources need cleanup
- [ ] File naming follows `test_{module}.py` convention
- [ ] Parametrize used for data-driven cases; markers for categorization
- [ ] Coverage targets considered if specified in requirements

## Troubleshooting

| Symptom | Likely Cause | Fix |
| ------- | ------------ | --- |
| Fixture not found | Scope or conftest location | Ensure conftest.py in same dir or parent; check fixture scope |
| Parametrize id collision | Duplicate ids | Use `ids` parameter for unique test names |
| Tests pass individually, fail together | Shared mutable state | Use function-scoped fixtures; avoid module/session for mutable data |
| monkeypatch not persisting | Wrong target path | Patch where object is used (e.g., `mymodule.func` not `builtins.func`) |
| Async tests fail | Missing pytest-asyncio | Add `@pytest.mark.asyncio`; install pytest-asyncio |
| Coverage not collected | Plugin not configured | Add pytest-cov; run `pytest --cov=src` |
| Import errors in tests | Path/sys.path | Add `conftest.py` with `sys.path` or use `pyproject.toml` pythonpath |
