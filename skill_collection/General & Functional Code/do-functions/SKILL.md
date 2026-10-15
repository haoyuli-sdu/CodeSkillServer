---
name: "do-functions"
description: "Generate serverless functions with triggers, packages, and scheduled invocations. Use when the user wants to create and deploy DigitalOcean Functions for serverless workloads."
---

## Instructions

You are a DigitalOcean Functions expert. Generate production-ready serverless function configurations with proper project structure, triggers, and deployment workflows.

### Step 1: Gather requirements

Determine from user input or `$ARGUMENTS`:
- **Runtime**: Node.js (18, 20), Python (3.9, 3.11), Go (1.21), PHP (8.1)
- **Trigger type**: HTTP (web function), scheduled (cron), event-driven
- **Purpose**: API endpoint, webhook handler, data processing, scheduled task
- **Dependencies**: external packages, connected resources (databases, Spaces)
- **Scale**: expected invocation rate and concurrency

### Step 2: Generate project structure

Create the DigitalOcean Functions project layout:

```
my-functions/
├── project.yml           # Project configuration
├── packages/
│   ├── api/              # Package: groups related functions
│   │   ├── login/
│   │   │   ├── index.js  # Function handler
│   │   │   └── package.json
│   │   ├── register/
│   │   │   ├── index.js
│   │   │   └── package.json
│   │   └── profile/
│   │       ├── index.py
│   │       └── requirements.txt
│   ├── jobs/
│   │   ├── cleanup/
│   │   │   ├── index.js
│   │   │   └── package.json
│   │   └── report/
│   │       ├── main.go
│   │       └── go.mod
│   └── webhooks/
│       └── stripe/
│           ├── index.js
│           └── package.json
└── .env                  # Local development env vars
```

### Step 3: Generate project.yml

```yaml
# project.yml - DigitalOcean Functions project configuration
packages:
  - name: api
    shared: false
    environment:
      DATABASE_URL: "${DB_URL}"
      JWT_SECRET: "${JWT_SECRET}"
    parameters: {}
    functions:
      - name: login
        runtime: nodejs:20
        web: true
        main: index.handler
        timeout: 10000          # 10 seconds
        memory: 256             # MB
        environment:
          TOKEN_EXPIRY: "3600"
        limits:
          logs: 5               # KB of logs retained
          memory: 256           # MB
          timeout: 10000        # ms

      - name: register
        runtime: nodejs:20
        web: true
        main: index.handler
        timeout: 15000
        memory: 256

      - name: profile
        runtime: python:3.11
        web: true
        main: __main__.main
        timeout: 10000
        memory: 128

  - name: jobs
    environment:
      DATABASE_URL: "${DB_URL}"
    functions:
      - name: cleanup
        runtime: nodejs:20
        web: false
        main: index.handler
        timeout: 300000         # 5 minutes
        memory: 512
        triggers:
          - name: daily-cleanup
            type: scheduler
            cron: "0 3 * * *"   # Every day at 3 AM UTC

      - name: report
        runtime: go:1.21
        web: false
        main: Main
        timeout: 600000         # 10 minutes
        memory: 1024
        triggers:
          - name: weekly-report
            type: scheduler
            cron: "0 8 * * 1"   # Every Monday at 8 AM UTC

  - name: webhooks
    functions:
      - name: stripe
        runtime: nodejs:20
        web: raw                # Raw HTTP access (no JSON wrapping)
        main: index.handler
        timeout: 30000
        memory: 256
        environment:
          STRIPE_WEBHOOK_SECRET: "${STRIPE_WEBHOOK_SECRET}"
```

### Step 4: Generate function handlers

**Node.js HTTP function (web: true):**
```javascript
// packages/api/login/index.js
const jwt = require('jsonwebtoken');

async function handler(event, context) {
  // event contains: http method, headers, path, body
  const { http, ...params } = event;
  const method = http.method;
  const headers = http.headers;
  const path = http.path;

  if (method !== 'POST') {
    return {
      statusCode: 405,
      headers: { 'Content-Type': 'application/json' },
      body: { error: 'Method not allowed' },
    };
  }

  try {
    const { email, password } = params;

    // Validate credentials (connect to database)
    const user = await authenticateUser(email, password);

    if (!user) {
      return {
        statusCode: 401,
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'Invalid credentials' },
      };
    }

    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: process.env.TOKEN_EXPIRY || '1h' }
    );

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store',
      },
      body: { token, user: { id: user.id, email: user.email } },
    };
  } catch (error) {
    console.error('Login error:', error.message);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: { error: 'Internal server error' },
    };
  }
}

module.exports = { handler };
```

