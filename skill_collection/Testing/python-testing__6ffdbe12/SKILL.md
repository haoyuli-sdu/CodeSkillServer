---
name: "python-testing"
description: "Generate pytest tests with parametrization, shared fixtures, minimal mocking. Use for unit tests and test coverage. Follows 1-1 file mapping and real object testing."
---

# Python Testing Skill

Generate pytest tests following project best practices.

## Core Principles

1. **Minimal Mocking**: Only mock external dependencies (APIs, DBs, file I/O)
2. **Parametrization**: Use `@pytest.mark.parametrize` for multiple cases
3. **Shared Fixtures**: Place reusable fixtures in `tests/conftest.py`
4. **1-1 Correspondence**: `src/module.py` → `tests/test_module.py`

## Instructions

1. **Analyze**: Read module to understand functions, dependencies, edge cases
2. **Check conftest.py**: Identify existing fixtures, plan new ones
3. **Mock Only**: External HTTP, DB, file I/O, system calls, time
4. **Write Tests**: Arrange-Act-Assert pattern, clear names
5. **Update conftest.py**: Add reusable fixtures

## Test Structure

```python
"""Tests for module_name (src/module.py)"""
import pytest

class TestClassName:
    """Test ClassName functionality"""

    def test_happy_path(self, fixture):
        """Test normal operation"""
        # Arrange, Act, Assert

    @pytest.mark.parametrize("input,expected", [...])
    def test_variations(self, input, expected):
        """Test multiple inputs"""

    def test_error_handling(self):
        """Test exception cases"""
        with pytest.raises(ExpectedException):
            ...
```

## Checklist

- [ ] All public methods tested
- [ ] Edge cases (None, 0, empty, max)
- [ ] Error conditions raise expected exceptions
- [ ] Similar tests parametrized
- [ ] Reusable fixtures in conftest.py
- [ ] Mocking limited to external deps only
