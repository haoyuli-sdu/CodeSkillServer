---
name: "project-scaffolding"
description: ">"
---

# Project Scaffolding

Scaffold a new project with any combination of: GitHub Actions, Dev Containers, Backend, Frontend, and End-to-End testing.

## When to Use This Skill

Use this skill when the user:

- Asks to "create a new project", "scaffold an app", or "bootstrap a project"
- Wants to set up a full-stack application from scratch
- Needs CI/CD pipelines, dev containers, backend, frontend, or E2E testing configured
- Says "set up a monorepo" or "generate project structure"

## Important: Gather Requirements First

**Before generating any files, you MUST ask the user clarification questions to determine exactly which parts they need.** A project can include one or more of the following top-level parts. Present them as a checklist and ask the user to pick:

1. **GitHub Actions** — CI/CD workflows
2. **Dev Container** — Development container configuration
3. **Backend** — Server-side application
4. **Frontend** — Client-side application
5. **E2E Testing** — End-to-end tests spanning backend + frontend together

Once the user selects which parts they want, drill down into each selected part using the detailed questions below.

---

## Part 1: GitHub Actions

If the user wants GitHub Actions, ask which workflow(s) they need (they can pick any combination):

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **PR Build** | Pull request to default branch | Build and publish a **pre-release** package |
| **Commit Build** | Push/commit to default branch | Build and publish a **latest** package |
| **Tag Build** | Git tag push (e.g. `v*`) | Build and publish a **stable version** package |

### PR Build Workflow

If selected, create `.github/workflows/build.yml`:

```yaml
name: PR Build

on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
...
```

### Commit Build Workflow

If selected, add a new trigger to `.github/workflows/build.yml` and a step to publish the latest version:

```yaml
on:
  push:
    branches: [main]
...
    steps:
      - name: publish latest version
        run: |
          echo "Publishing latest version"
          # Add actual publish commands based on the package registry

```

### Tag Build Workflow

If selected, add new triggers to `.github/workflows/build.yml` and a step to publish the stable version:

```yaml
on:
  push:
    tags: ['v*']
...
    steps:
      - name: publish stable version
        run: |
          echo "Publishing stable version"
          # Add actual publish commands based on the package registry
```

**Adapt workflows** to the chosen tech stack. If dockerized use docker to build, test and etc. For C# backends, use `actions/setup-dotnet@v4` and `dotnet build`/`dotnet test`/`dotnet publish`. For Node.js, use the templates above. If both backend and frontend exist, create jobs for each or a matrix build.

---

## Part 2: Dev Containers

Ask the user which dev container setup they prefer:

| Option | Description |
|--------|-------------|
| **Separate** | One dev container per project part (backend, frontend, etc.) |
| **Unified** | A single dev container for the entire project |
| **Both** | Separate containers for each part AND a unified one that runs everything |

### Unified Dev Container

Create `.devcontainer/devcontainer.json`:

```jsonc
{
  "name": "<project-name>",
  "image": "mcr.microsoft.com/devcontainers/universal:2",
  // Adjust features based on chosen tech stack
  "features": {
    "ghcr.io/devcontainers/features/node:1": { "version": "20" },
    "ghcr.io/devcontainers/features/dotnet:2": { "version": "8.0" }
  },
  "forwardPorts": [],
  "postCreateCommand": "echo 'Dev container ready!'",
  "customizations": {
    "vscode": {
      "extensions": []
    }
  }
}
```

### Separate Dev Containers

Create one `devcontainer.json` per part, for example:

- `backend/.devcontainer/devcontainer.json` — with C# / Node.js tools
- `frontend/.devcontainer/devcontainer.json` — with Node.js, npm, and frontend tooling

Tailor the `image`, `features`, and `extensions` to match the selected technology for each part.

### Containerized Backend Dev Container

If the backend is containerized, use `docker-compose.yml` inside the dev container config:

```jsonc
{
  "name": "<project-name>-backend",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace"
}
```

