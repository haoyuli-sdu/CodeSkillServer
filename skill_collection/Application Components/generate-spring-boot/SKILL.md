---
name: "generate-spring-boot"
description: "Generate Spring Boot CRUD scaffold with Controller-Service-Repository"
---

# Generate Spring Boot CRUD

Generate a complete Spring Boot CRUD scaffold for the given entity.

## What To Do

1. **Entity class** with JPA annotations (@Entity, @Table, @Id, @GeneratedValue)
2. **Repository interface** extending JpaRepository (or MongoRepository for MongoDB)
3. **Service class** with @Service, @Transactional, constructor injection
4. **Controller class** with @RestController, @RequestMapping, proper HTTP methods
5. **DTO record** with validation annotations (@NotBlank, @Size, @Email)
6. **Mapper** — static fromEntity() / toEntity() methods on DTO record
7. **Flyway migration** (V1__create_{entity}_table.sql) for SQL databases
8. **Exception handler** with @ControllerAdvice returning ProblemDetail (RFC 7807)
9. **Integration test** with @SpringBootTest and Testcontainers

## Structure

```
src/main/java/com/example/{module}/
  ├── controller/{Entity}Controller.java
  ├── service/{Entity}Service.java
  ├── repository/{Entity}Repository.java
  ├── model/{Entity}.java
  ├── dto/{Entity}Request.java (record)
  ├── dto/{Entity}Response.java (record)
  └── exception/{Entity}NotFoundException.java

src/main/resources/db/migration/
  └── V1__create_{entity}_table.sql

src/test/java/com/example/{module}/
  └── {Entity}ControllerTest.java
```

## Patterns
- Constructor injection (no @Autowired on fields)
- @Transactional on service methods
- @Valid on @RequestBody parameters
- Pageable for list endpoints (default 20, max 100)
- ResponseEntity for proper HTTP status codes
- @EntityGraph or JOIN FETCH for eager loading where needed

## Arguments
- `<entity-name>`: Entity name in PascalCase (e.g., Employee, JobOffer)
- `--db=<postgresql|mysql|mongodb>`: Database type (default: postgresql)
- `--auth=<jwt|oauth2>`: Authentication type (optional, adds @PreAuthorize)
