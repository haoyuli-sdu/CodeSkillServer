---
name: "write-unit-tests"
description: "Generate xUnit unit tests for a given class or file following the project's test conventions (AAA pattern, NSubstitute, constructor injection)."
---

# Write Unit Tests

Generate xUnit unit tests for the specified class or file, following the conventions used across this project.

## Instructions

### Step 1 — Read the source

Read the file or class the user wants to test. Understand its public API, dependencies, and behaviours.

If no target is specified, ask the user which class or file to test.

### Step 2 — Locate the test project

Find the corresponding test project under `libs/<Domain>/<Library>.Tests/`. Mirror the source folder structure inside the test project (e.g. source at `libs/Core/Shared.Core/Domain/Foo.cs` → test at `libs/Core/Shared.Core.Tests/Domain/FooTests.cs`).

If the test project does not exist yet, inform the user before creating any files.

### Step 3 — Write the tests

Apply **all** conventions below when generating the test file.

#### Conventions

**Framework & packages**
- xUnit (`[Fact]`) — no `[Theory]` unless the user explicitly asks for parameterised tests
- NSubstitute for mocking (`Substitute.For<T>()`)
- No FluentAssertions; use xUnit's `Assert.*` methods only

**Naming**
- Test class: `{SubjectUnderTest}Tests`
- Method: `{MethodOrProperty}_When{Condition}_Should{ExpectedOutcome}`
- For simple "no condition" cases the `_When…` segment may be omitted (e.g. `Constructor_WhenCalled_ShouldInitializeWithEmptyDomainEvents`)

**Structure — Arrange / Act / Assert**
```csharp
[Fact]
public void MethodName_WhenCondition_ShouldOutcome()
{
    // Arrange
    ...

    // Act
    ...

    // Assert
    ...
}
```
When Arrange and Act collapse into a single line, combine them with `// Arrange & Act`.

**Mocks — constructor injection**

Set up substitutes and the SUT in the constructor, not in each test:
```csharp
public class FooTests
{
    private readonly IDependency _dependency;
    private readonly Foo _sut;

    public FooTests()
    {
        _dependency = Substitute.For<IDependency>();
        _sut = new Foo(_dependency);

        // default returns
        _dependency.MethodAsync(Arg.Any<CancellationToken>()).Returns(...);
    }
}
```

**Private test helpers**

Declare helper types as `private class` / `private record` inside the test class — never in a separate file:
```csharp
private class TestFoo : BaseClass { ... }
private record TestEvent : DomainEvent;
```

**Assertions to prefer**
| Scenario | Assertion |
|---|---|
| Boolean | `Assert.True` / `Assert.False` |
| Equality | `Assert.Equal` / `Assert.NotEqual` |
| Null | `Assert.Null` / `Assert.NotNull` |
| Collection empty | `Assert.Empty` |
| Collection single | `Assert.Single` |
| Collection contains | `Assert.Contains` |
| Type check | `Assert.IsType<T>` / `Assert.IsAssignableFrom<T>` |
| Exception (sync) | `Assert.Throws<T>` |
| Exception (async) | `await Assert.ThrowsAsync<T>` |

**Async**

Mark async tests as `public async Task` and `await` all async calls:
```csharp
[Fact]
public async Task Method_WhenCondition_ShouldOutcome()
{
    // Arrange
    ...

    // Act
    await _sut.DoAsync();

    // Assert
    await _dependency.Received(1).CallAsync(Arg.Any<CancellationToken>());
}
```

**File header**

Only add `using` directives that are actually needed. Do not add `using Xunit;` — it is already a global using in all test projects.

**Test ordering**

Within each test class, order methods as follows:
1. Edge cases (null, empty, boundary values)
2. Error / exception paths
3. Happy path(s) — **always last**

**Coverage**

- Target a minimum of **85% code coverage** for the class under test
- Cover at minimum: edge cases (null, empty, boundary values), error/exception paths, and happy path(s)
- Avoid reflection in tests whenever possible — if the only way to test something requires reflection, consider it a signal that the production code should expose a better-designed API

### Step 4 — Create or update the file

Write the test file. If a test file already exists for the subject, add the new tests to it rather than overwriting it.

### Step 5 — Run tests

Run the test project to confirm all new tests pass:
```
dotnet test <path-to-test-project.csproj>
```

Report the result to the user. If any test fails, fix it before finishing.
