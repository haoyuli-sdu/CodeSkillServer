---
name: "write-unit-tests"
description: "Proactively apply when writing or reviewing unit tests. Triggers on unit test, TDD, AAA, test doubles, mocks, fakes, test smells, and DSL-driven testing. Use when adding tests, fixing brittle suites, or guiding agents toward maintainable, refactor-safe tests. Prefer a business DSL by default for new code, with brownfield pragmatism when migration cost is too high."
---

# Write Unit Tests

Write unit tests that catch regressions, stay fast, and survive refactoring. For new code, default to **DSL-driven testing** with an in-memory or domain-level driver, then apply classic-style unit-test rules inside that structure. Fall back to more direct tests mainly in brownfield areas where introducing a DSL would create too much churn for too little payoff.

In this skill, **classic style** means the **Chicago school**: prefer observable outcomes over interaction-heavy verification.

## Default Stance

For **new code**, write unit tests this way:

1. **Business-facing test case or scenario**
2. **Small business DSL that expresses domain intent**
3. **Fast in-memory/domain driver beneath it**
4. **Classic-style assertions on observable outcomes**

This is intentionally aligned with [`dsl-driven-testing`](../dsl-driven-testing/SKILL.md), which should be the default testing architecture by a wide margin.

### Main exception

Use a more direct style mainly in **brownfield** code when all of these are true:

- introducing the DSL would force broad rewrites,
- team adoption cost is high,
- and the near-term payoff is not worth the disruption.

Even in brownfield code, prefer **incremental DSL adoption** around new work, painful tests, and flaky areas rather than copying the old style forever.

## When to Use (and When NOT to)

| Use When | Skip When |
|----------|-----------|
| Adding tests for business logic in new or evolving code | Verifying full system wiring across processes |
| Expressing scenarios in business language with a DSL | Needing confidence in DB/network/framework integration |
| Protecting complex branches or edge cases | Writing broad end-to-end scenarios |
| Replacing brittle mock-heavy tests | Testing trivial getters/setters with no real risk |
| Reviewing AI-generated or over-mocked tests | Brownfield areas where DSL migration cost clearly outweighs the benefit right now |

**Goal:** maximize regression protection **without** coupling tests to implementation details.

## Core Defaults

1. **Default to DSL-driven testing for new code.** Prefer business-language scenarios over framework-shaped tests.
2. **Inside that DSL, prefer classic-style (Chicago school) tests.** Test observable behavior, not internal choreography.
3. **Use a fast in-memory or domain driver first.** Multiple drivers are optional, not required.
4. **Use real in-memory collaborators when they are deterministic and fast.**
5. **Prefer fakes over mocks** for external boundaries you must isolate.
6. **Use mocks only as a last resort** for outbound commands/side effects you cannot observe otherwise.
7. **Structure every test with Arrange, Act, Assert**, even when the scenario is wrapped in a business-language layer.
8. **Treat coverage as a diagnostic, not the goal.**

## Quick Decision Trees

### "What should I unit test first?"

```
What has the highest payoff?
├─ Important business behavior in new code    → Start with a small business DSL
├─ Complex business rules or branching     → Test first
├─ Code with frequent regressions          → Test first
├─ Public behavior used by many callers    → Test first
├─ Simple pass-through glue                → Lower priority
└─ Trivial code with no real risk          → Maybe skip
```

### "Should I write the test directly or via a DSL?"

```
What context am I in?
├─ New feature or greenfield area            → Use a DSL by default
├─ Long-lived test suite                     → Use a DSL by default
├─ Need scenarios to read like specifications → Use a DSL by default
├─ Brownfield code, high migration cost      → Be pragmatic; direct tests may be fine
└─ Tiny trivial logic with no useful language → Direct test is acceptable
```

### "Should I use a real dependency, fake, or mock?"

```
What kind of dependency is it?
├─ Pure, deterministic, in-memory          → Use the real dependency
├─ External but easy to model in memory    → Use a fake
├─ Need canned answers only                → Use a stub
├─ Need to observe calls after execution   → Use a spy
└─ Need strict interaction verification     → Mock as last resort
```

### "What kind of assertion should I write?"

```
What do I care about?
├─ Final state / returned value            → State assertion
├─ Error condition or boundary case        → Exception / error assertion
├─ Side effect recorded in fake/spy        → Verify observable effect
└─ Internal call order or private methods  → Usually don't test that
```

### "Why is this test fragile?"

```
Why does it break too often?
├─ Fails after harmless refactor           → Coupled to implementation
├─ Mocks every collaborator                → Over-mocked, too isolated
├─ Huge setup hides the intent             → Obscure Arrange phase
├─ Many unrelated assertions               → Assertion Roulette
└─ Depends on clock, DB, file system       → Not a true unit test
```

## The Unit-Test Workflow

1. **Pick one behavior** with business value.
2. **Name it in business language first.** Create a small business DSL before writing low-level test code.
3. **Choose the smallest meaningful scope** that still exercises real logic.
4. **Use a fast in-memory or domain driver** as the default execution path.
5. **Keep collaborators real** if they are fast, deterministic, and in-memory.
6. **Replace only unstable boundaries** with a fake, stub, spy, or rare mock.
7. **Write one clear Act step.**
8. **Assert on outcomes visible to the caller or domain.**
9. **Refactor the test for readability** without changing intent.
10. **Check for smells** before adding more tests.

