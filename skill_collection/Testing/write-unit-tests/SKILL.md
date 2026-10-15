---
name: "write-unit-tests"
description: "Author unit tests through a prohibitions-and-procedure flow. Use when starting a new unit test, when asked \"should I test this?\", or when adding tests in a PR. Walks worth-existing → right-instrument → behavior-name → assertion-first → minimum-arrangement → red-then-green. Do not use for reviewing existing tests."
---

# Write Unit Tests

Prohibitions first; procedure second. Prohibitions are unconditional. See `TEST-SMELLS.md` for full diagnosis and repair on each.

## Prohibitions

If any appears in the test you are about to write, STOP and fix the production code or rescope.

1. **No mocking internal collaborators.** Extract a pure function; assert its return value.
2. **No real I/O.** Process memory only. Inject clocks, schedulers, randomness.
3. **No formula-derived expected values.** Hard-code from the spec or a worked example.
4. **No asserting a mock was called.** Assert outputs or observable state.
5. **No snapshot-only assertions.** Pair with an invariant or replace with explicit asserts.
6. **No more than three test doubles.** A fourth means the unit is the wrong scope.

## Procedure

### 1. Worth-existing?

Does the code make a decision **and** does being right matter?

- **Test:** money / dates / parsing / encoding / state machines / domain rules with edge cases / defect-prone history.
- **Skip:** getters, setters, DTOs, config, DI wiring, generated code, framework code, pure delegations, type-checker-proven properties, prototypes.

If skip: write no test.

### 2. Right-instrument?

| Real question | Right tool |
|---|---|
| Holds for *all* inputs in a class? | Property-based test |
| Matches another team's API? | Contract test |
| Orchestration of collaborators? | Integration test |
| Output stable across versions? | Approval + invariant |
| Survives load / latency / partial failure? | Chaos / canary |
| Type-system-provable? | Move to types |

If a non-unit instrument fits: take that path; write no unit test.

### 3. Name the behavior

One Given–When–Then sentence describing what the user, caller, or contract would notice. If the sentence reads "method X is called" or "the function exists": reshape the code or the scope.

### 4. Write the assertion first

Hard-code the expected value from the spec or worked example. The assertion references the public contract: return value or observable state.

### 5. Minimum arrangement

Add only the setup the assertion needs. Setup ≤ 10× the assertion. Inline values used once; extract a builder only when ≥2 tests share the shape.

### 6. Red then green

Break the production code intentionally; run the test; confirm it **fails**. Restore; run again; confirm it **passes**. A test that never failed proves nothing.
