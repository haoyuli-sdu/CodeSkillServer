---
name: "api-test-generate"
description: "Auto-generate comprehensive API tests for REST and GraphQL endpoints with request/response validation"
---

# API Test Generation

I'll generate comprehensive API tests for your REST or GraphQL endpoints with proper validation and assertions.

**Features:**
- Auto-detect API framework (Express, FastAPI, Next.js API routes)
- Generate request/response tests
- Schema validation
- Error handling tests
- Authentication tests


## Phase 1: API Framework Detection

```bash
# Detect API framework efficiently
detect_api_framework() {
    if [ -f "package.json" ]; then
        if grep -q "\"express\"" package.json; then
            echo "express"
        elif grep -q "\"fastify\"" package.json; then
            echo "fastify"
        elif grep -q "\"next\"" package.json; then
            echo "nextjs"
        elif grep -q "\"@apollo/server\"" package.json; then
            echo "apollo"
        fi
    elif [ -f "requirements.txt" ]; then
        if grep -q "fastapi" requirements.txt; then
            echo "fastapi"
        elif grep -q "flask" requirements.txt; then
            echo "flask"
        elif grep -q "django" requirements.txt; then
            echo "django"
        fi
    elif [ -f "go.mod" ]; then
        if grep -q "gin-gonic" go.mod; then
            echo "gin"
        elif grep -q "fiber" go.mod; then
            echo "fiber"
        fi
    fi
}

FRAMEWORK=$(detect_api_framework)

if [ -z "$FRAMEWORK" ]; then
    echo "❌ No API framework detected"
    echo "Supported frameworks:"
    echo "  Node: Express, Fastify, Next.js API routes, Apollo"
    echo "  Python: FastAPI, Flask, Django"
    echo "  Go: Gin, Fiber"
    exit 1
fi

echo "✓ API Framework: $FRAMEWORK"
```

## Phase 2: Endpoint Discovery

```bash
echo ""
echo "Discovering API endpoints..."

# Use Grep to find endpoints efficiently
case $FRAMEWORK in
    express|fastify)
        ENDPOINTS=$(grep -r "\.get\(\\|\.post\(\\|\.put\(\\|\.delete\(\\|\.patch\(" \
                         --include="*.js" --include="*.ts" \
                         --exclude-dir=node_modules \
                         . | head -20)
        ;;
    nextjs)
        # Next.js API routes are file-based
        ENDPOINTS=$(find pages/api app/api -name "*.ts" -o -name "*.js" 2>/dev/null | head -20)
        ;;
    apollo)
        # GraphQL resolvers
        ENDPOINTS=$(grep -r "Query\\|Mutation" --include="*.ts" --include="*.js" \
                         --exclude-dir=node_modules . | head -20)
        ;;
    fastapi)
        ENDPOINTS=$(grep -r "@app\.\(get\|post\|put\|delete\|patch\)" --include="*.py" . | head -20)
        ;;
    flask)
        ENDPOINTS=$(grep -r "@app\.route" --include="*.py" . | head -20)
        ;;
    django)
        ENDPOINTS=$(find . -name "urls.py" -o -name "views.py" | head -20)
        ;;
esac

if [ -z "$ENDPOINTS" ]; then
    echo "⚠️ No API endpoints found"
    exit 1
fi

ENDPOINT_COUNT=$(echo "$ENDPOINTS" | wc -l)
echo "✓ Found $ENDPOINT_COUNT endpoints"
echo ""
echo "Sample endpoints:"
echo "$ENDPOINTS" | head -5 | sed 's/^/  /'
```

## Phase 3: Test Framework Setup

```bash
echo ""
echo "Setting up test framework..."

# Detect or install test framework
if [ "$FRAMEWORK" = "express" ] || [ "$FRAMEWORK" = "fastify" ] || [ "$FRAMEWORK" = "nextjs" ]; then
    # Node.js - use supertest + jest
    if ! grep -q "\"supertest\"" package.json; then
        echo "Installing supertest for API testing..."
        npm install --save-dev supertest @types/supertest
    fi

    if ! grep -q "\"jest\"" package.json; then
        echo "Installing Jest..."
        npm install --save-dev jest ts-jest @types/jest
    fi

    echo "✓ Test framework ready: Jest + Supertest"

elif [ "$FRAMEWORK" = "fastapi" ] || [ "$FRAMEWORK" = "flask" ]; then
    # Python - use pytest + requests
    if ! grep -q "pytest" requirements.txt 2>/dev/null; then
        echo "Add to requirements.txt: pytest requests"
    fi

    echo "✓ Test framework: Pytest"
fi
```

