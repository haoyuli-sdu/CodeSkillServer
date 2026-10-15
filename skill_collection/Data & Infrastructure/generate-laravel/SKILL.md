---
name: "generate-laravel"
description: "Generate Laravel CRUD scaffold with Model, Controller, FormRequest, Migration, Factory, Policy, and tests"
---

# Generate Laravel CRUD Scaffold

Generate a complete Laravel CRUD scaffold for the given entity.

## What To Do

1. **Model** with Eloquent fillable, casts, relations, and factory() link
2. **Migration** with typed columns, nullable constraints, foreign keys, and indexes
3. **Controller** as resource controller (index, store, show, update, destroy)
4. **FormRequest** with authorize() and rules() for create and update validation
5. **Factory** with Faker definitions for all fillable fields
6. **Seeder** calling the factory for demo data
7. **Policy** with viewAny, view, create, update, delete, restore, forceDelete
8. **API Resource** (JsonResource) for consistent response transformation
9. **Routes** entry with Route::apiResource or Route::resource
10. **PHPUnit test** covering CRUD HTTP endpoints

## Structure

```
app/
  Models/{EntityName}.php
  Http/Controllers/{EntityName}Controller.php
  Http/Requests/Store{EntityName}Request.php
  Http/Requests/Update{EntityName}Request.php
  Http/Resources/{EntityName}Resource.php
  Policies/{EntityName}Policy.php

database/
  migrations/{timestamp}_create_{entity_name_plural}_table.php
  factories/{EntityName}Factory.php
  seeders/{EntityName}Seeder.php

tests/Feature/
  {EntityName}ControllerTest.php
```

## Patterns
- declare(strict_types=1) on every generated PHP file
- Constructor property promotion in FormRequest constructors
- Route model binding: type-hinted model in method signatures
- RefreshDatabase trait on the test class

## Arguments
- `<entity-name>`: Entity name in PascalCase (e.g., JobOffer, Candidate)
- `--api`: API-only mode — generates apiResource routes and skips web views
