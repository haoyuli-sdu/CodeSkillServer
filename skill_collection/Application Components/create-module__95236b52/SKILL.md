---
name: "create-module"
description: "Create a new domain module following DDD + Hexagonal Architecture patterns for the blog-server project. Use when creating new modules in modules/ directory with domain, application, and adapter layers. Generates Aggregate Roots, Value Objects, UseCases, Services, Controllers, JPA entities, and Mappers following established patterns from the member module. All code includes Korean KDoc comments."
---

# Create Module

Create a new domain module following blog-server's DDD + Hexagonal Architecture.

## Quick Start

1. Create directory structure: `modules/{module}/domain`, `application`, `adapter/in/web`, `adapter/out/persistence/jpa`
2. Follow patterns from references:
   - **Domain layer**: See [domain-patterns.md](references/domain-patterns.md)
   - **Application layer**: See [application-patterns.md](references/application-patterns.md)
   - **Web adapter**: See [adapter-web-patterns.md](references/adapter-web-patterns.md)
   - **Persistence adapter**: See [adapter-persistence-patterns.md](references/adapter-persistence-patterns.md)

## Critical Requirements

### Korean KDoc

**All classes and methods MUST have Korean KDoc:**

```kotlin
/**
 * 회원 도메인 엔티티
 *
 * 회원의 핵심 정보와 행위를 정의합니다.
 */
class Member private constructor(...) {
    /**
     * 신규 회원을 등록합니다.
     */
    fun register(...): Member { ... }
}
```

### Naming Conventions

- **Package**: `cloud.luigi99.blog.{module}.{layer}.{subdomain}`
- **Files**: Match class name (`Member.kt`, `Email.kt`)
- **Classes**:
  - Aggregate Root: `{Entity}` (e.g., `Member`)
  - Value Object: `{Name}` (e.g., `Email`, `MemberId`)
  - UseCase: `{Verb}{Entity}UseCase` (e.g., `RegisterMemberUseCase`)
  - Service: `{Verb}{Entity}Service` (e.g., `RegisterMemberService`)
  - Controller: `{Entity}Controller` (e.g., `MemberController`)
  - JPA Entity: `{Entity}JpaEntity` (e.g., `MemberJpaEntity`)

## Module Structure

See [module-structure.md](references/module-structure.md) for complete directory layout and dependency rules.

## Development Workflow

### 1. Domain Layer

Start with pure business logic (no Spring dependencies):

- **Aggregate Root**: Private constructor, factory methods, immutability
- **Value Objects**: `@JvmInline value class`, `init` validation
- **Domain Events**: `data class` implementing `DomainEvent`
- **Exceptions**: Extend `BusinessException`

See [domain-patterns.md](references/domain-patterns.md) for code examples.

### 2. Application Layer

Orchestrate use cases with minimal Spring:

- **UseCase interfaces**: Nested Command/Response
- **Services**: `@Service`, `@Transactional`, domain orchestration
- **Facades**: Group related UseCases
- **Repository Ports**: Extend `Repository<T, ID>`

See [application-patterns.md](references/application-patterns.md) for code examples.

### 3. Adapter/In/Web Layer

Handle HTTP requests with full Spring Web:

- **API Interface**: Swagger annotations, separate from Controller
- **Controller**: Implements API interface, uses Facades
- **DTOs**: `@param:Schema` with Korean descriptions

See [adapter-web-patterns.md](references/adapter-web-patterns.md) for code examples.

### 4. Adapter/Out/Persistence Layer

Persist data with JPA:

- **JPA Entities**: Extend `JpaAggregateRoot<ID>` or `JpaDomainEntity<ID>`
- **Repositories**: Extend `JpaRepository`, custom `@Query`
- **Mappers**: `object` singleton, `toDomain()`/`toEntity()`
- **Adapters**: Implement Repository Port, publish domain events

See [adapter-persistence-patterns.md](references/adapter-persistence-patterns.md) for code examples.

## Reference Materials

Load these as needed:

- **[module-structure.md](references/module-structure.md)** - Directory structure, dependency flow
- **[domain-patterns.md](references/domain-patterns.md)** - Aggregate Root, Value Object, Entity, Event, Exception
- **[application-patterns.md](references/application-patterns.md)** - UseCase, Service, Facade, Repository Port
- **[adapter-web-patterns.md](references/adapter-web-patterns.md)** - Controller, API interface, DTOs
- **[adapter-persistence-patterns.md](references/adapter-persistence-patterns.md)** - JPA Entity, Mapper, Repository Adapter