## Phase 4: Generate Test Files

```bash
echo ""
echo "Generating test files..."

mkdir -p tests/api

# Generate test file based on framework
case $FRAMEWORK in
    express|fastapi)
        cat > tests/api/endpoints.test.ts << 'EOF'
import request from 'supertest';
import app from '../src/app'; // Adjust path to your app

describe('API Endpoints', () => {
  describe('GET /api/health', () => {
    it('should return 200 OK', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);

      expect(response.body).toHaveProperty('status');
      expect(response.body.status).toBe('ok');
    });
  });

  describe('GET /api/users', () => {
    it('should return list of users', async () => {
      const response = await request(app)
        .get('/api/users')
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      if (response.body.length > 0) {
        expect(response.body[0]).toHaveProperty('id');
        expect(response.body[0]).toHaveProperty('name');
        expect(response.body[0]).toHaveProperty('email');
      }
    });

    it('should handle query parameters', async () => {
      const response = await request(app)
        .get('/api/users?limit=10&offset=0')
        .expect(200);

      expect(response.body.length).toBeLessThanOrEqual(10);
    });
  });

  describe('POST /api/users', () => {
    it('should create new user', async () => {
      const newUser = {
        name: 'Test User',
        email: 'test@example.com'
      };

      const response = await request(app)
        .post('/api/users')
        .send(newUser)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.name).toBe(newUser.name);
      expect(response.body.email).toBe(newUser.email);
    });

    it('should validate required fields', async () => {
      const invalidUser = {
        name: 'Test User'
        // Missing email
      };

      await request(app)
        .post('/api/users')
        .send(invalidUser)
        .expect(400);
    });

    it('should reject invalid email format', async () => {
      const invalidUser = {
        name: 'Test User',
        email: 'invalid-email'
      };

      await request(app)
        .post('/api/users')
        .send(invalidUser)
        .expect(400);
    });
  });

  describe('GET /api/users/:id', () => {
    it('should return user by ID', async () => {
      const response = await request(app)
        .get('/api/users/1')
        .expect(200);

      expect(response.body).toHaveProperty('id');
      expect(response.body.id).toBe(1);
    });

    it('should return 404 for non-existent user', async () => {
      await request(app)
        .get('/api/users/99999')
        .expect(404);
    });
  });

  describe('PUT /api/users/:id', () => {
    it('should update existing user', async () => {
      const updates = {
        name: 'Updated Name'
      };

      const response = await request(app)
        .put('/api/users/1')
        .send(updates)
        .expect(200);

      expect(response.body.name).toBe(updates.name);
    });
  });

  describe('DELETE /api/users/:id', () => {
    it('should delete user', async () => {
      await request(app)
        .delete('/api/users/1')
        .expect(204);
    });

    it('should return 404 for non-existent user', async () => {
      await request(app)
        .delete('/api/users/99999')
        .expect(404);
    });
  });

  describe('Authentication', () => {
    it('should reject requests without auth token', async () => {
      await request(app)
        .get('/api/protected')
        .expect(401);
    });

    it('should accept requests with valid token', async () => {
      const token = 'valid-token'; // Get from login or fixture

      await request(app)
        .get('/api/protected')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);
    });

    it('should reject invalid tokens', async () => {
      await request(app)
        .get('/api/protected')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);
    });
  });

  describe('Error Handling', () => {
    it('should handle server errors gracefully', async () => {
      // Test endpoint that might throw an error
      const response = await request(app)
        .get('/api/error-test')
        .expect(500);

      expect(response.body).toHaveProperty('error');
    });

    it('should return proper error messages', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({}) // Invalid payload
        .expect(400);

      expect(response.body).toHaveProperty('message');
      expect(typeof response.body.message).toBe('string');
    });
  });
});
EOF

        echo "✓ Created tests/api/endpoints.test.ts"
        ;;

    apollo)
        cat > tests/api/graphql.test.ts << 'EOF'
import { ApolloServer } from '@apollo/server';
import { typeDefs, resolvers } from '../src/schema';

describe('GraphQL API', () => {
  let server: ApolloServer;

  beforeAll(() => {
    server = new ApolloServer({
      typeDefs,
      resolvers,
    });
  });

  describe('Queries', () => {
    it('should query users', async () => {
      const response = await server.executeOperation({
        query: `
          query {
            users {
              id
              name
              email
            }
          }
        `,
      });

      expect(response.body.kind).toBe('single');
      if (response.body.kind === 'single') {
        expect(response.body.singleResult.data?.users).toBeDefined();
      }
    });

    it('should query user by ID', async () => {
      const response = await server.executeOperation({
        query: `
          query GetUser($id: ID!) {
            user(id: $id) {
              id
              name
              email
            }
          }
        `,
        variables: { id: '1' },
      });

      expect(response.body.kind).toBe('single');
      if (response.body.kind === 'single') {
        expect(response.body.singleResult.data?.user).toHaveProperty('id');
      }
    });
  });

  describe('Mutations', () => {
    it('should create user', async () => {
      const response = await server.executeOperation({
        query: `
          mutation CreateUser($input: CreateUserInput!) {
            createUser(input: $input) {
              id
              name
              email
            }
          }
        `,
        variables: {
          input: {
            name: 'Test User',
            email: 'test@example.com',
          },
        },
      });

      expect(response.body.kind).toBe('single');
      if (response.body.kind === 'single') {
        expect(response.body.singleResult.data?.createUser).toHaveProperty('id');
      }
    });
  });
});
EOF

        echo "✓ Created tests/api/graphql.test.ts"
        ;;
esac

# Generate test helpers
cat > tests/api/helpers.ts << 'EOF'
// Test helpers and utilities

export const mockUser = {
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
};

export const mockUsers = [mockUser, { ...mockUser, id: 2, name: 'User 2' }];

export const createAuthToken = (userId: number): string => {
  // Generate test auth token
  return `test-token-${userId}`;
};

export const wait = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};
EOF

echo "✓ Created tests/api/helpers.ts"
```

