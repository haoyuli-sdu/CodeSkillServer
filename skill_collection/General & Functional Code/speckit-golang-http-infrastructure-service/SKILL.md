---
name: "speckit-golang-http-infrastructure-service"
description: "Use this skill when the user asks to create Spec Kit / Speckit documentation for a Go outbound HTTP infrastructure service that calls external APIs using standard net/http. This includes Indonesian prompts such as \"buat speckit infra HTTP Go\", \"buat speckit untuk generate code infra\", \"buat speckit outbound service\", \"buat spesifikasi integrasi vendor\", or English prompts such as \"generate Speckit for Go HTTP infrastructure service\", \"create outbound HTTP integration spec\", and \"make spec for vendor API adapter\". The output must be created under docs/speckit/<feature-name>/ and should be suitable as input for the golang-http-infrastructure-service implementation skill."
---

# Speckit Go HTTP Infrastructure Service

Use this skill when the user wants a Speckit specification before generating Go infrastructure/service code for an outbound external API integration.

This skill creates specification files only. Do not generate Go code directly from this skill.

The generated Speckit must be implementation-ready for a Go service that uses standard `net/http`, `context.Context`, injected `*http.Client`, JSON request/response handling, safe error mapping, sensitive logging rules, and `httptest.Server` unit tests.

## Output Location

Write files under:

```text
docs/speckit/<feature-name>/
```

Use kebab-case for `<feature-name>`.

Create exactly:

```text
docs/speckit/<feature-name>/
  spec.md
  plan.md
  tasks.md
```

## Workflow

Follow this order:

```text
clarify -> specify -> plan -> tasks
```

If required information is missing and the user allows assumptions, use `TBD` instead of guessing vendor-specific behavior.

## Clarify

Ask only for details that cannot be safely inferred.

Before generating files, clarify:

* service or integration name
* upstream/vendor name
* external API endpoint path
* HTTP method, defaulting to `POST` when not specified
* base URL config source if relevant
* required headers
* authentication requirement such as Basic Auth, Bearer token, API key, or static headers
* signature requirement, including signature input fields and header name
* application request DTO fields
* application response DTO fields
* exact vendor request JSON shape
* exact vendor response JSON shape
* upstream success response code, defaulting to `0000`
* HTTP error mapping rules
* business error mapping rules
* sensitive fields that must not be logged raw
* mock mode requirement
* expected package/path convention if the project differs from the default layout

Do not require the user to provide all answers before producing docs if they explicitly want a draft. Mark unknown values as `TBD`.

## spec.md

Focus on what the outbound integration must do and why.

Must include:

* feature or integration name
* purpose
* upstream/vendor name
* scope
* out of scope
* external endpoint
* HTTP method
* base URL expectation
* required headers
* authentication requirement
* signature requirement
* application request DTO fields
* application response DTO fields
* vendor request JSON shape
* vendor response JSON shape
* success response code
* HTTP status handling
* business response code handling
* sensitive data handling
* mock mode behavior
* timeout expectation
* retry expectation
* success criteria

Use tables for DTO fields, headers, and error mapping when helpful.

## plan.md

Focus on how the Go infrastructure service will be built.

Must include:

* tech stack: Go standard library `net/http`
* architecture boundary between application DTO and vendor DTO
* application DTO path
* outbound interface path
* infrastructure DTO path
* HTTP implementation path
* factory/config path
* config fields and validation rules
* constructor and default timeout plan
* payload mapping strategy
* response mapping strategy
* header construction strategy
* signature construction strategy if needed
* response body limit strategy using `io.LimitReader`
* JSON validation strategy
* HTTP error mapping strategy
* business error mapping strategy
* sensitive logging strategy
* mock mode strategy if needed
* unit test strategy using `httptest.Server`

Use these default paths unless the project uses a different convention:

```text
application/dto/<context>.go
application/repository/<feature>.go
internal/infrastructure/service/<feature>/<feature>_dto.go
internal/infrastructure/service/<feature>/<feature>_http.go
internal/infrastructure/service/<feature>/factory.go
internal/infrastructure/service/<feature>/<feature>_test.go
```

## tasks.md

Break the implementation into ordered tasks.

Use checkbox format:

```md
# Tasks

- [ ] Confirm upstream API contract and missing `TBD` values
- [ ] Create application request and response DTOs
- [ ] Create outbound repository or port interface
- [ ] Create vendor request and response DTOs with JSON tags
- [ ] Create config struct, constants, service struct, and constructor
- [ ] Validate required config fields and normalize base URL
- [ ] Implement payload mapping from application DTO to vendor DTO
- [ ] Implement request creation with `http.NewRequestWithContext`
- [ ] Set required headers and signature if needed
- [ ] Send request using injected `*http.Client`
- [ ] Read response body with `io.LimitReader`
- [ ] Unmarshal and validate JSON response
- [ ] Map HTTP 5xx and infrastructure failures
- [ ] Map HTTP 4xx according to upstream contract
- [ ] Map non-success business response codes
- [ ] Map vendor response DTO to application response DTO
- [ ] Add mock mode behavior if needed
- [ ] Add `httptest.Server` unit tests for success and error paths
- [ ] Verify expected headers and payload in tests
- [ ] Run `gofmt`
- [ ] Run focused Go unit tests
- [ ] Verify no raw sensitive data is logged
- [ ] Verify no third-party HTTP client is introduced
```

Add, remove, or rename tasks only when the integration contract requires it.

## Rules

* Generate only Speckit documentation files.
* Keep the docs concise but implementation-ready.
* Use `TBD` for unknown vendor-specific details.
* Do not invent vendor response codes, signatures, or auth behavior.
* Do not include inbound REST API endpoint specs unless the user explicitly asks for them.
* Do not include CRUD UI behavior.
* Require standard Go `net/http`; do not plan Resty or other third-party HTTP clients.
* Keep application DTOs separate from vendor DTOs.
* Plan unit tests with `httptest.Server`, not mockery, for HTTP infrastructure behavior.
* Mention mockery only for application/usecase tests that depend on the outbound interface.
* Avoid automatic retry for submit, registration, payment, activation, or mutation APIs unless idempotency is confirmed.
* Treat sensitive fields such as `nik`, `msisdn`, `image`, `document`, `file`, `base64`, `token`, `authorization`, `api_key`, `signature`, `secret`, and `password` as unsafe for raw logs.

## Agent Behavior

When applying this skill:

1. Ask clarification questions only for missing information that materially affects the Speckit.
2. Normalize feature name to kebab-case.
3. Create only `spec.md`, `plan.md`, and `tasks.md`.
4. Save files under `docs/speckit/<feature-name>/`.
5. Use `TBD` for missing details when the user wants a draft.
6. Make the generated docs suitable input for the `golang-http-infrastructure-service` implementation skill.
7. After creating files, summarize created files and mention that the next step is generating the Go infrastructure code from the Speckit.
