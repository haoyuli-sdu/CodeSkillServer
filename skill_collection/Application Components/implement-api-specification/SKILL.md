---
name: "implement-api-specification"
description: "Implement changes in the codebase for a specific Service based on the generated API classes and models."
---

# Implement Component

Read `AGENTS.md` before coding.

## Inputs

- Name of the Service to be implemented
- The original API class that should be rewritten

## Workflow

1. Read the related generated API classes and models in `src/infrastructure/api/generated`.
2. Read the original API class.
3. Treat the generated models as the source of truth and design the replacement Service API around those models.
4. Create a Service class that will replace the existing API class.
5. Update the rest of the codebase to use the generated models directly whenever possible (UI, state, payloads, mocks), instead of adapting models back to legacy shapes.
6. Make any necessary changes to the codebase and the mock API so that it reflects the new structure in the generated API classes and models.
7. Run yarn build and all e2e tests to make sure everything works.

## Constraints

- Remove the old API class
- The Mock API MUST reflect the new API classes and models. Change the old endpoints to match the new specification.
- Generated models are the canonical contract. Prefer changing feature/page/component code to match generated model fields and enums.
- Avoid `toSomething`-style conversion functions and compatibility layers in Services unless absolutely necessary for incremental migration.
- If a conversion function is unavoidable, keep it minimal, document why it is needed, and plan to remove it once call sites are migrated to the generated model.
