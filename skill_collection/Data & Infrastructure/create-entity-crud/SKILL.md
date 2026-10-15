---
name: "create-entity-crud"
description: "Scaffold a complete CRUD feature for a new entity. Use when: creating a new entity page, adding a new form, building a new registration page, scaffolding vehicles, drivers, routes, or any new entity following the multi-step form pattern."
---

# Create Entity CRUD

Scaffold a complete multi-step form feature for a new entity, following the established project patterns.

## When to Use
- User asks to create a new entity registration page (e.g., vehicles, drivers, routes)
- User wants to scaffold a CRUD create form for a new resource
- User references a backend DTO and wants a matching frontend

## Procedure

### 1. Gather Information
- **Entity name** (plural, English): e.g., `vehicles`, `drivers`
- **Backend DTO**: Read the DTO file to understand all fields, types, and validations
- **Endpoint**: Confirm the `POST` URL (usually `/{entities}`)
- **Step grouping**: Ask or infer logical grouping of fields into 2–4 steps

### 2. Create File Structure

Create all files under `src/app/<entity>/create/`:

```
src/app/<entity>/create/
├── page.tsx
├── components/
│   ├── <Entity>Form.tsx
│   ├── steps/
│   │   ├── Step1Name.tsx
│   │   ├── Step2Name.tsx
│   │   └── Step3Name.tsx
│   └── ui/                    ← Reuse from existing entity if possible
│       ├── Input.tsx
│       ├── Select.tsx
│       └── FileUpload.tsx
├── schemas/
│   └── <entity>.schema.ts
└── services/
    └── <entity>.service.ts
```

### 3. Build Schema (`schemas/<entity>.schema.ts`)

Reference: [Zod schema instructions](../../../.github/instructions/zod-schemas.instructions.md)

```typescript
import { z } from "zod";

const optionalString = z.string().optional().or(z.literal(""));

export const <entity>Schema = z.object({
  // Required fields with min(1) and Portuguese error messages
  // Optional fields with optionalString helper
  // Masked fields with .transform() + .pipe()
});

export type <Entity>FormData = z.infer<typeof <entity>Schema>;
```

### 4. Build Service (`services/<entity>.service.ts`)

Reference: [API service instructions](../../../.github/instructions/api-services.instructions.md)

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001";

export async function create<Entity>(data: <Entity>FormData) {
  const response = await fetch(`${API_URL}/<entities>`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json();
    throw error;
  }
  return response.json();
}
```

### 5. Build UI Components (`components/ui/`)

Check if `src/app/companies/create/components/ui/` already exists — **reuse** by copying or importing if similar. Only create new UI components if the entity needs something unique.

Existing components:
- `Input.tsx` — label, mask, error, register
- `Select.tsx` — label, options, error, register
- `FileUpload.tsx` — label, error, onChange, image preview

### 6. Build Step Components (`components/steps/`)

Each step:
- Receives `form: UseFormReturn<<Entity>FormData>` as prop
- Destructures `register`, `formState: { errors }`, and optionally `watch`, `setValue`
- Uses responsive grid: `grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3`
- Labels and placeholders in Portuguese (pt-BR)
- Mark required fields with `*` in the label

### 7. Build Form Container (`components/<Entity>Form.tsx`)

Follow the pattern in `src/app/companies/create/components/CompanyForm.tsx`:
- Define `STEPS` array with title and fields per step
- Define `STEP_FIELDS` record mapping step index to field arrays for validation
- `useForm` with `zodResolver`, `mode: "onTouched"`, all defaults set
- `handleNext()`: `form.trigger(STEP_FIELDS[currentStep])` before advancing
- `onSubmit()`: call service, toast success, handle 409 and other errors
- Visual stepper with numbered circles and step titles
- Navigation buttons: "Voltar", "Próximo", "Cadastrar <Entity>"

### 8. Build Page (`page.tsx`)

```typescript
import { Toaster } from "react-hot-toast";
import <Entity>Form from "./components/<Entity>Form";

export const metadata = { title: "Cadastro de <Entity>" };

export default function Create<Entity>Page() {
  return (
    <main className="min-h-screen bg-gray-50 px-4 py-10 sm:px-6 lg:px-8">
      <Toaster position="top-right" />
      <div className="mx-auto max-w-4xl">
        <h1 className="mb-2 text-center text-2xl font-bold text-gray-900 sm:text-3xl">
          Cadastro de <Entity>
        </h1>
        <p className="mb-8 text-center text-sm text-gray-500">
          Preencha os dados abaixo para cadastrar.
        </p>
        <<Entity>Form />
      </div>
    </main>
  );
}
```

### 9. Validate

Run `npm run build` to confirm no TypeScript or compilation errors.

### 10. Atualizar Chat SYSTEM_PROMPT (backend)

Adicione o novo módulo na constante `SYSTEM_PROMPT` em `gestao-de-frotas-back-end/src/chat/chat.service.ts`, na seção "Módulos disponíveis no sistema:", com o formato:
```
- **Nome do Módulo** (/rota) – Descrição breve da funcionalidade.
```
Isso garante que o assistente de chat conheça a nova funcionalidade e possa ajudar os usuários.

## Reference Implementation

See `src/app/companies/create/` for a complete working example of this pattern.
