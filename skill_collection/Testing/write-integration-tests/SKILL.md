---
name: "write-integration-tests"
description: "This skill defines the authoritative process for creating and maintaining integration tests within the Nexus Ecosystem. Integration tests follow a **'Black Box' API + 'White Box' Data Setup** philosophy."
---

# Skill: Write Integration Tests

This skill defines the authoritative process for creating and maintaining integration tests within the Nexus Ecosystem. Integration tests follow a **"Black Box" API + "White Box" Data Setup** philosophy.

## 1. Core Principles

- **Orchestration**: Use `vitest` for all test runners, assertions, and lifecycle hooks.
- **Data Setup (White Box)**: Use the `Factory` helper to seed the database directly. Do NOT use the API for prerequisite data.
- **API Interaction (Black Box)**: Use the `ApiClient` for all HTTP interactions.
- **Authentication**: Use the `client.as()` method to set the actor context. Never manually set headers.
- **Assertion Sequence**: ALWAYS verify the HTTP status code as the first assertion.

## 2. Mandatory Patterns

### Standardized Imports

Imports MUST use the `@tests/integration/lib/` alias. Do NOT use relative imports for test infrastructure.

**CRITICAL**: Do NOT insert spaces before the `@` symbol in import paths or aliases.

```typescript
import { ApiClient } from '@tests/integration/lib/client';
import { Factory } from '@tests/integration/lib/factory';
```

### API Client & Auth

The `ApiClient` handles session persistence and authentication logic.

```typescript
const client = new ApiClient();
// Authenticate as a specific user role defined in models.yaml
await client.as('user', { role: 'ADMIN' });
```

### Data Setup

Use `Factory.create` for speed and reliability.

```typescript
const user = await Factory.create('user', { email: 'test@example.com' });
```

## 3. Standard Test Structure

```typescript
import { describe, it, expect, beforeAll } from 'vitest';
import { ApiClient } from '@tests/integration/lib/client';
import { Factory } from '@tests/integration/lib/factory';

describe('Module: {Name} API', () => {
  let client: ApiClient;

  beforeAll(() => {
    client = new ApiClient();
  });

  it('should {perform action} successfully', async () => {
    // 1. Setup Data
    await Factory.create('some_model', { ... });

    // 2. Auth
    await client.as('user', { role: 'ADMIN' });

    // 3. Act
    const res = await client.get('/api/path');

    // 4. Assert (Status FIRST)
    expect(res.status).toBe(200);
    expect(res.body.data).toBeDefined();
  });
});
```

## 4. Directory Structure

To maintain separation between machine-maintained and human-authored tests, adhere to the following directory structure:

- **Generated Tests**: `tests/integration/api/generated/{entity}/`
  - These files are managed by the generator.
  - They contain the `// GENERATED CODE` header.
  - **DO NOT EDIT** manually.

- **Manual Tests**: `tests/integration/api/manual/`
  - Place custom, complex, or multi-step integration scenarios here.
  - You typically create these files manually.

## 5. Generated File Protection

Machine-generated tests (usually in `generated/` directories) include a protection header.
**DO NOT MODIFY** files containing:

```typescript
// GENERATED CODE - DO NOT MODIFY
```

Changes to these tests must be made by updating `api.yaml` or `models.yaml` and regenerating.
