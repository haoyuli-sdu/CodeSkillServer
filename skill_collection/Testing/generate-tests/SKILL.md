---
name: "generate-tests"
description: "Use when generating unit tests for existing code — analyzes source files, auto-detects the layer (domain/data/presentation), and creates appropriate tests with mocks"
---

# Generate Tests

Analyze existing code and generate appropriate unit tests.

## Trigger

User says: "write tests for", "generate tests", "add tests", or invokes `/generate-tests [path]`.

## Arguments

- `path` (optional): File or directory path. If omitted, ask the user.

## Quick Mode

When the user provides a path directly, skip prompts and generate tests immediately. Auto-detect the layer from file path and use default test patterns.

Example: `/generate-tests lib/features/auth/domain/usecases/login_user.dart` — generates test file without asking questions.

## Code Generation

All generated test code must include brief comments explaining the test structure for junior developers (what's being mocked, what's being tested, and why).

## Process

### Step 1: Detect Target

If path is a file: generate tests for that file.
If path is a directory: generate tests for all testable files in it.
If no path: ask "Which file or feature should I generate tests for?"

### Step 2: Analyze Source Code

Read the source file(s) and determine:

1. **Layer detection** (from file path):
   - `domain/usecases/` → Use Case test
   - `domain/entities/` → Skip (entities are simple data classes, rarely need tests)
   - `data/repositories/` → Repository implementation test
   - `data/models/` → Model serialization test
   - `data/datasources/` → Data source test
   - `presentation/cubit/` or `presentation/bloc/` → Cubit/BLoC test

2. **Dependencies** to mock (constructor parameters)
3. **Public methods** to test
4. **Return types** (Either → test Left and Right paths)

### Step 3: Generate Test File

**Test file location:** Mirror the source path under `test/`:
`lib/features/auth/domain/usecases/login_user.dart` → `test/features/auth/domain/usecases/login_user_test.dart`

**For Use Cases:**
- Mock the repository dependency
- Test: correct delegation to repository, correct parameter passing
- Test each method: success returns Right, failure returns Left
- Use `when()/thenAnswer()` pattern

**For Repository Implementations:**
- Mock the data source(s)
- Test success: data source returns data → maps to entity → returns Right
- Test failure: data source throws → returns Left with correct Failure

**For Cubits/BLoCs:**
- Mock the use case dependency
- Use `blocTest` from bloc_test package
- Test initial state
- For each public method: test [Loading, Success] and [Loading, Failure] sequences
- Use `tearDown(() => cubit.close())`

**For Models:**
- Test `fromJson` with sample JSON
- Test `toJson` produces expected map
- Test `toEntity` maps all fields correctly

### Step 4: Naming

Test descriptions follow: `should <expected behavior> when <condition>`

### Step 5: Report

List test files created. Run the tests: `flutter test <test_file>`. Report results.

## Rules Reference

- `rules/testing.md` — test types, AAA pattern, mocking, naming
- `rules/bloc.md` — cubit test patterns with blocTest