**Node.js raw webhook handler (web: raw):**
```javascript
// packages/webhooks/stripe/index.js
const crypto = require('crypto');

function handler(event, context) {
  const { http } = event;
  const signature = http.headers['stripe-signature'];
  const rawBody = event.__ow_body; // Raw body for signature verification

  // Verify webhook signature
  const expectedSig = crypto
    .createHmac('sha256', process.env.STRIPE_WEBHOOK_SECRET)
    .update(rawBody)
    .digest('hex');

  if (!crypto.timingSafeEqual(
    Buffer.from(signature.split(',').find(s => s.startsWith('v1=')).slice(3)),
    Buffer.from(expectedSig)
  )) {
    return { statusCode: 401, body: { error: 'Invalid signature' } };
  }

  const payload = JSON.parse(rawBody);

  switch (payload.type) {
    case 'payment_intent.succeeded':
      // Handle successful payment
      console.log('Payment succeeded:', payload.data.object.id);
      break;
    case 'customer.subscription.deleted':
      // Handle subscription cancellation
      console.log('Subscription cancelled:', payload.data.object.id);
      break;
    default:
      console.log('Unhandled event type:', payload.type);
  }

  return { statusCode: 200, body: { received: true } };
}

module.exports = { handler };
```

**Python function:**
```python
# packages/api/profile/__main__.py
import os
import json

def main(event, context):
    """Get user profile by ID."""
    http = event.get('http', {})
    method = http.get('method', 'GET')

    if method != 'GET':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'}),
        }

    user_id = event.get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'user_id parameter required'}),
        }

    try:
        # Fetch user from database
        user = get_user_profile(user_id)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(user),
        }
    except Exception as e:
        print(f'Profile error: {e}')
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'}),
        }
```

**Go function:**
```go
// packages/jobs/report/main.go
package main

import (
    "fmt"
    "os"
    "time"
)

type Response struct {
    StatusCode int               `json:"statusCode"`
    Headers    map[string]string `json:"headers"`
    Body       map[string]interface{} `json:"body"`
}

func Main(event map[string]interface{}) Response {
    dbURL := os.Getenv("DATABASE_URL")
    now := time.Now()

    fmt.Printf("Generating weekly report at %s\n", now.Format(time.RFC3339))

    // Generate report logic here
    report := generateReport(dbURL)

    return Response{
        StatusCode: 200,
        Headers:    map[string]string{"Content-Type": "application/json"},
        Body: map[string]interface{}{
            "generated_at": now.Format(time.RFC3339),
            "report":       report,
        },
    }
}
```

### Step 5: Dependency management

**Node.js (package.json per function):**
```json
{
  "name": "login",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "jsonwebtoken": "^9.0.0",
    "pg": "^8.12.0"
  }
}
```

**Python (requirements.txt per function):**
```
psycopg2-binary==2.9.9
pyjwt==2.8.0
requests==2.31.0
```

**Go (go.mod per function):**
```
module report

go 1.21

require (
    github.com/jackc/pgx/v5 v5.5.0
)
```

Dependencies are automatically installed during the build process. Each function is built independently.

### Step 6: Connected resources

Connect managed databases and other resources to functions:

```yaml
# In project.yml, reference connected resources
packages:
  - name: api
    environment:
      # These are injected when you connect a resource via the dashboard or CLI
      DATABASE_URL: "${db.DATABASE_URL}"
      DATABASE_CA: "${db.CA_CERT}"
```

```bash
# Connect a database to the functions namespace
doctl serverless connect <db-id>

# List connected resources
doctl serverless status --connected-resources
```

### Step 7: Local development and testing

```bash
# Install the serverless plugin
doctl serverless install

# Initialize a new project
doctl serverless init my-functions --language js

# Deploy to the cloud
doctl serverless deploy my-functions

# Deploy a single function
doctl serverless deploy my-functions --include "api/login"

# Invoke a function
doctl serverless functions invoke api/login \
  --param email=user@example.com \
  --param password=secret

# Invoke via HTTP (web functions)
curl -X POST "https://<namespace-id>.doserverless.co/api/v1/web/<namespace>/api/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'

# View function logs
doctl serverless activations logs --function api/login --follow

# List activations (invocations)
doctl serverless activations list --function api/login --limit 10

# Get activation result
doctl serverless activations result <activation-id>

# Watch for changes and redeploy
doctl serverless watch my-functions
```

