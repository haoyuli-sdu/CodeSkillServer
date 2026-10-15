---
name: "api-implementation"
description: "Implement backend API endpoints — routing, middleware, input validation, error handling, authentication, rate limiting, file upload. Trigger on /api-implementation, or when building endpoints, adding middleware, handling file uploads, or implementing API security."
---

# API Implementation

Build backend API endpoints with security, validation, and error handling from the start. Complements `api-design` (which reviews contracts) with actual implementation patterns.

## Workflow

### 1. Route structure

- **Consistent naming** — `GET /resources`, `POST /resources`, `DELETE /resources/:id`.
- **Middleware chain** — auth → validation → rate-limit → handler.
- **Handler separation** — route file only wires middleware + handler. Logic lives in service layer.
- **Async handling** — wrap async handlers to catch rejected promises (never unhandled promise rejection).

### 2. Input validation

Validate at the boundary — before the handler receives data.

- **Schema validation** — use Zod, Joi, Yup, or validation library. Never trust `req.body` directly.
- **Type coercion** — string numbers (`"5"`) parsed to actual numbers. Query params are strings by default.
- **Sanitization** — strip HTML/XSS from string inputs. Trim whitespace.
- **File validation** — check MIME type, file size, extension — not just extension.
- **Error response** — validation errors return 400 with field-level messages: `{ errors: [{ field: "email", message: "..." }] }`.

### 3. Authentication & Authorization

- **Auth middleware** — enforce authentication at middleware level, not in individual handlers.
- **401 vs 403** — 401 for unauthenticated, 403 for authenticated but not authorized.
- **Token validation** — verify signature, expiry, issuer. Reject before handler runs.
- **Scope/role check** — authorization middleware checks permissions after authentication.
- **Testing** — test both authenticated and unauthenticated paths for every protected endpoint.

### 4. Error handling

- **Consistent format** — all errors follow `{ error: { code, message, details? } }`.
- **HTTP status codes** — 400 validation, 401 auth, 403 forbidden, 404 not found, 409 conflict, 422 unprocessable, 500 server error.
- **Operational vs programmer errors** — operational (invalid input, not found) return structured errors. Programmer errors (undefined, type error) return 500 with minimal detail in production.
- **Error middleware** — centralized error handler at the app level, not try/catch in every handler.

### 5. Rate limiting

- **Per-endpoint or per-user** — auth endpoints stricter than read endpoints.
- **Headers** — return `RateLimit-Remaining`, `RateLimit-Reset` on every response.
- **Response** — 429 with `Retry-After` header when limit exceeded.
- **Distributed** — use Redis or similar for rate limit state across instances.

### 6. Response format

- **Consistent envelope** — `{ data, meta? }` for success, `{ error }` for failure.
- **Pagination** — `{ data: [], meta: { page, perPage, total } }` for list endpoints.
- **Idempotency** — `POST` endpoints return `409 Conflict` if retried with same idempotency key.
- **Caching headers** — `ETag`, `Last-Modified` for GET endpoints. `Cache-Control` for static responses.

### 7. File upload

- **Size limit** — enforce in middleware, not just client-side.
- **MIME validation** — check actual MIME type (magic bytes), not just `Content-Type` header.
- **Storage** — stream to disk/cloud, don't buffer entire file in memory.
- **Cleanup** — remove temp files on error or completion.

## Rules

- Do not put business logic in route handlers — delegate to services.
- Do not trust request body, query params, or headers without validation.
- Do not expose internal error messages in production responses.
- Each endpoint does one thing — no "hidden" side effects.
- Test edge cases: missing fields, wrong types, max length, SQL injection attempts.

## Experience Log

_This skill learns from experience. Mechanism:_

- **Read** `.claude/experience/api-implementation.md` at skill start to benefit from past lessons.
- **Write** to `.claude/experience/api-implementation.md` after use if you learned something new.
- **Format**: `YYYY-MM-DD: <lesson>` — one line per entry.
- **Evolve**: If the same issue repeats 3+ times, update this SKILL.md itself.
