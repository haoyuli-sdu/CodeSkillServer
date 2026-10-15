---
name: "generate-tests"
description: "Use when the user asks to generate, create, or write unit tests for Scala code. Analyzes the target code, produces a structured test case list for review, then generates test code. Supports Scala with ZIO Test (ZIOSpecDefault) and ScalaTest (AnyFunSpec), mockito-scala, and zio-mock."
---

# Generate Tests Skill

You will analyze Scala code and generate high-quality unit tests for a given target.

**Target to test:** $ARGUMENTS

## Quality Standards

- Take your time to analyze the code thoroughly before generating test cases.
- Quality is more important than speed — read all relevant source files and rules carefully.
- Do not skip any step in the workflow below. Every step exists for a reason.
- Do not take shortcuts with test data — read the actual classes to use correct constructors and fields.

---

## Instructions

### Step 1: Read Rules and Analyze Context

1. **Read the relevant rules** from `./rules/tests/` based on code type (see Rules Reference below)
2. **Read the target** source file/class/method
3. **Read dependencies**: Follow imports to read case classes, ADTs, custom exceptions, ZIO services, and other types referenced by the target (as specified in `code-context-analysis` rule)
4. **Check for existing tests**: Search for `{ClassName}Spec` or `{ClassName}Suite` in the test directory (as specified in `existing-test-awareness` rule)
   - If found, read fully — you will add missing tests to it, not create a new file
   - If not found, scan 2-3 neighboring test classes to learn project conventions
5. **Detect stack**: Check `build.sbt` to determine ZIO version, test framework (zio-test, ScalaTest, MUnit), and mocking library (mockito-scala, zio-mock)

### Step 2: Generate Test Cases

1. Analyze ALL code branches, including:
   - Success paths (happy path ZIO effects)
   - Error/defect paths (`ZIO.fail`, `ZIO.die`, custom ADT errors)
   - Validation logic
   - Private methods called by the target (via public API)
   - Authorization / access control logic (if present)
2. Apply the INCLUDE/EXCLUDE rules strictly
3. Output the list of test cases in the format below — do NOT generate test code yet

#### Test Case Output Format

```
## Test Cases for {ClassName}.{methodName}

### 1. {testMethodName}
- **Given:** {preconditions/input state}
- **When:** {action being tested}
- **Then:** {expected outcome}
- **Code branch:** {which code path this covers}

### 2. {testMethodName}
...
```

#### Naming Convention
Test method name format: `{testedMethod}_{givenState}_{expectedOutcome}`

Examples:
- `calculateTotal_validProducts_returnsSum`
- `calculateTotal_emptyList_failsWithInvalidInput`
- `getUser_unauthorized_returns401`

### Step 3: Ask for User Review

After outputting test cases, use the **AskUserQuestion tool** to ask:
```
Question: "Test cases are ready. Proceed with generating test code?"
Header: "Next step"
Options:
  - Label: "Yes, generate tests" / Description: "Proceed to generate test files from the test cases above"
  - Label: "No, let me review first" / Description: "Stop here so I can review and adjust the test cases"
```

- If user selects "Yes", proceed to Step 4
- If user selects "No", STOP and wait for further instructions

### Step 4: Generate Test Code

1. Determine code type and apply the matching rules:
   - **ZIO service / domain logic** → Apply `domain-service-rules.md` (use `ZIOSpecDefault`, `ZLayer.succeed`, zio-mock or mockito-scala)
   - **ZIO HTTP route / controller** → Apply `http-routes-rules.md` (use `Routes.run(Request(...))` directly)
   - **Pure Scala (no ZIO effects)** → Apply `domain-service-rules.md` with ScalaTest + mockito-scala patterns
   - **All Scala code** → Always apply `scala-test-template.md` and `argument-matching.md`
2. If an existing test class was found in Step 1, add new test methods to it (do not create a duplicate file)
3. Generate tests following all rules and the test cases from Step 2
4. Create or update the test file using the Write tool

### Step 5: Verify Compilation and Execution

1. Run compilation and fix any issues (max 5 attempts — see `compilation-verification.md`)
2. Run the generated test class to verify all tests pass (see `test-execution-verification.md`)
3. Fix any failing tests — do NOT modify production code
4. If a test cannot be fixed after 3 attempts, remove it and inform the user

