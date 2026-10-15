---
name: "webapp"
description: "Generate web application code including HTTP handlers, repository interfaces, implementations, and tests. Use when building REST APIs, creating CRUD endpoints, scaffolding backend services, or implementing web applications."
---

# Web Application Generator

## Overview

This skill generates web application code from domain models using Clean Architecture. It applies sensible defaults that can be overridden by project-specific CLAUDE.md.

## Workflow

**Execute all steps in sequence without stopping for user confirmation.**

1. **Analyze Relationships**
   - Follow `analyze-relations` skill to analyze domain models
   - Do NOT write to CLAUDE.md, do NOT stop after this step

2. **Write Layer Structure**
   - Run `split-layer` skill once, write `## Layer Structure` to CLAUDE.md
   - Do NOT run split-layer a second time, do NOT stop after this step

3. **Design Directory Structure**
   - Follow `design-structure` skill to derive directory structure
   - Input: `## Layer Structure` from CLAUDE.md, domain models, External Interfaces / External Dependencies from CLAUDE.md
   - Write `## Directory Structure` to CLAUDE.md, do NOT stop after this step

4. **Generate Code**
   - Read CLAUDE.md for configuration, layer structure, and directory structure
   - Output to `dist/` directory (keeps source clean)
   - dist/ should be a complete, runnable application

5. **Generate Tests**
   - Read `## Layer Structure` and generated code
   - Generate test code based on layer type and generated code (see Test Generation section)
   - Output to `dist/` directory alongside implementation

6. **Verify**
   - Ensure generated code compiles
   - Ensure tests pass
   - Check for proper error handling

---

## Layer Definition

| Condition | Layer Definition |
|-----------|------------------|
| Default, widely understood | Clean Architecture |
| Traditional enterprise | Layered |
| Emphasis on ports/adapters | Hexagonal |
| Domain model centric | Onion |
| Simple, fewer abstractions | Three-Tier |

Each reference contains layer concepts and Layer Structure Template for CLAUDE.md:
- [Clean Architecture](references/layers/clean-architecture.md) (default) - use `split-layer` skill
- [Layered](references/layers/layered.md)
- [Hexagonal](references/layers/hexagonal.md)
- [Onion](references/layers/onion.md)
- [Three-Tier](references/layers/three-tier.md)

For non-Clean Architecture styles, copy Layer Structure Template from the reference file to CLAUDE.md.

---

## Test Generation

Tests verify that each layer fulfills its responsibilities based on its position in the layer structure.

### Test Strategy by Layer Type

| Layer/Component | What to test | How to test |
|-----------------|--------------|-------------|
| Entity (inner) | Correct decisions based on rules | Unit test with various inputs |
| Entity (inner) | Business rules hold after any operation | Unit test |
| UseCase | Goal achieved by coordinating dependencies | Unit test with mocked dependencies |
| UseCase | Consistency maintained after operations | Unit test |
| Handler (input) | Correct response for valid/invalid requests | Unit test with mocked inner layer |
| Repository (output) | Save then retrieve returns equivalent data | Integration test with real or in-memory DB |
| Gateway (output) | Correct external call made | Unit test with mocked external service |

### Test File Structure

Place test files alongside implementation. The directory layout follows `design-structure` output.

### Test Patterns

#### Entity Test

```go
func TestTask_CanTransitionTo(t *testing.T) {
    // correct decision based on business rules
    task := NewTask("title", StatusTodo)

    // Valid transition
    if !task.CanTransitionTo(StatusInProgress) {
        t.Error("should allow Todo -> InProgress")
    }

    // Invalid transition
    if task.CanTransitionTo(StatusDone) {
        t.Error("should not allow Todo -> Done directly")
    }
}

func TestTask_Invariant(t *testing.T) {
    // business rules hold after operation
    task := NewTask("title", StatusTodo)
    task.Complete()

    if task.Status != StatusDone {
        t.Error("completed task should have Done status")
    }
    if task.CompletedAt == nil {
        t.Error("completed task should have CompletedAt set")
    }
}
```