## Phase 5: Configuration

```bash
# Add test scripts to package.json
echo ""
echo "Add these scripts to package.json:"
cat << 'EOF'

  "scripts": {
    "test:api": "jest tests/api",
    "test:api:watch": "jest tests/api --watch",
    "test:api:coverage": "jest tests/api --coverage"
  }
EOF
```

## Summary

```bash
echo ""
echo "=== API Test Generation Complete! ==="
echo ""
echo "✓ Framework: $FRAMEWORK"
echo "✓ Endpoints discovered: $ENDPOINT_COUNT"
echo "✓ Test files created"
echo ""
echo "📁 Generated files:"
echo "  - tests/api/endpoints.test.ts (or graphql.test.ts)"
echo "  - tests/api/helpers.ts"
echo ""
echo "🚀 Run tests:"
echo "  npm run test:api              # Run API tests"
echo "  npm run test:api:watch        # Watch mode"
echo "  npm run test:api:coverage     # With coverage"
echo ""
echo "📝 Next steps:"
echo "  1. Update test file with actual endpoint paths"
echo "  2. Customize assertions for your data models"
echo "  3. Add authentication setup if needed"
echo "  4. Run tests: npm run test:api"
echo "  5. Add to CI pipeline with /ci-setup"
```

## Best Practices

**API Testing Tips:**
- Test happy paths and error cases
- Validate request/response schemas
- Test authentication and authorization
- Test rate limiting and pagination
- Mock external dependencies

**Integration Points:**
- `/api-validate` - Validate API contracts
- `/ci-setup` - Add to CI pipeline
- `/test` - Run alongside unit tests

**Credits:** API testing patterns based on Supertest documentation, FastAPI testing guide, and industry best practices.

## Token Optimization

**Expected range**: 1,200–2,500 tokens (initial), 300–500 tokens (cache hit)

**Caching**: Caches API endpoint inventory in `.claude/cache/api/endpoints.json` for 7 days. Invalidated when route files change.

**Early exit**: Returns immediately if no API routes found in changed files.

**Patterns used**: Grep-before-Read, early exit, git diff scope default, template-based generation, caching