---

## Part 3: Backend

Ask the user:

1. **Language**: C# (default) or Node.js?
2. **Containerized?** Should the backend run in a Docker container?
3. **Persisted data?** If yes, what storage — JSON/text file, SQLite, PostgreSQL, MongoDB, SQL Server, or other?
4. **Tests?** Which testing levels:
   - **Unit tests** — test individual functions/classes in isolation
   - **Integration tests** — mock application boundaries (DB, external APIs) and test components together
   - **E2E with actual DB** — run tests against a real database instance

### C# Backend (default)

Create the following structure:

**Key points:**: regardless of the choices, you should use latest syntax and best practices.

```
backend/
├── src/
│   └── <ProjectName>/
│       ├── <ProjectName>.csproj
│       ├── Program.cs
│       ├── appsettings.json
│       ├── Controllers/
│       ├── Models/
│       └── Services/
├── tests/
│   ├── <ProjectName>.UnitTests/
│   │   └── <ProjectName>.UnitTests.csproj
│   ├── <ProjectName>.IntegrationTests/
│   │   └── <ProjectName>.IntegrationTests.csproj
│   └── <ProjectName>.E2ETests/
│       └── <ProjectName>.E2ETests.csproj
├── Dockerfile          (if containerized)
├── docker-compose.yml  (if containerized)
└── <ProjectName>.slnx
```

**Key C# details:**
- Use ASP.NET Core minimal API or controller-based API (ask user preference)
- For unit tests, use xUnit (default) or NUnit
- For integration tests, use `WebApplicationFactory<T>` with mocked services
- For E2E tests with actual DB, use Testcontainers for .NET to spin up a real DB in Docker
- For data persistence:
  - JSON/Text file: use `System.Text.Json` + file I/O
  - SQLite: use EF Core with SQLite provider
  - PostgreSQL: use EF Core with Npgsql provider
  - SQL Server: use EF Core with SQL Server provider
  - MongoDB: use MongoDB.Driver

### Node.js Backend

Create the following structure:

```
backend/
├── src/
│   ├── index.ts
│   ├── routes/
│   ├── models/
│   ├── services/
│   └── middleware/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── package.json
├── tsconfig.json
├── Dockerfile          (if containerized)
└── docker-compose.yml  (if containerized)
```

**Key Node.js details:**
- Use Express.js (default) or Fastify (ask user)
- TypeScript by default
- For unit tests, use Jest (default) or Vitest
- For integration tests, use Supertest with mocked dependencies
- For E2E tests with actual DB, use Testcontainers for Node.js
- For data persistence:
  - JSON/Text file: native `fs` module with a simple file-based store
  - SQLite: use better-sqlite3 or Prisma with SQLite
  - PostgreSQL: use Prisma or pg driver
  - MongoDB: use Mongoose or MongoDB native driver

### Containerized Backend

If containerized, create:

**Dockerfile:**
```dockerfile
# Adapt FROM image to chosen language
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**docker-compose.yml** (include DB service if persisted data is selected):
```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
    environment:
      DATABASE_URL: "postgresql://postgres:postgres@db:5432/appdb"

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  db-data:
```

Adapt the DB service based on the chosen database engine.

---

## Part 4: Frontend

Ask the user:

1. **Framework/Build tool**: React + Vite (default), Next.js, or other?
2. **Styling**: Tailwind CSS (default) or SASS?
3. **Dark theme support?**
4. **Multilingual (i18n)?**
5. **PWA (Progressive Web App)?**
6. **Fake backend?** Use `rest_api_faker` for frontend development without a running backend?
7. **Tests?**
   - **Unit (component) tests**: Jest (default), Vitest, or other?
   - **Integration tests**: Playwright (default), Cypress, or other? Test against fake server or actual backend?
8. **Package manager**: pnpm (default), npm, or yarn?

### React + Vite (default)

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── manifest.json       (if PWA)
│   └── locales/            (if multilingual)
│       ├── en/
│       │   └── translation.json
│       └── <other-lang>/
│           └── translation.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   ├── i18n/               (if multilingual)
│   │   └── i18n.ts
│   └── __tests__/          (if unit tests)
├── tests/
│   └── integration/        (if integration tests)
│       └── example.spec.ts
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts      (if Tailwind)
├── postcss.config.js       (if Tailwind)
├── playwright.config.ts    (if Playwright integration tests)
├── cypress.config.ts       (if Cypress integration tests)
└── db.json                 (if fake backend)
```

