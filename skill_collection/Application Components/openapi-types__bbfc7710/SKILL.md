---
name: "openapi-types"
description: "Generate TypeScript types and client SDKs from OpenAPI specs"
---

# OpenAPI Type Generator

I'll generate TypeScript types, client SDKs, and Zod schemas from OpenAPI 3.0 specifications.

Arguments: `$ARGUMENTS` - path to OpenAPI spec file

**Features:**
- TypeScript types from OpenAPI schemas
- Type-safe fetch/axios client SDK
- Zod schemas for runtime validation
- React hooks for data fetching
- Integration with `/api-docs-generate`

## Token Optimization

**Expected range**: 2,000–3,000 tokens (initial), 100 tokens (types current)

**Caching**: No persistent caching — validates types against current spec on each run.

**Early exit**: Returns immediately if generated types are already in sync with the OpenAPI spec.

**Patterns used**: Grep-before-Read, early exit, Bash for system queries
