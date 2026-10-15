---
name: "generate-jest-tests"
description: "Analyze project code and recent changes to generate high-quality Jest unit tests that increase test coverage and follow existing project testing patterns."
---

# Jest Unit Test Generator

## Purpose

This skill analyzes project code and recent repository changes to generate **Jest unit tests** that:

- increase test coverage
- validate new features
- protect against regressions
- follow existing testing conventions

The skill generates **production-quality unit tests** compatible with the project’s existing Jest setup.

---

# When To Use This Skill

Use this skill when:

- new features were implemented
- functions or modules changed
- components were added
- refactoring occurred
- test coverage dropped
- a pull request requires tests

Typical triggers:

- generate jest tests
- add unit tests
- write tests for modified files
- improve test coverage
- generate tests for new modules

---

# Step 1 — Detect Test Environment

Identify testing stack used in the project.

Inspect:

package.json

Look for dependencies:

```

jest
ts-jest
@testing-library/react
@testing-library/jest-dom
vitest
babel-jest

```

Detect configuration:

```

jest.config.js
jest.config.ts
vitest.config.ts

```

Determine:

- test framework (Jest)
- TypeScript support
- React testing library usage
- module alias configuration

---

# Step 2 — Detect Changed Code

Identify files needing tests.

Run:

```

git diff --name-only HEAD

```

or:

```

git diff --name-only origin/main

```

Focus on:

```

src/
components/
hooks/
utils/
services/
api/
lib/

```

Ignore:

```

*.test.ts
*.spec.ts
*.stories.tsx

```

Prioritize **new or modified files**.

---

# Step 3 — Identify Test Targets

Extract testable units:

Functions
Hooks
Services
API utilities
React components

Example detection:

```

src/utils/priceFormatter.ts
src/hooks/useCart.ts
src/components/ProductCard.tsx
src/services/wishlistService.ts

```

Each should receive **dedicated unit tests**.

---

# Step 4 — Detect Existing Test Patterns

Analyze existing test files:

```

*.test.ts
*.test.tsx
*.spec.ts

```

Extract conventions:

- test file naming
- folder placement
- mocking strategy
- use of testing-library
- snapshot usage
- jest setup imports

Generated tests must **follow the same conventions**.

---

# Step 5 — Coverage-Aware Test Planning

Identify missing test coverage.

If coverage tools exist:

```

coverage/

```

Focus on:

- untested functions
- untested branches
- edge cases
- error handling

Generate tests that increase **branch and statement coverage**.

---

# Step 6 — Generate Unit Tests

Generate tests that cover:

### Functional Behavior

Test core logic.

Example:

```

expect(formatPrice(10)).toBe("$10.00")

```

---

### Edge Cases

Test unusual inputs.

Examples:

```

null
undefined
empty arrays
large numbers

```

---

### Error Handling

Ensure functions fail safely.

Example:

```

expect(() => parsePrice(null)).toThrow()

```

---

### Conditional Branches

Test all logical branches.

Example:

```

if (user.isAdmin)
else

```

---

# Step 7 — React Component Tests

If React components are detected:

Use **React Testing Library**.

Validate:

- rendering
- props behavior
- user interactions
- accessibility

Example:

```

render(<ProductCard product={mockProduct} />)

expect(screen.getByText("Product Name")).toBeInTheDocument()

```

Test interactions:

```

fireEvent.click(button)

```

---

# Step 8 — Mock External Dependencies

Mock external modules when needed.

Examples:

```

jest.mock("next/router")
jest.mock("axios")
jest.mock("../services/api")

```

Ensure tests remain **isolated**.

---

# Step 9 — API & Service Tests

Test service layers.

Validate:

- request generation
- response handling
- error handling

Example:

```

jest.spyOn(api, "get").mockResolvedValue(mockResponse)

```

---

# Step 10 — Hook Tests

If hooks exist:

Use:

```

@testing-library/react-hooks

```

or React Testing Library.

Example:

```

const { result } = renderHook(() => useCart())

expect(result.current.items.length).toBe(0)

```

---

# Step 11 — File Placement

Follow existing structure.

Example:

```

src/utils/priceFormatter.ts
src/utils/**tests**/priceFormatter.test.ts

```

or:

```

src/utils/priceFormatter.test.ts

```

Use the same pattern used in the repository.

---

# Step 12 — Test Naming Conventions

Follow consistent naming:

```

describe("priceFormatter", () => {

it("formats integer prices correctly")

it("handles decimal values")

it("throws error on invalid input")

})

```

Prefer **behavior-based descriptions**.

---

# Step 13 — Snapshot Tests (Optional)

For UI components:

```

expect(container).toMatchSnapshot()

```

Use snapshots only if project already uses them.

---

# Step 14 — Validate Generated Tests

Ensure tests:

- compile successfully
- follow TypeScript types
- avoid flaky behavior
- mock external dependencies
- remain deterministic

---

# Output Format

Return tests grouped by file.

Example:

---

# Generated Test Files

### File

src/utils/priceFormatter.test.ts

```ts
import { formatPrice } from "../priceFormatter";

describe("formatPrice", () => {
  it("formats integer prices correctly", () => {
    expect(formatPrice(10)).toBe("$10.00");
  });

  it("formats decimal prices correctly", () => {
    expect(formatPrice(10.5)).toBe("$10.50");
  });

  it("throws error on invalid input", () => {
    expect(() => formatPrice(null)).toThrow();
  });
});
```

---

# Coverage Improvements

Estimated improvements:

| File               | Coverage Gain |
| ------------------ | ------------- |
| priceFormatter.ts  | +35%          |
| wishlistService.ts | +28%          |

---

# Test Strategy Summary

Explain what behaviors are validated.

Example:

- formatting logic
- error handling
- edge cases
- input validation

---

# Example Commands

Generate tests for modified files:

```
/generate-jest-tests based on git diff
```

Generate tests for a module:

```
/generate-jest-tests for src/utils/priceFormatter.ts
```

Improve test coverage:

```
/generate-jest-tests improve coverage
```

Generate tests for new feature:

```
/generate-jest-tests for new wishlist feature
```

---

# Best Practices

Tests must:

- validate behavior, not implementation
- avoid brittle snapshots
- mock external dependencies
- cover edge cases
- follow project conventions
- remain readable and maintainable

Avoid:

- testing private implementation details
- duplicating production logic inside tests