### Next.js

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── manifest.json       (if PWA)
│   └── locales/            (if multilingual)
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   ├── hooks/
│   ├── services/
│   └── i18n/               (if multilingual)
├── tests/
│   ├── unit/               (if unit tests)
│   └── integration/        (if integration tests)
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts      (if Tailwind)
├── postcss.config.js       (if Tailwind)
└── db.json                 (if fake backend)
```

### Styling: Tailwind CSS (default)

Install and configure Tailwind CSS:
- Add `tailwindcss`, `@tailwindcss/postcss`, and `postcss` as dev dependencies
- Create `tailwind.config.ts` with `content` paths pointing to `./src/**/*.{ts,tsx}`
- Create `postcss.config.js` with Tailwind plugin
- Add Tailwind directives to the main CSS file: `@tailwind base; @tailwind components; @tailwind utilities;`

### Styling: SASS

- Install `sass` as a dev dependency
- Rename `.css` files to `.scss`
- Set up a SASS folder structure: `src/styles/` with `_variables.scss`, `_mixins.scss`, `main.scss`

### Dark Theme

If dark theme is requested:
- **Tailwind**: Use `darkMode: 'class'` in `tailwind.config.ts`. Create a theme toggle component that adds/removes the `dark` class on `<html>`. Use `dark:` variants in class names
- **SASS**: Create `_themes.scss` with CSS custom properties for light/dark themes. Create a toggle component that switches a `data-theme` attribute on `<html>`

### Multilingual (i18n)

- Install `react-i18next` and `i18next`
- Create `src/i18n/i18n.ts` with language configuration
- Create `public/locales/<lang>/translation.json` files for each language
- Wrap the app with `I18nextProvider`
- Ask the user which languages to support (default: English + one additional)

### PWA

- For Vite: install `vite-plugin-pwa` and configure in `vite.config.ts`
- For Next.js: install `next-pwa` and configure in `next.config.ts`
- Create `public/manifest.json` with app name, icons, theme colors
- Add a service worker registration

### Fake Backend (rest_api_faker)

- Install `rest_api_faker` as a dev dependency: `npm install --save-dev rest_api_faker`
- Create `db.json` at the frontend root with mock data structure
- Add a script in `package.json`: `"fake-api": "rest_api_faker --port 3001 --db db.json"`
- Configure API base URL to switch between fake and real backend via environment variables

### Frontend Unit Tests

- **Jest** (default): Install `jest`, `@testing-library/react`, `@testing-library/jest-dom`, `ts-jest`. Create `jest.config.ts`
- **Vitest**: Install `vitest`, `@testing-library/react`, `@testing-library/jest-dom`. Configure in `vite.config.ts`
- Create example test in `src/__tests__/App.test.tsx`

### Frontend Integration Tests

- **Playwright** (default): Install `@playwright/test`. Create `playwright.config.ts` with `webServer` to start dev server. Create `tests/integration/` directory
- **Cypress**: Install `cypress`. Create `cypress.config.ts`. Create `cypress/e2e/` directory
- Ask user: test against fake server (using `rest_api_faker`) or actual backend?

---

## Part 5: E2E Testing (Full-Stack)

This is a **project-level** E2E test suite that lives **outside** both `backend/` and `frontend/` folders. It tests the full stack (backend + frontend) together. It should use the same package manager as the frontend for consistency.

Ask the user:
1. **Framework**: Playwright (default), Cypress, or other?

### Structure

```
e2e/
├── tests/
│   └── example.spec.ts
├── package.json
├── tsconfig.json
├── playwright.config.ts     (if Playwright)
├── cypress.config.ts        (if Cypress)
└── docker-compose.e2e.yml   (optional: to spin up backend + DB for tests)
```

### Playwright (default)

```typescript
// e2e/playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: 'http://localhost:5173', // frontend URL
    trace: 'on-first-retry',
  },
  webServer: [
    {
      command: 'cd ../backend && npm start',
      port: 3000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'cd ../frontend && npm run dev',
      port: 5173,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
```

### Cypress

```typescript
// e2e/cypress.config.ts
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: 'tests/**/*.spec.ts',
    supportFile: false,
  },
});
```

Add scripts to `e2e/package.json`:
```json
{
  "scripts": {
    "test": "playwright test",
    "test:headed": "playwright test --headed",
    "test:ui": "playwright test --ui"
  }
}
```

---

## Project Root Files

Always generate these at the project root:

### README.md

Generate a `README.md` that describes:
- Project overview (ask user for a brief description)
- Tech stack summary (based on selections)
- Prerequisites (Node.js, .NET, Docker, etc.)
- Getting started instructions for each part
- How to run tests at each level
- How to run with fake backend (if applicable)
- CI/CD pipeline summary (if GitHub Actions selected)

### .gitignore

Generate a comprehensive `.gitignore` combining patterns for all selected technologies:

```gitignore
# Dependencies
node_modules/

