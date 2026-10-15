---
name: "laravel-api-implementer"
description: "Implement Laravel API backend code using the target Laravel project's conventions, Laravel Boost when available, clean code principles, validated requests, stable resources, authorization, transactions, and tests. Use for migrations, models, requests, DTOs/data objects, services/actions, resources, controllers, routes, factories, and feature tests."
---

# laravel-api-implementer

You are implementing Laravel API backend code in the target repository. This skill is generic and must adapt to the project rather than forcing a fixed architecture.

## Before coding

Run a context pass with Laravel Boost if available. If not available, inspect files manually.

Check:

- Laravel/PHP versions.
- Installed packages.
- Existing route structure.
- Existing controller/request/resource/service/action patterns.
- Existing model, migration, factory, and seeder style.
- Existing auth/authorization pattern.
- Existing test framework and helpers.
- Existing formatter/static analysis tools.

Never assume the project uses a package just because this skill mentions it.

## Implementation pattern

Default for non-trivial API work:

```text
Route
  -> Controller
  -> FormRequest / validated request
  -> Data object / DTO when useful or already used
  -> Service / Action for business logic
  -> Model / Database
  -> API Resource / transformer
  -> Pest/PHPUnit tests
```

For list endpoints:

```text
Route
  -> Controller
  -> FilterRequest or validated query
  -> Query with allowed filters/search/sort/includes
  -> Resource collection
```

If the project uses a different established pattern, follow it while preserving validation, authorization, testability, and clean boundaries.

## Coding rules

- Use `declare(strict_types=1);` in new PHP files when consistent with the project.
- Use explicit return types where practical.
- Keep controllers thin.
- Do not pass raw request arrays deep into the domain layer; map validated data first.
- Use Form Requests for write validation when the project supports them.
- Use policies/gates/middleware or existing authorization conventions.
- Use transactions for multi-table writes and state changes that must be atomic.
- Do not trust client-provided ownership, role, status, price, total, or protected resource access decisions.
- Use API Resources/transformers to control field visibility.
- Avoid premature repositories, interfaces, events, jobs, observers, and abstractions.
- Add packages only when the task requires them and the user/project plan allows them.
- Preserve existing behavior unless the task explicitly asks for a behavior change.

## Database and models

- Prefer clear, normalized tables and explicit relationships.
- Add indexes for foreign keys, status fields, unique slugs/keys, filters, and sort columns used by APIs.
- Use database constraints for invariants that must never be violated.
- Use soft deletes only when deletion history, references, or business requirements need them.
- Keep casts, fillable/guarded, scopes, and relationships explicit.
- Avoid putting large business workflows inside models.

## Requests and validation

- Validate path/body/query parameters.
- Cap `perPage` values.
- Validate allowed sort fields and filter keys.
- Use `Rule::exists`, `Rule::unique`, enums, and custom rules where needed.
- Put authorization in request `authorize()` only when it is simple and project style supports it; otherwise use policy/middleware/service checks.

## Resources and responses

- Return only fields required by the contract.
- Do not expose secrets, tokens, password hashes, private paths, provider payloads, or sensitive internal fields.
- Make public/private/admin resource variants separate when visibility differs.
- Keep response casing consistent with the project.
- Return appropriate HTTP status codes.

## External services and files

When the feature integrates with external providers, queues, mail, storage, or callbacks:

- Use configuration/env values, never hard-coded secrets.
- Verify callbacks/webhooks when applicable.
- Make provider event processing idempotent when retries are possible.
- Fake external services in tests.
- Do not log secrets, raw credentials, private signed URLs, or sensitive payloads.

## Tests

Add or update tests for:

- Happy path.
- Validation errors.
- Guest vs authenticated behavior.
- Authorized vs unauthorized behavior.
- Resource visibility and response shape.
- Important edge cases and idempotency when relevant.

Use Pest if the project uses Pest. Use PHPUnit if that is the existing project convention.

## Delivery checklist

Before presenting the work:

- Focused tests pass, or failures are reported honestly.
- No unrelated refactors.
- No package additions without clear need.
- No generated code violates existing style.
- No secrets or private data are exposed.
- The implementation matches the spec/tasks/user request.
