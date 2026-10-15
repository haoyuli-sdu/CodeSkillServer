---
name: "customgpt-api"
description: "CustomGPT API integration for developers. Generate code for agents, conversations, sources, analytics. Use when: API integration, SDK code, CustomGPT endpoints, REST API."
---

# CustomGPT API Integration

**Role**: Developer API Assistant

I help developers write code that integrates with CustomGPT.ai APIs.
I know all endpoints, authentication patterns, and best practices.

## Capabilities

- Generate API integration code (Python, JavaScript, curl)
- Authentication setup (API keys, Bearer tokens)
- All endpoint patterns (agents, conversations, sources, analytics)
- Error handling and retry logic
- SDK usage patterns

## When to Use

**DO use** for:
- Writing code to call CustomGPT APIs
- Setting up authentication
- Creating/managing agents programmatically
- Building conversation flows
- Fetching analytics data

**DO NOT use** for:
- Querying knowledge bases (use customgpt-rag)
- General REST API questions unrelated to CustomGPT

## Authentication

Base URL: `https://app.customgpt.ai`

All requests require Bearer token:
```python
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
```

Get your API key from: Settings > API Keys in the CustomGPT dashboard.

## Endpoint Reference

### Agents (Projects)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/projects | List all agents |
| POST | /api/v1/projects | Create agent |
| GET | /api/v1/projects/{id} | Get agent |
| POST | /api/v1/projects/{id} | Update agent |
| DELETE | /api/v1/projects/{id} | Delete agent |
| POST | /api/v1/projects/{id}/replicate | Clone agent |
| GET | /api/v1/projects/{id}/stats | Get stats |

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/projects/{id}/conversations | Create conversation |
| GET | /api/v1/projects/{id}/conversations | List conversations |
| GET | /api/v1/projects/{id}/conversations/{sid} | Get conversation |
| DELETE | /api/v1/projects/{id}/conversations/{sid} | Delete conversation |
| POST | /api/v1/projects/{id}/conversations/{sid}/messages | Send message |
| GET | /api/v1/projects/{id}/conversations/{sid}/messages | Get messages |
| POST | /api/v1/projects/{id}/chat/completions | OpenAI-compatible |
| POST | /api/v1/projects/{id}/conversations/{sid}/share | Share conversation |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/projects/{id}/conversations/{sid}/messages/{mid} | Get message |
| POST | /api/v1/projects/{id}/conversations/{sid}/messages/{mid}/feedback | Add feedback |
| GET | /api/v1/projects/{id}/conversations/{sid}/messages/{mid}/claims | Get claims |
| GET | /api/v1/projects/{id}/conversations/{sid}/messages/{mid}/trust-score | Get trust score |
| POST | /api/v1/projects/{id}/conversations/{sid}/messages/{mid}/verify | Verify response |

### Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/projects/{id}/sources | List sources |
| POST | /api/v1/projects/{id}/sources | Add source |
| GET | /api/v1/projects/{id}/sources/{sid} | Get source |
| PUT | /api/v1/projects/{id}/sources/{sid} | Update source |
| DELETE | /api/v1/projects/{id}/sources/{sid} | Remove source |
| PUT | /api/v1/projects/{id}/sources/{sid}/instant-sync | Sync now |

### Pages (Content)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/projects/{id}/pages | List pages |
| DELETE | /api/v1/projects/{id}/pages/{pid} | Delete page |
| POST | /api/v1/projects/{id}/pages/{pid}/reindex | Reindex page |
| GET | /api/v1/projects/{id}/pages/{pid}/labels | Get labels |
| POST | /api/v1/projects/{id}/pages/{pid}/labels | Add labels |
| DELETE | /api/v1/projects/{id}/pages/{pid}/labels | Remove labels |
| GET | /api/v1/projects/{id}/pages/{pid}/metadata | Get metadata |
| PUT | /api/v1/projects/{id}/pages/{pid}/metadata | Update metadata |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/projects/{id}/reports/intelligence | Customer insights |
| GET | /api/v1/projects/{id}/reports/traffic | Traffic metrics |
| GET | /api/v1/projects/{id}/reports/queries | Query analytics |
| GET | /api/v1/projects/{id}/reports/conversations | Conv metrics |
| GET | /api/v1/projects/{id}/reports/leads | Lead data |
| POST | /api/v1/projects/{id}/reports/leads/export | Export leads |

### Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/projects/{id}/settings | Get settings |
| PUT | /api/v1/projects/{id}/settings | Update settings |
| GET | /api/v1/projects/{id}/personas | List personas |
| POST | /api/v1/projects/{id}/personas | Create persona |
| PUT | /api/v1/projects/{id}/personas/{pid} | Update persona |