# Build outputs
dist/
build/
.next/
out/
bin/
obj/

# Environment
.env
.env.local
.env*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test results
coverage/
test-results/
playwright-report/

# Docker
docker-compose.override.yml
```

### .editorconfig

```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.cs]
indent_size = 4

[*.{csproj,sln}]
indent_size = 2
```

---

## Step-by-Step Scaffolding Process

1. **Greet the user** and ask: "Which parts do you want in your new project?" Present the 5 top-level options
2. **For each selected part**, ask the detailed follow-up questions listed above
3. **Confirm the full plan** with the user before generating any files: show a summary table of all selections. Also create a roadmap/todo list of the steps to generate the project.
4. **Generate the project structure** — create all directories and files
5. **Generate file contents** — populate each file with working boilerplate code based on selections
6. **Provide next steps** — tell the user what commands to run to get started

### Summary Table Format

Before generating, show the user a summary like:

```
📋 Project Scaffolding Summary
──────────────────────────────────────────
Project Name: <name>

✅ GitHub Actions
   • PR Build → pre-release
   • Tag Build → stable release

✅ Dev Container
   • Unified (single container)

✅ Backend
   • Language: C#
   • Containerized: Yes
   • Database: PostgreSQL
   • Tests: Unit + Integration

✅ Frontend
   • Framework: React + Vite
   • Styling: Tailwind CSS
   • Dark theme: Yes
   • Multilingual: Yes (English, French)
   • PWA: No
   • Fake backend: Yes
   • Unit tests: Vitest
   • Integration tests: Playwright

✅ E2E Testing
   • Framework: Playwright
──────────────────────────────────────────
```

Ask: "Does this look correct? Should I proceed with generating the project?"

---

## Rules and Best Practices

- **Always ask before assuming.** Never pick a default without confirmation unless the user explicitly says "use defaults"
- **Use TypeScript** for all JavaScript/TypeScript code
- **Use the latest stable versions** of all packages and tools
- **Include proper `.gitignore`** entries for every technology in the stack
- **Include `package.json` scripts** for all common tasks (build, test, dev, lint)
- **Keep the folder structure clean**: backend, frontend, and e2e are top-level siblings
- **Environment variables** should use `.env` files with `.env.example` committed as a template
- **Docker Compose** should be used when multiple services need to run together
- **All test commands** should be runnable independently (unit, integration, e2e)
- **No project specific code** you don't need to write actual application logic, just the boilerplate and structure to get started immediately.
