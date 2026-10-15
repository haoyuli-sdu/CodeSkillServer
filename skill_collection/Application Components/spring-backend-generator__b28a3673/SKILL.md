---
name: "spring-backend-generator"
description: "Generate production-ready Spring Boot 3.x backend code following DDD principles and team conventions. Use when you need to: (1) Create complete backend layers (Entity/Repository/Service/Controller/DTO) from specifications, (2) Convert DDL to JPA Entities, (3) Generate API endpoints from API specifications, (4) Create domain-specific error codes and exceptions, (5) Build CRUD operations following the team's coding standards (Java 21, constructor injection, Lombok conventions, transaction management, N+1 prevention, soft delete patterns, context isolation via ID references). Supports 아이니이누 project structure with contexts: member, pet, walk, chat, community, lostpet, notification."
---

# Spring Backend Generator

Generate production-ready Spring Boot 3.x backend code for the 아이니이누 (Aini Inu) project following Domain-Driven Design principles and strict team conventions.

## When to Use This Skill

Use this skill when you need to generate backend code for the 아이니이누 project, specifically:

- **Full layer generation**: "Create Member context with all layers"
- **DDL to Entity**: "Convert the member table DDL to a JPA Entity"
- **API to Controller**: "Generate ThreadController from the API spec"
- **CRUD operations**: "Create Pet CRUD with error handling"
- **Context setup**: "Initialize Chat context with base structure"

## External Documentation (Context7 MCP)

**IMPORTANT**: This skill leverages the Context7 MCP server for up-to-date Spring ecosystem documentation.

When generating code or resolving framework-specific questions, use Context7 to query:

- **Spring Boot** (`/spring-projects/spring-boot`) - For configuration, auto-configuration, starters
- **Spring Framework** (`/spring-projects/spring-framework`) - For core concepts, DI, AOP
- **Spring Data JPA** (`/spring-projects/spring-data-jpa`) - For repository patterns, query methods
- **Hibernate** (`/hibernate/hibernate-orm`) - For JPA implementation details, annotations
- **Lombok** (`/projectlombok/lombok`) - For annotation usage and behavior

**Usage Pattern**:
```
1. Use mcp__context7__resolve-library-id to find the library
2. Use mcp__context7__query-docs with specific questions
3. Apply the documentation to code generation
```

**Example**:
- Question: "How to use @EntityGraph to prevent N+1?"
- Action: Query Spring Data JPA docs via Context7
- Apply: Use the latest recommended patterns in generated repository code

This ensures generated code follows the latest best practices and framework conventions.

## Quick Start

### Step 1: Read Project Conventions

**ALWAYS** start by reading the conventions reference:

```
view references/conventions.md
```

This file contains critical information about:
- Package structure (`com.ainiinu.{context}/{layer}`)
- DDD principles (ID-only references across contexts)
- Lombok rules (@Data forbidden, Entity with @NoArgsConstructor(access=PROTECTED))
- Transaction management (@Transactional(readOnly=true) for queries)
- Value objects (@Embeddable patterns)

### Step 2: Read Response Patterns

For API and error handling code, read:

```
view references/response-patterns.md
```

This covers:
- ApiResponse<T> structure
- ErrorCode interface and domain-specific enums
- BusinessException pattern
- GlobalExceptionHandler

### Step 3: Read Entity Patterns (if creating entities)

For entity generation, read:

```
view references/entity-patterns.md
```

This covers:
- Business methods (no setters)
- Dirty checking
- Lazy loading
- N+1 prevention
- Soft delete (@SQLDelete)
- BaseTimeEntity

### Step 4: Review Examples

See complete working examples:

```
view references/examples.md
```

## Core Principles (Summary)

**MANDATORY - Never Violate**:

1. **No `var`**: Always use explicit types
2. **No setters in Entity**: Use business methods
3. **Constructor injection**: @RequiredArgsConstructor only
4. **Context isolation**: Reference other contexts by ID only
5. **Error handling**: ErrorCode enum per domain + BusinessException
6. **Response format**: ResponseEntity<ApiResponse<T>>
7. **Lazy loading**: All @ManyToOne and @OneToOne
8. **Transaction**: @Transactional(readOnly=true) for queries
9. **Lombok limits**: No @Data in entities, Entity with @NoArgsConstructor(access=PROTECTED), @Setter allowed in DTOs
10. **Dynamic queries**: Use QueryDSL when dynamic query conditions are needed

## Typical Workflow

### Generate Complete Context

```
User: "Create the Pet context with CRUD operations"

Steps:
1. view references/conventions.md
2. view references/entity-patterns.md  
3. view references/response-patterns.md
4. Create package structure: com.ainiinu.pet/{entity,repository,service,controller,dto,exception}
5. Generate PetErrorCode enum
6. Generate Pet entity with business methods
7. Generate PetRepository
8. Generate PetService with @Transactional annotations
9. Generate PetController with ResponseEntity<ApiResponse<T>>
10. Generate Request/Response DTOs (class with appropriate Lombok annotations)
```

### Convert DDL to Entity

```
User: "Convert this DDL to a Pet entity"

Steps:
1. view references/entity-patterns.md
2. Map SQL types to Java types
3. Add @Entity, @Id, @GeneratedValue
4. Add BaseTimeEntity extends
5. Use @Embeddable for value objects (if applicable)
6. Add business methods (no setters)
7. Add @NoArgsConstructor(access=PROTECTED)
```

### Generate from API Spec

```
User: "Generate ThreadController from the API spec"

Steps:
1. view references/conventions.md
2. view references/response-patterns.md
3. Parse endpoints, methods, request/response
4. Generate Request DTOs (class with @Getter @Setter @NoArgsConstructor, add jakarta.validation)
5. Generate Response DTOs (class with @Getter @Builder or @AllArgsConstructor)
6. Generate Controller with @RestController, @RequestMapping
7. Use ResponseEntity<ApiResponse<T>> for all endpoints
8. Add @Valid for request validation
```

## Package Structure Reference

```
com.ainiinu/
├── common/
│   ├── config/          (SecurityConfig, JpaConfig, etc.)
│   ├── security/        (JwtTokenProvider, etc.)
│   ├── response/        (ApiResponse, PageResponse, SliceResponse - 추후 추가 예정)
│   ├── exception/       (GlobalExceptionHandler, BusinessException, ErrorCode interface, CommonErrorCode)
│   ├── entity/          (BaseTimeEntity)
│   └── util/            (DateTimeUtil, LocationUtil)
│
├── member/              (Bounded Context)
│   ├── entity/
│   ├── repository/
│   ├── service/
│   ├── controller/
│   ├── dto/
│   └── exception/       (MemberErrorCode)
│
├── pet/                 (Bounded Context)
│   ├── entity/
│   ├── repository/
│   ├── service/
│   ├── controller/
│   ├── dto/
│   └── exception/       (PetErrorCode)
│
└── (other contexts: walk, chat, community, lostpet, notification)
```

## Important Notes

- **Read references FIRST** before generating code
- **Multiple references** may be needed for complex tasks
- **Validate against conventions** after generation
- **Test code** should follow the same principles (BDD style, given/when/then)

## References

For detailed information, see:
- [Conventions](references/conventions.md) - **READ THIS FIRST**
- [Response Patterns](references/response-patterns.md) - API response & error handling
- [Entity Patterns](references/entity-patterns.md) - JPA entity guidelines
- [Examples](references/examples.md) - Complete working code samples
