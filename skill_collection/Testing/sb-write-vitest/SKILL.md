---
name: "sb-write-vitest"
description: "Write modern Vitest unit tests for code that already exists. Use when the user wants to add unit tests, backfill coverage, or test a function/module/component that wasn't built test-first. Tests live beside the source file using `*.test.*` (never `*.spec.*` — `.spec.` is reserved for integration/e2e). Skip this skill and use `tdd` instead when the user is doing test-first development."
---

# Write Vitest Unit Tests

For code that already exists. If the user is writing tests *before* the implementation, stop and use the [`tdd`](../tdd/SKILL.md) skill instead — this skill is for backfilling.

## File conventions

- One test file per source file, **beside** the source: `src/cart.ts` → `src/cart.test.ts`.
- Use `*.test.*`, never `*.spec.*`. In this project `.spec.` is reserved for integration/e2e tests.
- Mirror the source extension: `.ts` → `.test.ts`, `.tsx` → `.test.tsx`.
- One `describe` per exported symbol; nest `describe` for sub-cases when it improves readability.

## Modern Vitest standards

- **Explicit imports, not globals.** `import { describe, it, expect, vi, beforeEach } from 'vitest'`. Don't rely on `globals: true` — explicit imports type-check cleanly and tree-shake.
- **`vi` namespace** replaces `jest`: `vi.fn()`, `vi.spyOn()`, `vi.mock()`, `vi.useFakeTimers()`.
- **Type-safe mocks** via `vi.mocked(fn)` — preserves the function's argument and return types after mocking.
- **`vi.mock()` is hoisted.** Put it at the top of the file. If a factory needs a value defined in the test file, wrap that value in `vi.hoisted(() => ...)`.
- **Parameterized cases** with `it.each([...])(...)` instead of copy-pasting `it` blocks.
- **Async readiness** — prefer `await expect.poll(() => state).toBe(...)` over hand-rolled `setTimeout` waits.
- **Soft assertions** — only use `expect.soft(...)` when you genuinely want to keep asserting after a failure.
- **Fresh state per test.** Use `beforeEach` for setup; never share mutable state between tests. Set `restoreMocks: true` in `vitest.config` (or call `vi.restoreAllMocks()` in `afterEach`) so spies don't bleed.
- `it` and `test` are aliases — pick one and stay consistent. This skill uses `it` because BDD-style names read better ("it returns null when…").

## Workflow

1. **Read the source** under test plus its types and direct dependencies.
2. **Identify the public interface** — exported functions, classes, hooks, or components. That's what tests should call into.
3. **List the behaviors worth testing**: happy path, edge cases (empty, null, boundary), error paths, async timing. Aim to describe what the module *does*, not chase line coverage.
4. **Confirm the behavior list with the user before writing tests.** Ask which behaviors matter most and whether any can be skipped.
5. **Write tests one behavior at a time.** Run `vitest run path/to/foo.test.ts` after each, confirm green, move on.
6. **Run the full file at the end** and verify there are no type errors.

## Test quality

- **Test behavior, not implementation.** The test should survive an internal refactor that preserves observable behavior.
- **Don't mock internal collaborators.** Mock only at the boundary: network, filesystem, time, third-party SDKs. If you find yourself mocking another module from your own codebase, the test is probably testing the wrong layer.
- **AAA structure** — Arrange, Act, Assert. Blank line between sections.
- **One concept per test.** If the test name needs "and", split it.
- **Test names describe behavior** — `it('returns null when the cart is empty')`, not `it('handles edge case')` or `it('works')`.

## Minimal example

```ts
// src/cart.ts
export function totalCents(items: { priceCents: number; qty: number }[]) {
  return items.reduce((sum, i) => sum + i.priceCents * i.qty, 0);
}
```

```ts
// src/cart.test.ts
import { describe, expect, it } from 'vitest';
import { totalCents } from './cart';

describe('totalCents', () => {
  it('returns 0 for an empty cart', () => {
    expect(totalCents([])).toBe(0);
  });

  it.each([
    { items: [{ priceCents: 500, qty: 1 }], expected: 500 },
    { items: [{ priceCents: 250, qty: 4 }], expected: 1000 },
  ])('multiplies price by qty ($expected cents)', ({ items, expected }) => {
    expect(totalCents(items)).toBe(expected);
  });
});
```

See [PATTERNS.md](PATTERNS.md) for mocking modules, spies, fake timers, async polling, error assertions, and React Testing Library.