---

## Troubleshooting

### Target file not found
If the specified target does not exist, inform the user with the exact path you searched and ask for clarification.

### Unsupported library
If the target uses a library without specific rules (e.g., Http4s, Cats Effect instead of ZIO), apply only the general rules and inform the user that library-specific conventions may need manual review.

### Compilation keeps failing
If compilation fails after 5 attempts:
1. Stop and show the user the remaining errors
2. Suggest possible causes (missing dependencies, version mismatch between Scala 2/3, missing implicits)
3. Ask the user to resolve the build issue before continuing

### Tests fail due to production code behavior
If tests fail because the production code behaves differently than expected:
1. Do NOT modify production code
2. Fix the test to match actual behavior
3. If the behavior seems like a bug, add a comment: `// NOTE: current behavior may be a bug — {description}`

---

## Example

```
User says: "/generate-tests src/main/scala/com/example/service/OrderService.scala"

Step 1: Agent reads rules, reads OrderService.scala, reads Order.scala,
        OrderRequest.scala, OrderRepository.scala (dependencies), checks
        for existing OrderServiceSpec.scala. Detects ZIO + zio-test in build.sbt.

Step 2: Agent outputs 7 test cases covering:
        - createOrder success path
        - createOrder with invalid request (validation)
        - processPayment success
        - processPayment failure (ZIO.fail)
        - calculateTotal with products
        - calculateTotal with empty list
        - cancelOrder for non-existent order

Step 3: Agent asks user to review. User says "Yes, generate tests".

Step 4: Agent generates OrderServiceSpec.scala extending ZIOSpecDefault,
        with ZLayer test doubles, 7 test cases using assertTrue / assertZIO.

Step 5: Agent runs `sbt "testOnly *OrderServiceSpec"`, all tests pass.

Result: Complete test file delivered with 7 passing tests.
```

---

## Rules Reference

**CRITICAL: You MUST read and apply all relevant rules from the `./rules/tests/` directory.**

> **Maintenance note:** General rules in `./rules/tests/general/` are shared with the `generate-test-cases` skill (which has copies in `rules/general/`). When updating rules, keep both locations in sync.

### General Rules (Always Apply)
- `general/test-case-generation-strategy.md` - INCLUDE/EXCLUDE criteria
- `general/naming-conventions.md` - Test naming format
- `general/general-principles.md` - Core testing principles (Given-When-Then, actual/expected)
- `general/technology-stack-detection.md` - Detect language and framework
- `general/what-makes-good-test.md` - Clarity, Completeness, Conciseness, Resilience
- `general/cleanly-create-test-data.md` - Use helpers and builders for test data
- `general/keep-cause-effect-clear.md` - Effects follow causes immediately
- `general/no-logic-in-tests.md` - KISS > DRY, avoid logic in assertions
- `general/keep-tests-focused.md` - One scenario per test
- `general/test-behaviors-not-methods.md` - Separate tests for behaviors
- `general/verify-relevant-arguments-only.md` - Only verify relevant mock arguments
- `general/prefer-public-apis.md` - Test public APIs over private methods
- `general/existing-test-awareness.md` - Check for existing tests, match project conventions
- `general/code-context-analysis.md` - Read dependencies before writing tests

### Scala Unit Tests
- `scala/unit/scala-test-template.md` - Basic template, ZIO Test vs ScalaTest, FORBIDDEN patterns
- `scala/unit/argument-matching.md` - ArgumentCaptor in mockito-scala, zio-mock verification
- `scala/unit/domain-service-rules.md` - ZIO Test / mockito-scala patterns for services
- `scala/unit/http-routes-rules.md` - ZIO HTTP route testing patterns
- `scala/unit/zio-test-rules.md` - ZIO-specific: TestClock, TestRandom, assertZIO, ZLayer
- `scala/unit/logging-rules.md` - Log capture with TestConsole / logback ListAppender

### Post-Generation
- `post-generation/compilation-verification.md` - Verify compilation with sbt
- `post-generation/test-execution-verification.md` - Verify tests pass
