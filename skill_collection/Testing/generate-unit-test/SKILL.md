---
name: "generate-unit-test"
description: "Generate unit tests for new features. Use when: writing tests, unit test, test coverage, test cases, testing new feature, jest, vitest."
---

# Generate Unit Tests

Generates well-structured unit tests for new features by understanding the code, analyzing integration points with existing functionality, and matching the project's existing test style.

## When to Use

- A new feature, function, hook, or component was just implemented
- You want test coverage for a specific file or module
- You want to ensure new code doesn't break existing behavior

## Procedure

### 1. Identify What to Test

Accept input from the user in any of these forms:

- A file path (e.g. `lib/blog.ts`)
- A feature name or description
- A spec document (e.g. `features/<name>/index.md`)
- Code pasted directly into the chat

If the input is a file path or feature name, read the relevant source file(s) before proceeding.

### 2. Audit the Existing Test Setup

Before writing a single test, check what's already there:

```bash
# Look for test config files
ls *.config.* jest.config* vitest.config* playwright.config*

# Look for existing test files
find . -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.spec.ts" -o -name "*.spec.tsx" | grep -v node_modules | head -20
```

Check `package.json` for test-related dependencies:

- `jest`, `@testing-library/react`, `@testing-library/jest-dom` → Jest + RTL setup
- `vitest`, `@testing-library/react` → Vitest + RTL setup
- Neither → must install (see Step 2b)

**If tests already exist:** read 1–2 existing test files to understand:

- Import style and file naming conventions
- How components are rendered (e.g. `render()`, `renderWithProviders()`)
- How async is handled (`waitFor`, `act`, MSW mocks, etc.)
- Assertion style (`expect(...).toBe`, `toBeInTheDocument`, etc.)

**2b. If no test framework exists:** recommend and install Vitest + Testing Library (preferred for Next.js App Router):

```bash
pnpm add -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom jsdom
```

Create a minimal `vitest.config.ts`:

```ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    globals: true,
  },
});
```

Create `vitest.setup.ts`:

```ts
import "@testing-library/jest-dom";
```

### 3. Analyze the Feature

Read the target source file(s) and identify testable units:

| Unit type           | What to test                                            |
| ------------------- | ------------------------------------------------------- |
| Pure function       | All input/output combinations, edge cases, error cases  |
| Custom hook         | State transitions, side effects, cleanup                |
| Server Component    | Rendered output with mocked data, loading/error states  |
| Client Component    | User interactions, conditional rendering, form behavior |
| API / Server Action | Input validation, success response, error response      |

Also identify **integration points**: does this feature call or depend on other existing modules? If so, note which ones need to be mocked vs. exercised for real.

### 4. Think Through Integration

For each dependency the new feature has, decide:

- **Mock it** — external APIs, database calls, `fetch`, Next.js router, auth session
- **Use real implementation** — pure utility functions from the same codebase that are already tested

Document your decision briefly as a comment at the top of the test file.

### 5. Build the Test Cases

For each testable unit, define test cases before writing code:

```
describe('<FunctionOrComponentName>')
  ✓ happy path — expected behavior with valid input
  ✓ edge case — empty input / zero / null / undefined
  ✓ error case — invalid input or failed dependency
  ✓ [component] renders correctly in loading state
  ✓ [component] renders correctly in error state
  ✓ [component] user interaction triggers expected outcome
```

### 6. Implement the Tests

Write the tests following the project's existing conventions (or the Vitest + RTL defaults if newly installed).

**File placement:** co-locate test files with source:

- `lib/blog.ts` → `lib/blog.test.ts`
- `components/Navbar.tsx` → `components/Navbar.test.tsx`

**Structure template:**

```ts
/**
 * @file blog.test.ts
 * @description Unit tests for blog.ts — markdown parsing and metadata extraction.
 * Mocks: none (all functions are pure).
 */
import { describe, it, expect, vi } from "vitest";
import { parseBlogMeta } from "./blog";

describe("parseBlogMeta", () => {
  it("extracts title and date from frontmatter", () => {
    const input = `---\ntitle: Hello\ndate: 2026-01-01\n---\nBody`;
    expect(parseBlogMeta(input)).toEqual({
      title: "Hello",
      date: "2026-01-01",
    });
  });

  it("returns null for missing frontmatter", () => {
    expect(parseBlogMeta("No frontmatter here")).toBeNull();
  });
});
```

### 7. Run and Verify

```bash
pnpm test        # or: pnpm vitest run
```

If tests fail:

1. Read the error message carefully.
2. Fix the test logic (not the source) if the source behavior is correct.
3. Fix the source if the test reveals a real bug.
4. Re-run until all pass.

Report the final test results to the user.
