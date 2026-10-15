---
name: "php-test"
description: "Generate PHPUnit and Pest tests for PHP/Laravel classes"
---

# Generate PHP Tests

Generate PHPUnit or Pest tests for the given PHP/Laravel class or file.

## What To Do

1. **Read the target file** to understand public methods, dependencies, and validation rules
2. **Generate test class** in the correct tests/ subdirectory
3. **Create factory or test data** using Laravel factories
4. **Write test methods** following Arrange-Act-Assert
5. **Cover edge cases**: null values, empty inputs, boundary values, unauthorized access

## Test Types

### Unit Test (default)
- Extend TestCase (not Laravel TestCase — no framework boot)
- Use PHPUnit MockObject or Mockery for dependencies
- No database, no HTTP

### Feature Test (--type=feature)
- Extend Laravel's TestCase with RefreshDatabase
- Test service class behavior with real database via factories

### HTTP Test (--type=http)
- actingAs($user) for authenticated requests
- getJson(), postJson(), putJson(), deleteJson()
- assertStatus, assertJson, assertDatabaseHas

### Database Test (--type=database)
- Test Eloquent scopes, relations, and query results
- assertDatabaseHas / assertDatabaseMissing

## Arguments
- `<class-or-file>`: Target class name or file path
- `--type=<unit|feature|http|database>`: Test type (default: unit)
- `--pest`: Generate Pest syntax instead of PHPUnit
