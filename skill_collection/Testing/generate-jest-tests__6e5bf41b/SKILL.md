---
name: "generate-jest-tests"
description: "Generates a Jest test suite for backend API endpoints and controllers."
---

# Skill — Generate Jest Tests

## What You Do
Read the backend code and produce a comprehensive Jest test suite covering
API endpoints and business logic.

## Steps
1. Read the [BACKEND] GitHub Issue — understand what was built
2. Read `src/backend/routes/` — identify all endpoints
3. Read `src/backend/controllers/` — understand business logic
4. Read `docs/design/design-doc.md` — confirm API contracts
5. Generate test files in `src/backend/__tests__/`
6. Generate Prisma mock in `src/backend/__tests__/__mocks__/prisma.ts`
7. Raise PR with all test files

## Test File Structure
```typescript
// Feature: {feature name}
// Source: GitHub Issue #{number}

import request from 'supertest'
import app from '../index'

describe('{Feature} API', () => {

  let authToken: string

  beforeAll(async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@foodorder.com', password: 'password123' })
    authToken = res.body.token
  })

  describe('{METHOD} /api/{path}', () => {
    it('should return {status} on success', async () => {
      // arrange — set up test data
      // act — make the request
      // assert — verify response
    })

    it('should return 401 without auth token', async () => {})
    it('should return 400 if required fields missing', async () => {})
  })

})
```

## Coverage Requirements
Every endpoint must have at minimum:

| Test Type | What It Verifies |
|-----------|-----------------|
| Happy path | Correct input returns correct status and response shape |
| Auth test | No token returns 401 |
| Validation | Missing required fields returns 400 |
| Edge case | At least one edge case per endpoint |

## Prisma Mock Setup
Always generate this mock file for unit tests:
```typescript
// src/backend/__tests__/__mocks__/prisma.ts
import { PrismaClient } from '@prisma/client'
import { mockDeep, mockReset, DeepMockProxy } from 'jest-mock-extended'

export const prismaMock = mockDeep<PrismaClient>()

beforeEach(() => {
  mockReset(prismaMock)
})
```

## Testing Patterns

### Arrange / Act / Assert — always use this pattern
```typescript
it('should add item to cart', async () => {
  // arrange
  const payload = { menuItemId: 1, quantity: 1 }

  // act
  const res = await request(app)
    .post('/api/cart/items')
    .set('Authorization', `Bearer ${authToken}`)
    .send(payload)

  // assert
  expect(res.status).toBe(201)
  expect(res.body).toHaveProperty('id')
  expect(res.body.menuItemId).toBe(1)
})
```

### Response shape validation — always check shape not just status
```typescript
// CORRECT
expect(res.body).toHaveProperty('items')
expect(res.body.items).toBeInstanceOf(Array)

// WRONG — only checking status is not enough
expect(res.status).toBe(200)
```

## Edge Cases to Always Test
For any cart-like feature check:
- Add same item twice → quantity increments not duplicates
- Remove item not in cart → 404
- Get empty cart → returns empty items array not error
- Update quantity to 0 → 400 or removes item

For any auth-protected feature check:
- Expired token → 401
- Malformed token → 401
- Missing Authorization header → 401

## Example Test File (Cart API)
```typescript
describe('Cart API', () => {
  describe('POST /api/cart/items', () => {
    it('should add item and return 201', async () => {})
    it('should return 401 without token', async () => {})
    it('should return 400 if menuItemId missing', async () => {})
    it('should increment quantity if item already in cart', async () => {})
  })

  describe('DELETE /api/cart/items/:id', () => {
    it('should remove item and return 200', async () => {})
    it('should return 401 without token', async () => {})
    it('should return 404 if item not in cart', async () => {})
  })
})
```
