---
name: "frontend-scaffold"
description: "Scaffold a new frontend feature with correct file structure, types, tests, and styles. Triggers on \"scaffold feature\", \"new feature\", \"scaffold component\", \"create feature\", \"set up feature\"."
---

# Frontend Scaffold — Feature-Level Structure

Read existing conventions first: `ls src/ && ls src/components/ 2>/dev/null`

## File Structures

### React SPA
```
src/features/[name]/
  components/Feature.tsx, Feature.module.css, Feature.test.tsx
  hooks/useFeatureData.ts
  types.ts
  api.ts
```

### Astro + Preact
```
src/
  pages/feature.astro
  islands/FeatureIsland.tsx, FeatureIsland.module.css
  components/FeatureStatic.astro
  stores/featureStore.ts  (if cross-island state)
```

### Next.js App Router
```
app/feature/
  page.tsx, loading.tsx, error.tsx
  _components/FeatureClient.tsx  ('use client')
```

**Always match existing structure.** Don't introduce `features/` if project uses flat `components/`.

## Per-File Requirements

- **Types**: Discriminated unions, explicit props, no `any`
- **Tests**: Testing Library by role/label, axe-core scan
- **Data**: Use project's existing library
- **Forms**: Label every input, `aria-invalid` on errors
- **State**: Classify (local/shared/server/URL), use project's library

### API File (TanStack Query)
```tsx
export const featureKeys = {
  all: ['features'] as const,
  list: (filters: F) => [...featureKeys.all, filters] as const,
  detail: (id: string) => [...featureKeys.all, id] as const,
}

export async function fetchFeatures(filters: F) {
  const res = await fetch(`/api/features?${new URLSearchParams(filters)}`)
  if (!res.ok) throw new Error(`${res.status}`)
  return z.array(FeatureSchema).parse(await res.json())
}
```

### Starter Test
```tsx
describe('Feature', () => {
  test('renders', () => {
    render(<Feature />)
    expect(screen.getByRole('heading', { name: /feature/i })).toBeInTheDocument()
  })
  test('accessible', async () => {
    const { container } = render(<Feature />)
    expect(await axe(container)).toHaveNoViolations()
  })
})
```

## Before Generating

Show file tree and confirm with user. Generate only after approval.

## Self-Check

- [ ] Matches project naming/structure conventions
- [ ] Loading, error, empty states
- [ ] Tests: render + interaction + a11y
- [ ] Accessible: semantic HTML, keyboard
- [ ] Route added if new page
