---
name: "generate-be-code"
description: "Generate scalable backend modules and APIs with principal-level standards. Use when: creating Node/NestJS/Express endpoints, service/repository layers, database models, validation, authentication, pagination, caching, queue integration, and traffic-ready API design with observability and security hardening."
---

# Generate Backend Code

Generate production-ready backend APIs and modules designed for high traffic, strong correctness, and operational reliability.

## Use When

- Creating new APIs, services, and repositories.
- Designing schema/query paths for high-read or high-write workloads.
- Implementing authz/authn and input validation.
- Building queue-driven or async processing flows.

Trigger phrases:
- "generate BE code"
- "create backend API"
- "build scalable endpoint"
- "create service and repository"

## Inputs to Collect

1. Domain and business rules.
2. API contract: routes, request/response, status/error model.
3. Data model and consistency constraints.
4. Traffic profile: expected QPS, burst pattern, latency target.
5. Security model: auth, roles/permissions, tenant boundaries.

## Dependency Approval Gate

Before introducing new infrastructure, storage, or external services, always ask for explicit approval first.

Examples that require approval:

- Redis caching/session layer.
- Queue/broker systems (BullMQ, RabbitMQ, Kafka).
- Search engines/vector stores.
- New auth providers.
- New monitoring/tracing stack.

Required prompt format:

"I can implement this with current stack, or with [X] for [benefit]. Do you want me to add [X]?"

If user says "yes": implement and include setup/config impacts.
If user says "no": proceed using existing stack only.
If unclear: ask one concise follow-up question.

If traffic data is missing, default to conservative scale assumptions and state them.

## Workflow

## Mandatory Backend Standards

Always enforce these defaults unless user explicitly overrides:

### Structured Logging Fields

- request_id
- user_id
- endpoint
- latency
- error_code

### Metrics and Tracing

- Include P95 latency metric.
- Include error rate metric.
- Add tracing when applicable in the target architecture.

### N+1 Query Prevention Rule

Explicitly prevent N+1 access patterns using one or more of:

- joins
- batching
- dataloader pattern (if needed)

### Idempotency Rules (Critical)

For payment-related APIs, require idempotent request handling:

- Accept and validate idempotency key.
- Persist request fingerprint and result.
- Return the original successful response for repeated same key.
- Reject mismatched payload reuse for same key.
- Protect with transaction and unique constraint strategy.

### 1) API and Domain Design

1. Define route contracts and idempotency expectations.
2. Separate controller/service/repository concerns.
3. Define DTO/schema validation at boundaries.

### 2) Data Layer Design

1. Model entities for query access patterns first.
2. Add indexes for hot filters/sorts/joins.
3. Use transactions where multi-write consistency is required.
4. Implement pagination strategy (cursor preferred for large datasets).

### 3) Reliability and Performance

1. Add timeouts, retries (only for safe operations), and backpressure controls.
2. Add cache strategy (read-through, key design, invalidation policy) where beneficial.
3. Move heavy/slow operations to queue/background workers.
4. Prevent N+1 and over-fetching in query paths.

### 4) Security and Guardrails

1. Enforce authentication and authorization at endpoint level.
2. Validate/sanitize all external input.
3. Add rate limiting and abuse protections on sensitive routes.
4. Avoid sensitive data leakage in logs and errors.

### 5) Observability and Quality Gates

A module is done only when:

- Structured logging includes traceable request context.
- Structured logs include: request_id, user_id, endpoint, latency, error_code.
- Metrics include at minimum P95 latency and error rate.
- Tracing is added when applicable.
- API responses are consistent and typed.
- Query strategy demonstrates N+1 prevention (joins/batching/dataloader as needed).
- Payment APIs implement idempotency key flow and replay-safe behavior.
- Tests cover happy path + key failure modes.
- Migration/index impact is reviewed for production safety.

## Output Contract

1. Implementation plan with architecture decisions.
2. Full runnable code for routes/services/repositories/schemas.
3. DB and index recommendations tied to query patterns.
4. Test plan (unit + integration) and run commands.
5. Deployment/ops notes for safe rollout.

## Principles

- Design from SLOs and traffic profile, not just functionality.
- Keep domain logic in services, persistence in repositories.
- Favor explicit contracts and deterministic error handling.
- Build for debuggability from day one.
