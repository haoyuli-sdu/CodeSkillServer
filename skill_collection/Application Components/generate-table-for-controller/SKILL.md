---
name: "generate-table-for-controller"
description: "Generate a single table/list component from parsed controller metadata. Renders a sortable, filterable, paginated data table for the list/index endpoint. Use ONLY when generating a table view. Do NOT generate forms, pages, or API clients."
---

# Generate Table for Controller

Generate one table component for a controller's list/index action.

## Frontend Stack

- **React 19** + **TypeScript** functional components
- CSS classes (not CSS modules, not Tailwind, not styled-components)
- No external UI libraries — pure HTML + CSS
- **sonner** for toast notifications

## Input

You receive parsed controller metadata (from `parse-csharp-controller`):
- The controller's route prefix, resource name
- The list action (`[HttpGet]` returning a collection)
- The detail action (`[HttpGet("{id}")]`) — for row click navigation
- The update action — for "Edit" row button
- The delete action — for "Delete" row button
- The response DTO with all properties
- Enums referenced by the DTO

## What to generate

### 1. Component structure

**Location:** `Frontend/src/components/{ResourceName}Table.tsx`

```typescript
import React, { useState } from 'react';
import type { ResponseType } from '../types/{resourceName}.types';

interface {ResourceName}TableProps {
  data: ResponseType[];
  loading: boolean;
  onRefresh: () => void;
  onEdit: (item: ResponseType) => void;
  onDelete: (id: number) => void;
  onView: (item: ResponseType) => void;
}

export const {ResourceName}Table: React.FC<{ResourceName}TableProps> = ({
  data,
  loading,
  onRefresh,
  onEdit,
  onDelete,
  onView,
}) => {
  // Component implementation
};
```

### 2. Table implementation

Follow the pattern from `LogTable.tsx`:

```tsx
// Loading state
if (loading) {
  return <div className="loading-state">Loading {resourceName}s...</div>;
}

// Empty state
if (data.length === 0) {
  return (
    <div className="empty-state">
      <p>No {resourceName}s found</p>
      <button onClick={onRefresh} className="btn btn-primary">Refresh</button>
    </div>
  );
}

// Table with data
return (
  <div className="table-container">
    <table className="{resourceName}-table">
      <thead>
        <tr>
          {/* Column headers from DTO properties */}
          <th>ID</th>
          <th>Name</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {data.map((item) => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td>{item.name}</td>
            <td>
              <button className="btn btn-detail" onClick={() => onView(item)}>
                View
              </button>
              <button className="btn btn-secondary" onClick={() => onEdit(item)}>
                Edit
              </button>
              <button className="btn btn-danger" onClick={() => onDelete(item.id)}>
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
```

### 3. Column display rules

| C# type | Column display |
|---|---|
| `string` | Text, sortable, searchable |
| `int`, `long`, `decimal`, `double` | Right-aligned, sortable |
| `bool` | Checkmark/badge |
| `DateTime`, `DateTimeOffset`, `DateOnly` | Formatted date, sortable |
| `Guid` | Truncated with copy tooltip |
| `Enum` | Colored badge (map enum names to display) |
| Nullable `T?` | Show "—" for null |
| `List<T>`, `IEnumerable<T>` | First-N with "+N more" badge |
| `decimal` (currency) | Formatted currency |

### 4. Sorting and filtering

- Sortable columns: clicking header toggles asc/desc/none
- Filter controls per property type:
  - `string` → text input
  - `Enum` → multi-select dropdown
  - `bool` → yes/no/any tri-state
  - `DateTime` → date range picker
  - `decimal` → min/max range inputs
- Show active filter chips with remove buttons

### 5. Selection (optional)

If the controller supports bulk operations, add checkbox selection:
```tsx
// Add to props
selectedItems: number[];
onSelectItem: (id: number) => void;
onSelectAll: () => void;
onDeleteSelected: () => void;

// Toolbar with bulk actions
{selectedItems.length > 0 && (
  <div className="table-toolbar">
    <button onClick={onDeleteSelected} className="btn btn-danger">
      Delete Selected ({selectedItems.length})
    </button>
  </div>
)}

// Checkbox column
<td>
  <input
    type="checkbox"
    checked={selectedItems.includes(item.id)}
    onChange={() => onSelectItem(item.id)}
  />
</td>
```

### 6. CSS classes to use

Use these CSS classes (already defined in the design system):
- `.table-container` — white card with shadow
- `.{resourceName}-table` — full-width table
- `.loading-state` — centered loading text
- `.empty-state` — centered empty message with CTA
- `.btn` — base button style
- `.btn-primary` — blue action button
- `.btn-secondary` — gray button
- `.btn-danger` — red delete button
- `.btn-detail` — small blue button
- `.badge` — colored badge
- `.badge-error`, `.badge-warning`, `.badge-info` — level-specific badges

### 7. Detail modal (optional)

If the controller has a detail view, include a modal:
```tsx
const [viewingItem, setViewingItem] = useState<ResponseType | null>(null);

{viewingItem && (
  <div className="modal-overlay" onClick={() => setViewingItem(null)}>
    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
      <div className="modal-header">
        <h2>{ResourceName} Details</h2>
        <button className="modal-close" onClick={() => setViewingItem(null)}>✕</button>
      </div>
      <div className="modal-body">
        {/* Display all properties */}
      </div>
    </div>
  </div>
)}
```

## Location

Save to: `Frontend/src/components/{ResourceName}Table.tsx`

## Do NOT

- Generate form components (that's `generate-form-for-controller`)
- Generate API client services (that's `generate-api-client-for-controller`)
- Generate page-level layout or routing
- Parse the controller file (use parsed metadata already provided)
- Use CSS modules, Tailwind, or styled-components — use plain CSS classes