### Citations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/projects/{id}/open-graph | Get Open Graph data |

### Labels

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/projects/{id}/labels | List labels |
| POST | /api/v1/projects/{id}/labels | Create label |
| GET | /api/v1/projects/{id}/labels/{lid} | Get label |
| PUT | /api/v1/projects/{id}/labels/{lid} | Update label |
| DELETE | /api/v1/projects/{id}/labels/{lid} | Delete label |
| GET | /api/v1/projects/{id}/labels/user-mappings | Get user mappings |
| POST | /api/v1/projects/{id}/labels/user-mappings | Set user mappings |

### Licenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/licenses | List licenses |
| POST | /api/v1/licenses | Create license |
| GET | /api/v1/licenses/{id} | Get license |
| PUT | /api/v1/licenses/{id} | Update license |
| DELETE | /api/v1/licenses/{id} | Delete license |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/user/profile | Get profile |
| GET | /api/v1/user/team | Search team |
| GET | /api/v1/user/limits | Usage limits |

## Code Patterns

### Python: Create Agent

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "https://app.customgpt.ai"

response = requests.post(
    f"{BASE_URL}/api/v1/projects",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "project_name": "My Knowledge Base",
        "sitemap_path": "https://example.com/sitemap.xml"
    }
)
agent = response.json()["data"]
print(f"Created agent: {agent['id']}")
```

### Python: Send Message (Get RAG Response)

```python
import requests

project_id = "your_project_id"
session_id = "your_session_id"  # From create conversation

response = requests.post(
    f"{BASE_URL}/api/v1/projects/{project_id}/conversations/{session_id}/messages",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"prompt": "What is your return policy?"}
)
data = response.json()["data"]
answer = data["openai_response"]
citations = data.get("citations", [])
```

### Python: Create Conversation

```python
response = requests.post(
    f"{BASE_URL}/api/v1/projects/{project_id}/conversations",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"name": "Support Chat"}
)
session_id = response.json()["data"]["session_id"]
```

### Python: OpenAI-Compatible Format

```python
response = requests.post(
    f"{BASE_URL}/api/v1/projects/{project_id}/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "messages": [{"role": "user", "content": "Hello, what can you help with?"}],
        "stream": False
    }
)
completion = response.json()
```

### Python: Streaming Response

```python
response = requests.post(
    f"{BASE_URL}/api/v1/projects/{project_id}/conversations/{session_id}/messages",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"prompt": "Explain our pricing", "stream": True},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode())
```

### JavaScript: List Agents

```javascript
const API_KEY = "your_api_key";
const BASE_URL = "https://app.customgpt.ai";

const response = await fetch(`${BASE_URL}/api/v1/projects`, {
  headers: { "Authorization": `Bearer ${API_KEY}` }
});
const { data } = await response.json();
console.log(`Found ${data.length} agents`);
```

### JavaScript: Send Message

```javascript
const response = await fetch(
  `${BASE_URL}/api/v1/projects/${projectId}/conversations/${sessionId}/messages`,
  {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ prompt: "What topics do you cover?" })
  }
);
const { data } = await response.json();
console.log(data.openai_response);
```

### curl: Quick Test

```bash
# List agents
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://app.customgpt.ai/api/v1/projects

# Send message
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}' \
  "https://app.customgpt.ai/api/v1/projects/{id}/conversations/{sid}/messages"
```

## Error Handling

```python
import time

def call_api(url, method="GET", data=None, max_retries=3):
    headers = {"Authorization": f"Bearer {API_KEY}"}

    for attempt in range(max_retries):
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise Exception("Invalid API key - check your credentials")
        elif response.status_code == 403:
            raise Exception("Access denied - check permissions")
        elif response.status_code == 404:
            raise Exception("Resource not found")
        elif response.status_code == 429:
            wait = 2 ** attempt * 10  # Exponential backoff
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
        elif response.status_code >= 500:
            time.sleep(5)  # Server error, brief wait
        else:
            raise Exception(f"API error: {response.status_code}")

    raise Exception("Max retries exceeded")
```

## Response Format

All endpoints return:

```json
{
  "status": "success",
  "data": { ... }
}
```

Error responses:

```json
{
  "status": "error",
  "message": "Error description"
}
```

## Rate Limits

- Respect 429 responses with exponential backoff
- Batch operations where possible
- Cache responses when appropriate

## Related

- API Reference: https://docs.customgpt.ai/reference
- Getting Started: https://docs.customgpt.ai/docs/welcome
- MCP Integration: https://docs.customgpt.ai/mcp
- customgpt-rag skill: For querying knowledge bases via MCP
