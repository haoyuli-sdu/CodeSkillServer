---
name: "legacy-rewrite"
description: "Safely modernize legacy code while preserving behavior"
---

# Legacy Rewrite

## When to Use

Use this skill when:
- Modernizing old Python code (e.g., Python 2 patterns, outdated stdlib usage)
- Replacing deprecated APIs or libraries
- Restructuring code to match current project conventions

## Inputs

- Target file or directory to modernize
- Specific modernization goals (optional)

## Steps

1. **Assess current state:**
   - Read the target code
   - Identify Python version and dependencies
   - Note existing tests for the target code

2. **Ensure test coverage:**
   - Check if tests exist for the code being changed
   - If tests are missing, STOP and write tests first
   - Run existing tests to confirm they pass

3. **Plan changes:**
   - List specific modernizations (e.g., f-strings, pathlib, type hints)
   - Identify risk areas (behavior changes, API differences)
   - Plan changes in small, independent steps

4. **Apply changes incrementally:**
   - Make one category of change at a time
   - Run tests after each change
   - Commit after each passing step

5. **Verify:**
   - All tests still pass
   - No new warnings from linter
   - Behavior is preserved

## Output Format

```
## Legacy Rewrite Report

### Target
file_or_directory

### Changes Made
1. Replaced os.path with pathlib (5 files)
2. Added type hints to public functions (3 files)
3. Replaced .format() with f-strings (12 occurrences)

### Tests
- Before: 15 passing
- After: 15 passing

### Risks
- None identified / List any behavior changes
```

## Safety Notes

- NEVER rewrite code without tests. Write tests first.
- NEVER combine modernization with feature changes.
- If a refactor changes behavior, stop and confirm with the operator.
- Commit after each successful step so changes can be reverted individually.
