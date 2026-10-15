---
name: "project-scaffold"
description: "Scaffold a new full-stack project with React+Vite frontend and Node.js backend. Use this when starting a brand new project or adding a new service. Sets up folder structure, TypeScript, ESLint, Prettier, and base configs."
---

# Project Scaffold

Bootstrap a production-ready full-stack project. Always run after `spec-writer`. Never scaffold without an approved spec.

## Trigger Conditions
- User says "create new project", "scaffold app", "init project"
- No `package.json` exists in the target directory

## Prerequisites
- `specs/<feature-slug>.spec.md` exists and is approved

## Steps

### 1. Confirm Spec Exists
```bash
ls specs/*.spec.md || echo "ERROR: No spec found. Run spec-writer first."
```
**Gate:** Stop if no spec exists.

### 2. Scaffold Frontend (React + Vite + TypeScript)
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D \
  eslint @eslint/js eslint-plugin-react eslint-plugin-react-hooks \
  eslint-plugin-jsx-a11y \
  @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  prettier eslint-config-prettier \
  vitest @vitest/ui @vitest/coverage-v8 \
  @testing-library/react @testing-library/user-event @testing-library/jest-dom \
  axe-core @axe-core/react \
  playwright @playwright/test
npm install \
  react-router-dom \
  @tanstack/react-query \
  axios
```

### 3. Frontend Config Files

**`frontend/vite.config.ts`**
```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: { lines: 80, functions: 80, branches: 80, statements: 80 }
    }
  }
})
```

**`frontend/.eslintrc.cjs`**
```js
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/strict',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/strict',
    'prettier'
  ],
  plugins: ['react-refresh', 'jsx-a11y'],
  rules: {
    'react/react-in-jsx-scope': 'off',
    'react-refresh/only-export-components': 'warn'
  }
}
```

**`frontend/src/test/setup.ts`**
```ts
import '@testing-library/jest-dom'
```

### 4. Scaffold Backend (Node.js + TypeScript)
```bash
mkdir backend && cd backend
npm init -y
npm install express cors helmet dotenv pg
npm install -D \
  typescript ts-node nodemon \
  @types/express @types/cors @types/node @types/pg \
  eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  prettier \
  vitest
npx tsc --init --strict --target ES2022 --module commonjs --outDir dist --rootDir src
```

**`backend/src/index.ts`**
```ts
import express from 'express'
import cors from 'cors'
import helmet from 'helmet'

const app = express()
const PORT = process.env.PORT || 3001

app.use(helmet())
app.use(cors())
app.use(express.json())

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

app.listen(PORT, () => console.log(`Server running on port ${PORT}`))

export default app
```

### 5. Root Docker Compose (Development)
**`docker-compose.yml`**
```yaml
version: '3.9'
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppassword
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      DATABASE_URL: postgres://appuser:apppassword@db:5432/appdb
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  pgdata:
```

### 6. Root `.env.example`
```
DATABASE_URL=postgres://appuser:apppassword@localhost:5432/appdb
PORT=3001
NODE_ENV=development
RAILWAY_TOKEN=
```

### 7. Git Init and Initial Commit
```bash
git init
echo "node_modules/\ndist/\n.env\ncoverage/\nplaywright-report/" > .gitignore
git add .
git commit -m "chore: initial project scaffold"
```

### 8. Verification Gate
```bash
# Frontend compiles
cd frontend && npm run build && echo "FRONTEND BUILD: OK"

# Backend compiles
cd ../backend && npx tsc --noEmit && echo "BACKEND TS: OK"

# Lint passes
cd ../frontend && npm run lint && echo "FRONTEND LINT: OK"
cd ../backend && npm run lint && echo "BACKEND LINT: OK"
```

**Gate:** All 4 checks must pass before moving to next skill.

## Artifacts Produced
- `frontend/` — Vite + React + TS project
- `backend/` — Node.js + Express + TS project
- `docker-compose.yml` — local dev environment
- `.gitignore`, `.env.example`
