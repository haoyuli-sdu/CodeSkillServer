---
name: "generate-tests"
description: "Generate comprehensive tests for FlowAPI code. Use when you need to write unit tests, integration tests, or test coverage for new or existing code."
---

# Generate Tests

Generate tests for: **$ARGUMENTS**

## Step 1: Understand the Test Infrastructure

Read these files first:

1. Read `tests/helpers/mock-registry.ts` — mock service registry used across tests
3. Read 2-3 existing test files similar to what you're testing (search in `tests/`)
4. Read the source code being tested thoroughly

## Step 2: Identify Test Type

| Type | Location | Pattern |
|------|----------|---------|
| Unit tests (nodes) | `tests/nodes/` | Test individual node handlers |
| Unit tests (services) | `tests/services/` | Test service classes |
| Unit tests (core) | `tests/core/` | Test core framework features |
| Middleware tests | `tests/middleware/` | Test middleware handlers |
| Security tests | `tests/security/` | Test auth, encryption, secrets |
| Integration tests | `tests/integration/` | Test component interactions |
| Plugin tests | `tests/plugin/` | Test plugin lifecycle and nodes |
| Workflow tests | `tests/workflow/` | Test workflow engine features |
| Expression tests | `tests/expression-arrays/` | Test expression engine |

## Step 3: Write the Tests

### Test File Naming
- File: `tests/<category>/<feature>.test.ts`
- Use descriptive test names that explain the expected behavior

### Test Patterns

**Pattern A: Manual test pattern (189 of 205 tests use this)**
```typescript
import { describe, test, expect } from 'bun:test';

// Direct imports from source (not dist)
import { createSomeNode } from '../../packages/nodes/src/...';

describe('SomeNode', () => {
  test('should do expected thing', () => {
    // Arrange
    const node = createSomeNode();
    const context = { state: {}, input: { params: {}, query: {}, body: {} } };
    const config = { target: 'result', value: 'test' };

    // Act
    const result = await node.execute(context, config);

    // Assert
    expect(result.state.result).toBe('test');
  });
});
```

**Pattern B: Using mock registry**
```typescript
import { createMockRegistry } from '../helpers/mock-registry';

const registry = createMockRegistry({
  // mock service implementations
});
const node = createSomeNode(registry);
```

### What to Test
1. **Happy path** — normal operation with valid inputs
2. **Edge cases** — empty inputs, null values, boundary conditions
3. **Error handling** — invalid config, missing dependencies, service failures
4. **Expression resolution** — `{{ }}` templates in config values
5. **State mutations** — verify context.state is updated correctly
6. **Config options** — test each config option individually

### Rules
- Import from source paths (`../../packages/X/src/...`), NOT from `@chimpanze/flowapi`
- Use `bun:test` imports (`describe`, `test`, `expect`)
- Do NOT use jest, mocha, or other test frameworks
- Mock external services (database, redis, HTTP) — don't make real calls
- Each test should be independent — no shared mutable state between tests
- Use descriptive test names: `should return user when valid ID provided`

## Step 4: Verify Tests Pass

Run the tests:
```bash
bun test
```

If only running specific tests:
```bash
bun test tests/<category>/<file>.test.ts
```

## Step 5: Check Coverage

Ensure you've covered:
- [ ] All public methods/functions
- [ ] All config options
- [ ] Error paths
- [ ] Edge cases
- [ ] Expression resolution (if applicable)