## DSL-First Unit Testing

When the code is new or expected to live a long time, prefer this stack:

```text
Test case / scenario → small business DSL → in-memory driver → system under test
```

Why this should be the default:

- scenarios read like executable specifications,
- tests stay decoupled from HTTP/UI/framework details,
- the same language can often scale beyond unit level later,
- and teams avoid locking their test suite to implementation noise.

If you need the full architecture and migration guidance, use [`dsl-driven-testing`](../dsl-driven-testing/SKILL.md) together with this skill.

## AAA / Four-Phase Structure

```text
Arrange → Act → Assert → (Optional) Teardown
```

- **Arrange:** only the data and collaborators needed for this scenario
- **Act:** ideally one triggering call
- **Assert:** verify the business-relevant outcome
- **Teardown:** only when a shared resource truly needs cleanup

## Test Double Selection

| Double | Use It For | Avoid When |
|--------|------------|------------|
| **Dummy** | Satisfying an unused parameter | You need real behavior |
| **Stub** | Returning fixed answers | You need to inspect effects |
| **Spy** | Recording calls or emitted messages | You want strict pre-programmed expectations |
| **Mock** | Rare verification of unavoidable outbound commands | You are testing queries, internal calls, or domain collaboration |
| **Fake** | Lightweight in-memory implementation of an external contract | The fake would become more complex than the real thing |

**Default order:** real dependency → fake → stub/spy → mock.

## Example Guidance

- Prefer **DSL-first tests** in new code: test case → small business DSL → in-memory driver → SUT.
- Prefer **observable outcomes** over interaction verification.
- Keep **one Act step** per scenario.
- Treat **coverage as a clue**, not proof of quality.

For worked examples, see:

- [examples/SERVICE-EXAMPLE.md](examples/SERVICE-EXAMPLE.md)
- [../dsl-driven-testing/SKILL.md](../dsl-driven-testing/SKILL.md)

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Over-mocking** | Tests freeze internal design and break on refactors | Replace mocks with real collaborators or fakes |
| **Assertion Roulette** | Hard to know why the test failed | Use fewer, sharper assertions with clear intent |
| **Obscure Test** | Setup overwhelms the scenario | Use builders/helpers and remove irrelevant setup |
| **Conjoined Twins** | Hidden shared state makes tests flaky | Isolate state and keep everything in-memory |
| **No real assertion** | Coverage rises but confidence does not | Assert outcomes that matter |
| **Testing private methods** | Locks tests to implementation details | Test through public behavior |
| **Multiple behaviors in one test** | Failures are ambiguous | Split into one scenario per test |
| **Skipping a useful DSL in new code** | Tests speak framework details instead of business intent | Add a small scenario/DSL layer first |

## The Four Quality Pillars

Evaluate each test against these four properties:

| Pillar | Ask |
|--------|-----|
| **Regression protection** | Would this catch a real bug? |
| **Resistance to refactoring** | Will this stay green after harmless internal changes? |
| **Fast feedback** | Will developers run it constantly? |
| **Maintainability** | Can another developer understand and update it easily? |

If a test scores poorly on **refactoring resistance**, redesign it before adding more assertions.

## Review Checklist

- Does the test describe a business-relevant behavior?
- In new code, should this be expressed through a small business DSL first?
- Is the Act phase a single meaningful trigger?
- Are assertions about outcomes instead of internals?
- Could a real in-memory dependency replace a mock?
- Would the test survive a harmless refactor?
- Is the setup shorter than the behavior being tested?
- Is the test deterministic and fast locally?
- Does it avoid using coverage as the definition of quality?

## AI-Specific Guidance

Coding agents often generate too many mocks. When writing tests with AI assistance:

1. **Explicitly ask for DSL-driven tests in new code.**
2. **Ask for a small business DSL first, then a fast in-memory driver.**
3. **State “prefer classic-style assertions and fakes over mocks.”**
4. **Forbid verification of private calls or call order unless strictly necessary.**
5. **Require AAA layout and one behavior per test.**
6. **Ask the agent to explain why each test double is needed and why a DSL was or was not introduced.**

## Reference Documentation

| File | Purpose |
|------|---------|
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Quick checklist for daily use |
| [references/TEST-DOUBLES.md](references/TEST-DOUBLES.md) | Choosing between real deps, fakes, spies, and mocks |
| [examples/SERVICE-EXAMPLE.md](examples/SERVICE-EXAMPLE.md) | Example of a DSL-first, classic-style unit test |
| [../dsl-driven-testing/SKILL.md](../dsl-driven-testing/SKILL.md) | Default test architecture for long-lived code |

## Sources

### Primary Source
- User-provided literature review on unit testing — local reference used to synthesize the guidance in this skill

### Key Authors and Concepts Reflected
- Gerard Meszaros — *xUnit Test Patterns* (AAA / Four-Phase, test doubles, test smells)
- Vladimir Khorikov — *Unit Testing: Principles, Practices, and Patterns* (four quality pillars, classic style, refactoring resistance)
- Martin Fowler — test doubles taxonomy and mocking guidance
- Empirical findings summarized in the review: TDD/testing improves quality, excessive mocking increases fragility, and code coverage is useful as a signal but weak as a target
