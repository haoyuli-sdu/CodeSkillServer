---
name: "crud-complete"
description: "Generates complete CRUD operations (Create, Read, Update, Delete) following .NET Clean Architecture with CQRS, MediatR, EF Core, and FluentValidation. Use when user asks to create CRUD for an entity, add CRUD operations, or scaffold entity features."
---

# CRUD Complete - Clean Architecture CQRS Generator

## Overview

This Skill generates complete CRUD operations for entities following the project's Clean Architecture pattern with CQRS and MediatR.

**Generated files:**

- Domain Entity
- Persistence: DbContext registration
- Application: Commands, Queries, Handlers, Validators, DTOs
- API: Controller with RESTful endpoints
- Tests: Unit tests for handlers and validators
- Mappings: AutoMapper profiles

## Workflow

### Step 1: Ask for Entity Details

Ask the user for:

1. **Entity Name** (singular, PascalCase) - e.g., `Product`, `Customer`
2. **Properties** with types - e.g., `Name (string), Price (decimal), IsActive (bool)`
3. **API Route Prefix** (optional, defaults to kebab-case plural) - e.g., `api/v1/products`

### Step 2: Generate Domain Entity

Create entity in `Domain/` following this pattern:

```csharp
using System;

namespace Domain;

public class {EntityName}
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public required string Property1 { get; set; }
    public required string Property2 { get; set; }
    public int Property3 { get; set; }
}
```

**Rules:**

- Id is always `string` with `Guid.NewGuid().ToString()` default
- Use `required` for non-nullable reference types
- Use appropriate .NET types

### Step 3: Update Persistence Layer

Add `DbSet<{EntityName}>` to `Persistence/AppDbContext.cs`:

```csharp
public DbSet<{EntityName}> {EntityName}Plural { get; set; } = null!;
```

### Step 4: Generate Application Layer

Create folder structure under `Application/Features/{EntityName}Plural/`:

```text
Application/Features/{EntityName}Plural/
├── Commands/
│   ├── Create{EntityName}/
│   │   ├── Create{EntityName}Command.cs
│   │   ├── Create{EntityName}CommandHandler.cs
│   │   ├── Create{EntityName}CommandValidator.cs
│   │   └── Create{EntityName}Dto.cs
│   ├── Edit{EntityName}/
│   │   ├── Edit{EntityName}Command.cs
│   │   ├── Edit{EntityName}CommandHandler.cs
│   │   ├── Edit{EntityName}CommandValidator.cs
│   │   └── Edit{EntityName}Dto.cs
│   └── Delete{EntityName}/
│       ├── Delete{EntityName}Command.cs
│       └── Delete{EntityName}CommandHandler.cs
└── Queries/
    ├── Common/
    │   └── DTOs/
    │       └── Get{EntityName}Dto.cs
    ├── Get{EntityName}List/
    │   ├── Get{EntityName}ListQuery.cs
    │   └── Get{EntityName}ListQueryHandler.cs
    └── Get{EntityName}Details/
        ├── Get{EntityName}DetailsQuery.cs
        └── Get{EntityName}DetailsQueryHandler.cs
```

**See [templates.md](templates.md) for complete code templates.**

### Step 5: Update MappingProfiles

Add mappings to `Application/Core/MappingProfiles.cs`:

```csharp
// ========== QUERIES (Read) ==========
CreateMap<{EntityName}, Get{EntityName}Dto>();

// ========== COMMANDS (Write) ==========
CreateMap<Create{EntityName}Dto, {EntityName}>()
    .ForMember(dest => dest.Id, opt => opt.Ignore());
CreateMap<Edit{EntityName}Dto, {EntityName}>()
    .ForMember(dest => dest.Id, opt => opt.Ignore());
```

### Step 6: Create API Controller

Create controller in `API/Controllers/{EntityName}PluralController.cs`:

```csharp
[Route("api/v1/{route-prefix}")]
public class {EntityName}PluralController : BaseApiController
{
    // GET, POST, PUT, DELETE endpoints
}
```

**See [templates.md](templates.md) for complete controller template.**

### Step 7: Create Tests

Create tests under `Tests/Application_Tests/Features/{EntityName}Plural/`:

```text
Tests/Application_Tests/Features/{EntityName}Plural/
├── Commands/
│   ├── Create{EntityName}/
│   │   ├── Create{EntityName}CommandValidatorTests.cs
│   │   └── Create{EntityName}CommandHandlerTests.cs
│   ├── Edit{EntityName}/
│   │   ├── Edit{EntityName}CommandValidatorTests.cs
│   │   └── Edit{EntityName}CommandHandlerTests.cs
│   └── Delete{EntityName}/
│       └── Delete{EntityName}CommandHandlerTests.cs
└── Queries/
    ├── Get{EntityName}List/
    │   └── Get{EntityName}ListQueryHandlerTests.cs
    └── Get{EntityName}Details/
        └── Get{EntityName}DetailsQueryHandlerTests.cs
```

**See [tests.md](tests.md) for complete test templates.**

### Step 8: Database Migration

1. Create migration: `dotnet ef migrations add Add{EntityName} -p Persistence -s API`
2. Apply migration: `dotnet ef database update -p Persistence -s API`

### Step 9: Run Tests

```bash
dotnet test
```

## Validation Rules

**See [validators.md](validators.md) for common validator patterns:**

- Required fields: `NotEmpty()` or `NotNull()`
- String length: `MaximumLength()`
- Numeric ranges: `GreaterThan()`, `LessThan()`
- Email validation: `EmailAddress()`
- Custom validation: `Must()`

## Important Notes

1. **Namespace conventions**: Use plural form for feature folders (`Products`, `Customers`)
2. **DTO naming**: `CreateXDto`, `EditXDto`, `GetXDto`
3. **Command/Query naming**: `CreateXCommand`, `GetXListQuery`, `GetXDetailsQuery`
4. **Handler naming**: `CreateXCommandHandler`, `GetXListQueryHandler`
5. **Validators**: Always create `AbstractValidator<T>` for Create/Edit commands
6. **Result pattern**: Use `Result<T>` with `Success()` or `Failure()`
7. **Error codes**: 400 for bad request, 404 for not found

## Example: Creating a Product Entity

User input: "Create CRUD for Product with Name (string), Price (decimal), Stock (int)"

Generated files:

- `Domain/Product.cs`
- `Application/Features/Products/...` (Commands, Queries, DTOs, Handlers, Validators)
- `API/Controllers/ProductsController.cs`
- `Tests/Application_Tests/Features/Products/...`

## Quick Reference

| File Pattern | Location |
| --- | --- |
| Entity | `Domain/{EntityName}.cs` |
| DbContext | `Persistence/AppDbContext.cs` |
| Commands | `Application/Features/{Feature}/Commands/{Operation}/` |
| Queries | `Application/Features/{Feature}/Queries/{Operation}/` |
| DTOs | Within Command/Query folders or `Queries/Common/DTOs/` |
| Validators | Within Command folders |
| Controller | `API/Controllers/{EntityName}PluralController.cs` |
| Tests | `Tests/Application_Tests/Features/{EntityName}Plural/` |