### Step 8: Terraform deployment

```hcl
resource "digitalocean_app" "functions_app" {
  spec {
    name   = "my-functions"
    region = "nyc"

    function {
      name       = "api"
      source_dir = "packages/api"

      github {
        repo           = "myorg/my-functions"
        branch         = "main"
        deploy_on_push = true
      }

      routes {
        path = "/api"
      }

      env {
        key   = "DATABASE_URL"
        value = digitalocean_database_cluster.db.uri
        type  = "SECRET"
      }
    }
  }
}
```

### Step 9: Function limits and configuration

| Limit | Value |
|-------|-------|
| Timeout | Max 600 seconds (10 minutes) |
| Memory | 128MB to 1024MB |
| Payload size (request) | 1MB (web), 5MB (non-web) |
| Payload size (response) | 1MB |
| Concurrent executions | 100 per namespace (can request increase) |
| Functions per namespace | 100 |
| Packages per project | 25 |
| Environment variables | 100 per function |
| Build size | 250MB uncompressed |

### Step 10: Scheduled functions (cron triggers)

```yaml
# project.yml - scheduled function
packages:
  - name: cron
    functions:
      - name: daily-backup
        runtime: nodejs:20
        web: false
        main: index.handler
        timeout: 300000
        memory: 512
        triggers:
          - name: daily-backup-trigger
            type: scheduler
            cron: "0 2 * * *"     # 2 AM UTC daily

      - name: hourly-sync
        runtime: python:3.11
        web: false
        main: __main__.main
        timeout: 60000
        memory: 256
        triggers:
          - name: hourly-sync-trigger
            type: scheduler
            cron: "0 * * * *"     # Every hour

      - name: monthly-cleanup
        runtime: nodejs:20
        web: false
        main: index.handler
        timeout: 600000
        memory: 1024
        triggers:
          - name: monthly-cleanup-trigger
            type: scheduler
            cron: "0 0 1 * *"     # First day of each month at midnight
```

```bash
# Manage triggers
doctl serverless triggers list
doctl serverless triggers get <trigger-name>
doctl serverless triggers create <trigger-name> \
  --function <package>/<function> \
  --type scheduler \
  --cron "0 * * * *"
```

### Comparison with other serverless platforms

| Feature | DO Functions | AWS Lambda | Cloudflare Workers |
|---------|-------------|------------|-------------------|
| Runtimes | Node, Python, Go, PHP | Node, Python, Go, Java, .NET, Ruby, Rust | JavaScript, WASM |
| Max timeout | 10 min | 15 min | 30s (free), 15min (paid) |
| Max memory | 1024MB | 10240MB | 128MB |
| Cold start | ~200ms | ~100-500ms | <1ms (V8 isolates) |
| Free tier | 25,000 invocations/mo | 1M invocations/mo | 100,000 requests/day |
| Pricing | $0.0000185/GB-s | $0.0000166667/GB-s | $0.50/million requests |
| VPC access | Via connected resources | Via VPC config | No |

### Best practices

- Use `web: true` for HTTP-triggered functions that return JSON
- Use `web: raw` for webhooks that need access to the raw request body
- Use `web: false` for background jobs and scheduled tasks
- Keep functions small and focused on a single task
- Use environment variables for all configuration; never hardcode secrets
- Use packages to group related functions that share environment variables
- Set appropriate timeout and memory limits to avoid paying for unused resources
- Use connection pooling or keep-alive for database connections across warm invocations
- Log structured JSON for easier debugging and monitoring
- Version your function code with Git and deploy via CI/CD

### Anti-patterns to avoid

- Do not build long-running processes as functions; use workers or Droplets instead
- Do not store state in function memory between invocations; use databases or Spaces
- Do not include large dependencies that inflate build size; keep functions lean
- Do not use functions for real-time communication (WebSockets); use Droplets instead
- Do not process files larger than the payload limit within functions
- Do not rely on function warm starts for correctness; design for cold starts
- Do not skip error handling; unhandled exceptions terminate the function silently

### Cost optimization tips

- Free tier includes 25,000 invocations and 90,000 GB-seconds per month
- Set the minimum memory required for each function (128MB to start)
- Use shorter timeouts to prevent runaway costs from stuck invocations
- Use scheduled triggers instead of external cron services
- Batch small operations into fewer invocations when possible
- Use the `doctl serverless activations list` command to monitor invocation counts
- Consider App Platform workers for always-running background processes (more predictable cost)
- Use connected resources (managed databases) instead of provisioning separate infrastructure
