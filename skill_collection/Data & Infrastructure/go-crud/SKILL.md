---
name: "go-crud"
description: "Generate Go CRUD operations using Gin framework and GORM. Includes Models, DTOs, Repository, Service, and Handler templates."
---

# go-crud

Stack: Go 1.21+ + Gin 1.9.x + GORM 1.25.x

## Workflow

1. Generate CRUD code using the template generator
2. Review and customize the generated files
3. Build and run the application

## Quick Start

### Generate CRUD

```bash
# Generate CRUD for an entity
# Usage: bash scripts/generate-crud.sh <EntityName> [output-dir]
bash scripts/generate-crud.sh User ./internal
```

**Parameters**:
- `EntityName`: The name of the entity (e.g., User, Product, Order)
- `output-dir`: Optional output directory (default: ./internal)

**AI Agent Notes**:
- Entity name should be PascalCase (e.g., User, ProductCategory)
- Output directory should be the internal package folder
- The script generates: Model, DTOs, Repository, Service, Handler
- Follows clean architecture with layered separation
- Uses GORM for database operations

## Generated Code Structure

```
{output-dir}/
├── models/
│   └── {entity}.go
├── dto/
│   └── {entity}_dto.go
├── repository/
│   └── {entity}_repository.go
├── service/
│   └── {entity}_service.go
└── handler/
    └── {entity}_handler.go
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/{entity} | Create new entity |
| GET | /api/{entity} | List all entities |
| GET | /api/{entity}/:id | Get entity by ID |
| PUT | /api/{entity}/:id | Update entity |
| DELETE | /api/{entity}/:id | Delete entity |

## Dependencies (go.mod)

```go
require (
    github.com/gin-gonic/gin v1.9.1
    gorm.io/driver/mysql v1.5.2
    gorm.io/gorm v1.25.5
)
```

## Coding Standards

This skill follows Go best practices:

### Naming Conventions

- **Exported Functions/Types**: PascalCase (e.g., `UserService`, `CreateUser`)
- **Unexported Functions/Variables**: camelCase (e.g., `userService`, `createUser`)
- **Package Names**: short, lowercase, simple (e.g., `models`, `handlers`)
- **Constants**: PascalCase for exported, camelCase for unexported

### Code Patterns

- Follow Go project layout (standard Go layout or simple layout)
- Use interfaces for abstraction
- Return errors, don't panic
- Use context for request-scoped values
- Use dependency injection
- Follow Gin framework conventions
- Use GORM for database operations

## Customization

- Modify model fields in the generated Model file
- Add custom queries in Repository
- Add business logic in Service
- Configure routes in main.go