#### Handler Test

```go
func TestTaskHandler_Create(t *testing.T) {
    // valid request → correct response
    mockUseCase := &MockTaskUseCase{}
    handler := NewTaskHandler(mockUseCase)

    req := httptest.NewRequest("POST", "/tasks", strings.NewReader(`{"title":"test"}`))
    rec := httptest.NewRecorder()

    handler.Create(rec, req)

    if rec.Code != http.StatusCreated {
        t.Errorf("expected 201, got %d", rec.Code)
    }
}

func TestTaskHandler_Create_InvalidRequest(t *testing.T) {
    // invalid request → error response
    handler := NewTaskHandler(&MockTaskUseCase{})

    req := httptest.NewRequest("POST", "/tasks", strings.NewReader(`{invalid}`))
    rec := httptest.NewRecorder()

    handler.Create(rec, req)

    if rec.Code != http.StatusBadRequest {
        t.Errorf("expected 400, got %d", rec.Code)
    }
}
```

#### Repository Test

```go
func TestTaskRepository_SaveAndFind(t *testing.T) {
    // save then retrieve → equivalent data returned
    db := setupTestDB(t)
    repo := NewTaskRepository(db)

    task := &Task{Title: "test", Status: StatusTodo}
    err := repo.Save(context.Background(), task)
    if err != nil {
        t.Fatal(err)
    }

    found, err := repo.FindByID(context.Background(), task.ID)
    if err != nil {
        t.Fatal(err)
    }

    if found.Title != task.Title || found.Status != task.Status {
        t.Error("retrieved task should be equivalent to saved task")
    }
}

func TestTaskRepository_FindByID_NotFound(t *testing.T) {
    // retrieve non-existent → not-found indication
    db := setupTestDB(t)
    repo := NewTaskRepository(db)

    _, err := repo.FindByID(context.Background(), "nonexistent")
    if err != ErrNotFound {
        t.Errorf("expected ErrNotFound, got %v", err)
    }
}
```

### Test Conventions

- Use table-driven tests for multiple input scenarios
- Name tests as `Test{Component}_{Method}`
- Use `t.Helper()` for test helper functions
- Use `t.Parallel()` where safe

---

## Defaults

These defaults apply unless overridden in project's CLAUDE.md.

### API Design

| Relationship | Route Pattern |
|-------------|---------------|
| Top-level entity | `/{entities}`, `/{entities}/{id}` |
| belongs_to | `/{parents}/{parentID}/{children}` |
| Self-reference | `/{entities}/{id}/sub{entities}` |
| Many-to-many | `/{entities}/{id}/{related}`, `/{entities}/{id}/{related}/{relatedID}` |
| Polymorphic | Routes on each target (`/{targets}/{id}/attachments`) |

### Conventions

- Use `context.Context` for all repository methods
- Return domain errors, not database-specific errors
- Use domain methods for business logic (e.g., `entity.CanDelete(userID)`)
- Handler signature: `func(w http.ResponseWriter, r *http.Request)`
- JSON for request/response bodies
- User ID from `X-User-ID` header (for authorization checks)

### Authorization

Infer authorization rules from domain methods:
- `CanDelete(userID)` → check before delete
- `CanEdit(userID)` → check before update
- `IsOwner(userID)` → owner-only operations
- `IsMember(userID)` → member-only access

### Schema Generation

- Generate `initSchema()` function in main.go
- Include foreign key constraints based on relationships
- Add indexes for foreign key columns
- Use appropriate types per database

---

## Project CLAUDE.md

Projects specify (human writes):

```markdown
## Application

{Description of the application}

## External Interfaces

- {Name}: {Description}

## External Dependencies

- {Name}: {Description}

## Tech Stack

- Language: Go 1.21+
- HTTP Router: chi
- Database: SQLite with sqlx
```

Generated by skills (can be edited by human):

```markdown
## Layer Structure

(Derived by split-layer skill)

## Directory Structure

(Derived by design-structure skill)
```
