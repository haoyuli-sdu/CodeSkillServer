---
name: "bolt-templates"
description: "Smart project template generator based on constitution. Creates folder structures, boilerplate files and configuration tailored to the tech stack (React + .NET, Vue + Python, Angular + Node, etc.). Triggers: 'generate template', 'project structure', 'scaffold project', 'boilerplate', 'create component template', 'create from constitution', '/bolt-templates'."
---

# Bolt Templates — Methodology

Methodology: follow `bolt-framework` skill (loaded automatically). Specialist for
intelligent project structures based on the constitution's tech stack.

## Template generation rules

### React + .NET Constitution → Templates

- `src/frontend/` (React + Vite + TypeScript)
  - `components/` (common, forms, layout)
  - `pages/` (route components)
  - `hooks/` (custom React hooks)
  - `services/` (API clients)
  - `types/` (TypeScript definitions)
  - `styles/` (CSS modules/Tailwind)
- `src/backend/` (.NET 8+ Minimal API)
  - `Controllers/` (API endpoints)
  - `Services/` (business logic)
  - `Models/` (data models)
  - `Data/` (Entity Framework)
  - `Extensions/` (service extensions)
- `tests/` (Jest + xUnit)
  - `unit/frontend/`
  - `unit/backend/`
  - `integration/`
  - `e2e/`
- `docs/` (API documentation)

### Vue + Python Constitution → Templates

- `src/web/` (Vue 3 + Pinia)
  - `components/` (base, forms, layout)
  - `views/` (page views)
  - `composables/` (Vue composition functions)
  - `services/` (HTTP clients)
  - `types/` (TypeScript definitions)
- `src/api/` (FastAPI + SQLAlchemy)
  - `routers/` (API routes)
  - `services/` (business logic)
  - `models/` (SQLAlchemy models)
  - `schemas/` (Pydantic schemas)
  - `database/` (DB configuration)
- `tests/` (Vitest + pytest)
  - `unit/web/`
  - `unit/api/`
  - `integration/`

### Angular + Node.js Constitution → Templates

- `src/app/` (Angular + TypeScript)
- `src/server/` (Express + TypeScript)
- `tests/` (Jasmine + Jest)

## Commands to execute

### Generate from constitution

```bash
# Generate complete project structure
./.boltf/scripts/bash/generate-project-structure.sh --from-constitution

# Generate specific component type
./.boltf/scripts/bash/create-component.sh --type react-page --name UserProfile
./.boltf/scripts/bash/create-component.sh --type api-controller --name UserController
./.boltf/scripts/bash/create-component.sh --type vue-component --name DataTable
```

### Template validation

```bash
# Validate generated structure against constitution
./.boltf/scripts/bash/validate-template.sh --constitution .boltf/.boltf/memory/constitution.md
```

## Auto-generation logic

When user requests:

1. **Read constitution** to determine tech stack.
2. **Select appropriate template** based on stack.
3. **Generate folder structure** with proper naming.
4. **Create base files** with boilerplate code.
5. **Setup package.json / project files** with dependencies.
6. **Generate configuration** files (tsconfig, vite.config, etc.).

## Template files to create

### Frontend (React)

- `package.json` with proper scripts and dependencies.
- `tsconfig.json` with strict TypeScript config.
- `vite.config.ts` with development server setup.
- `index.html` with proper meta tags.
- `src/main.tsx` with React 18 setup.
- `src/App.tsx` with router setup.
- Component templates with TypeScript + CSS modules.

### Backend (.NET)

- `.csproj` file with package references.
- `Program.cs` with Minimal API setup.
- `appsettings.json` with configuration.
- Controller templates with proper attributes.
- Service templates with dependency injection.
- Model templates with proper validation.

### Testing

- `jest.config.js` for frontend testing.
- Test templates for components and services.
- Integration test setup with test database.

## Smart defaults

Based on constitution constraints:

- **Security**: add authentication templates if mentioned.
- **Database**: generate Entity Framework models if SQL specified.
- **Styling**: add Tailwind CSS if mentioned in constitution.
- **State management**: add Redux/Pinia if complex app.
- **API documentation**: generate OpenAPI specs automatically.

## Example usage

```markdown
User: "Generate project structure for e-commerce app"
Constitution: React + .NET + PostgreSQL

Generated:
├── src/
│   ├── frontend/ (React + TypeScript + Tailwind)
│   │   ├── components/
│   │   │   ├── product/
│   │   │   ├── cart/
│   │   │   └── user/
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── ProductListPage.tsx
│   │   │   └── CheckoutPage.tsx
│   │   └── services/
│   │       ├── productApi.ts
│   │       └── authApi.ts
│   └── backend/ (.NET + Entity Framework + PostgreSQL)
│       ├── Controllers/
│       │   ├── ProductsController.cs
│       │   └── OrdersController.cs
│       ├── Models/
│       │   ├── Product.cs
│       │   └── Order.cs
│       └── Data/
│           └── EcommerceContext.cs
└── tests/
    ├── unit/frontend/
    ├── unit/backend/
    └── integration/
```

Always ensure generated templates follow constitution standards and include proper
error handling, validation, and security practices.

## Related agents (next steps)

- → `bolt-implement`: generate complete project structure based on constitution and
  selected template.
- → `bolt-deps`: install all required dependencies for the generated template.
