---
name: "syncfusion-react-ui-builder"
description: "Generates production-ready webpages powered by Syncfusion React Components. Orchestrates Orchestrates a structured workflow that handles design thinking, component picking, code generation, and validation with built-in WCAG 2.1 AA accessibility and responsive design. Use when the user asks to create web components, build UI pages, design interfaces, or generate frontend code for React applications."
---

# Syncfusion React UI Builder

## Overview

The **Syncfusion React UI Builder** skill is a frontend-only React component generator that orchestrates an AI agent through 8 stages to generate production-ready UI components powered by Syncfusion.

## What This Skill Does

**✅ Generates:**
- React functional components (`.tsx`/`.jsx`) with hooks
- CSS stylesheets (CSS Modules, Tailwind classes, inline styles)
- TypeScript interfaces for properties, state, and event handlers
- Syncfusion component integration with correct imports and properties
- Client-side form validation logic
- WCAG 2.1 AA accessibility markup (ARIA attributes, semantic HTML)
- Responsive CSS with mobile-first breakpoints
- Component index exports and barrel files

**❌ Does NOT Generate:**
- Backend code (API routes, server handlers, middleware)
- Database schemas or ORM models
- Authentication/authorization logic
- Server-side validation
- Routing configuration
- Environment secrets or infrastructure config

## When to Use

### ✅ USE this Skill for:

- **Full UI builds** with 3+ Syncfusion components
- **Design system decisions** required (CSS framework, colors, spacing, typography)
- **Complete pages or dashboards** from scratch
- **WCAG 2.1 AA validation** for complex layouts
- **Multi-stage workflows** requiring design → code → validate
- **Team collaboration** on larger component projects
- Examples:
  - Building a complete React admin dashboard
  - Designing a multi-form wizard interface
  - Creating a full data management portal with multiple sections
  - Implementing a complex dashboard with multiple views and charts

### ❌ DO NOT USE this Skill for:

- ✋ Configuring a single component (use component skill directly)
- ✋ Quick implementation questions (use component skill directly)
- ✋ Component tutorials or how-tos (use component skill directly)
- ✋ Troubleshooting component issues (use component skill + diagnostic protocol)
- ✋ Backend/API code (out of scope)
- ✋ Non-Syncfusion React questions (use general React help)

## Quick Start

### Prerequisites

1. **Active React project** (React 18+, Next.js 13+, Vite, or CRA)
2. **Node.js 18+** and npm/yarn/pnpm installed
4. **Syncfusion components library** (auto-installed if missing):
   ```bash
   npx skills add syncfusion/react-ui-components-skills -y
   ```

### Basic Usage

**Example 1: Generate a Login Form**

```
User: "Create a login form with email, password, and remember me checkbox"

Skill executes:
  → Stage 1: Identifies login form component type
  → Stage 2: Detects project structure (React, TypeScript, etc.)
  → Stage 3-4: AI creates optimal component-mapping.json → maps to Syncfusion components
  → Stage 5: Generates LoginForm.tsx with validation
  → Stage 6: Installs dependencies
  → Stage 7: Validates WCAG 2.1 AA compliance
  → Stage 8: Inserts code into project

Output:
  ✓ components/LoginForm/LoginForm.tsx
  ✓ components/LoginForm/LoginForm.module.css
  ✓ components/LoginForm/index.ts
```

**Example 2: Generate a Dashboard**

```
User: "Build a dashboard with customer overview, recent orders table, and sales chart"

Output:
  ✓ components/Dashboard/Dashboard.tsx (main layout)
  ✓ components/CustomerOverview/CustomerOverview.tsx
  ✓ components/RecentOrders/RecentOrders.tsx (with Syncfusion DataGrid)
  ✓ components/SalesChart/SalesChart.tsx (with Syncfusion ChartComponent)
  ✓ Mock data included (useState with sample data)
  ✓ Responsive design (mobile-first, grid layout)
  ✓ Dark mode support with design tokens
  ✓ Full accessibility compliance (WCAG 2.1 AA)
```

## How It Works: 8-Stage AI Orchestration (Stateless)

The skill orchestrates **8 stages of pure AI reasoning** with **two user decision points**.

**Key Architecture:**
- **Stateless design**: Conversation history maintains state
- **Pure AI reasoning**: Each stage reads guidance docs, analyzes context, makes decisions
- **1 user decision gates**: Stage 4 (theme confirmation)
- **7 fully automated stages**: 1, 2, 3, 5, 6, 7, and final code insertion
- **Dedicated theming stage**: Stage 4 locks design system before code generation

```
User Request
    ↓
[Stage 1: Intent Analysis] 
  AI reads query → identifies component type & features
    ↓
[Stage 2: Project Detection]
  AI scans project → detect framework, language, CSS strategy, preferences
    ↓
[Stage 3: Layout Analysis & Component Mapping] 
  AI analyzes requirements → creates optimal component-mapping.json
  AI maps to specific Syncfusion components (3+ components)
    ↓
[Stage 4: Theming & Design System] ⭐ USER DECISION #1
  AI locks CSS framework → Syncfusion theme mapping
  AI selects color system (OKLCH, brand colors)
  AI confirms spacing/typography scale (4pt grid, 1.25 ratio)
  Design system decisions locked before code generation
  User confirms theming decision
    ↓
[Stage 5: Code Generation]
  AI generates .tsx, .css, TypeScript interfaces
  Uses theming decisions from Stage 4
  For complex UIs (4+ sections or 3+ component types), components MUST be split into modular subcomponents.
  With accessibility + responsive design built-in
    ↓
[Stage 6: Dependencies]
  AI detects required packages (Syncfusion + CSS framework)
  Presents npm install command or runs it
  Proceed to next stage
    ↓
[Stage 7: Validation] 
  AI validates WCAG 2.1 AA + security + performance + theming
  Binary result: PASS ✓ or FAIL ✗
    ↓
[Stage 8: Code Insertion]
  AI inserts files into project
  Updates imports, verifies build
    ↓
✓ Complete
```

**Stage Descriptions:**

- **Stage 1 (Intent Analysis)**: Parse user query, identify component type and features. Read: `references/stage-1-intent-analysis.md`
- **Stage 2 (Project Detection)**: Auto-detect framework, language, CSS strategy, component directory. Read: `references/stage-2-project-detection.md`
- **Stage 3 (Layout Analysis & Component Mapping)**: AI analyzes requirements, creates optimal component-mapping.json, maps to Syncfusion components. Read: `references/stage-3-layout-analysis.md`
- **Stage 4 (Theming & Design System)**: Lock CSS framework, Syncfusion theme, color system (OKLCH), spacing (4pt), typography (1.25 ratio). Read: `references/stage-4-theming-and-design-system.md`
- **Stage 5 (Code Generation)**: Generate React with design tokens from Stage 4 applied + accessibility + responsive design. Read: `references/stage-5-code-generation.md`
- **Stage 6 (Dependencies)**: Detect packages (Syncfusion + CSS framework), resolve conflicts, prepare install command. Read: `references/stage-6-dependencies.md`
- **Stage 7 (Validation)**: Validate WCAG 2.1 AA, security, performance, theming integration. Binary pass/fail. Read: `references/stage-7-validation.md` + `assets/validation-rules.md`
- **Stage 8 (Code Insertion)**: AI inserts files, updates imports, verifies build succeeds.

**User Interaction Summary:**

| Stage | Interaction |
|-------|-------------|
| 1 | None (AI analyzes) |
| 2 | None (AI analyzes) |
| 3 | None (AI analyzes) |
| 4 | Confirm theming decisions (CSS framework, colors, spacing, typography) |
| 5 | None (AI generates) |
| 6 | None (AI executes) |
| 7 | None (AI analyzes) |
| 8 | None (AI executes) |

**Total user decision gates: 1** (Stage 4: theming decision). Rest fully automated with AI reasoning + guidance docs.

## Agent Instructions

### When User Requests UI Component Generation

1. **Validate scope**: Confirm request is for frontend components (not backend/API)
2. **Load guidance**: Read `stage-1-intent-analysis.md` to understand Stage 1
3. **Execute 8-stage flow**: Follow the orchestration flow shown above
4. **Progressive disclosure**: Load stage guides on-demand; load support references only when needed
5. **Maintain conversation history**: Each stage reads previous decisions from conversation context (stateless)

### Stage Execution & Reference Loading

**Stage 1: Intent Analysis**
- Read: `references/stage-1-intent-analysis.md`
- Task: Parse user query, identify component type, resolve ambiguities
- Output: Component type + modifiers + target directory

**Stage 2: Project Detection**
- Read: `references/stage-2-project-detection.md`
- Task: Auto-detect React framework, language, CSS strategy, formatting rules
- Output: Project configuration

**Stage 3: Layout Analysis & Component Mapping**
- Read: `references/stage-3-layout-analysis.md`
- Task: Analyze user requirements → create optimal component-mapping.json → map to Syncfusion components (3+ minimum)
- Output: component-mapping.json + Component mapping

**Stage 4: Theming & Design System** ⭐ USER DECISION #1
- Read: `references/stage-4-theming-and-design-system.md`
- Task: Lock CSS framework, Syncfusion theme, color system (OKLCH), spacing (4pt grid), typography (1.25 ratio), responsive breakpoints
- Output: Design system decisions + User confirmation

**Stage 5: Code Generation**
- Read: `references/stage-5-code-generation.md`
- Task: Generate React .tsx, CSS, TypeScript interfaces using theming from Stage 4
- Ensure: WCAG 2.1 AA accessibility, responsive design, token architecture applied
- Output: Generated files ready for review

**Stage 6: Dependencies**
- Read: `references/stage-6-dependencies.md`
- Task: Detect required packages (Syncfusion + CSS framework), resolve version conflicts
- Output: Output installation command only; do not assume auto-install unless explicitly requested

**Stage 7: Validation**
- Read: `references/stage-7-validation.md` + `assets/validation-rules.md` + `references/web-standards.md`
- Task: Validate against WCAG 2.1 AA, security, performance, theming integration standards
- Auto-apply fixes where possible
- Output: Binary result (PASS ✓ or FAIL ✗)

**Stage 8: Code Insertion**
- Task: Insert generated files into project, update imports, verify build
- Output: Success report with file paths

### Boundary Rules (CRITICAL)

**AI agents executing this skill MUST:**

1. **Frontend only**: Never generate backend code (API routes, database schemas, middleware)
2. **Mock data only**: Use `useState` with hardcoded samples; no `fetch()` to real APIs
3. **No secrets**: Exception: `.env.local` for `SYNCFUSION_LICENSE_KEY` when user provides
4. **React components only**: Generate `.tsx`/`.jsx` files in component directories
5. **Redirect backend requests**: *"This skill generates frontend UI only. Backend integration is your app's responsibility. Ready to generate the frontend?"*
6. **Prioritize skill**: Always prioritize Syncfusion component skill files as source of truth when available; do not rely on memory.

### Error Handling

If any stage fails:

1. **Retry once** with same approach
2. **If retry fails**, attempt workaround or skip to next stage
3. **Notify user** with error message from stage output
4. **Offer recovery**: *"Would you like to go back to Stage 3 and choose a different layout?"*

If stage failure impacts correctness, halt and request user direction instead of proceeding with uncertain output

### Resource Loading Strategy (Progressive Disclosure)

**Load SKILL.md first** (you're reading it now) ~400 lines

**Load stage guides on-demand** (each <200 lines):
- `stage-1-intent-analysis.md` → During Stage 1
- `stage-2-project-detection.md` → During Stage 2
- `stage-3-layout-analysis.md` → During Stage 3
- etc.

**Load support references only when needed**:
- `web-standards.md` → When validating in Stage 5
- `assets/validation-rules.md` → When validating in Stage 5

**Result**: Initial load ~400 lines (SKILL.md only). Full spec available on-demand, never exceeding Agent Skills context limits.

## Configuration & User Customization

### Auto-Detected Settings

During **Stage 2 (Project Detection)**, AI automatically detects:

- **Framework**: React, Next.js (App Router / Pages Router), Vite, Create React App
- **Language**: TypeScript (if `tsconfig.json` exists) or JavaScript
- **Styling**: CSS Modules, Tailwind CSS, CSS-in-JS, or inline styles
- **Formatting**: Prettier/ESLint rules (indentation, quotes, semicolons)
- **Component Directory**: `src/components/`, `app/components/`, or similar

### User Override Options

In **Stage 2**, user can override any detected setting:

```
Detected Settings:
  Framework: Next.js 14 (App Router)
  Language: TypeScript
  CSS: CSS Modules
  Component Directory: app/components/

[Confirm] [Override Each] [Cancel]
```

### Syncfusion License Configuration

The skill handles license key setup:

1. **Check** for existing `SYNCFUSION_LICENSE_KEY` in `.env.local`
2. **If missing**, prompt user: *"Get a free Community License at https://www.syncfusion.com/account/manage-trials"*
3. **If provided**, write to `.env.local` + inject `registerLicense()` in app entry
4. **If skipped**, proceed but warn that watermark will appear in preview

---

## Code Generation Standards

All generated code includes:

### Accessibility (WCAG 2.1 AA)
- ✅ Semantic HTML5 (`<form>`, `<label>`, `<input>`, `<button>`)
- ✅ ARIA labels and descriptions
- ✅ Keyboard navigation (tab order, focus management)
- ✅ Color contrast ≥ 4.5:1
- ✅ Focus indicators on interactive elements

### Responsive Design
- ✅ Mobile-first CSS (320px base, then scale up)
- ✅ Flexbox/Grid layouts (no fixed widths)
- ✅ Media queries at 768px, 1024px+ breakpoints
- ✅ Touch-friendly buttons (44x44px minimum)

### Security
- ✅ Input validation and sanitization
- ✅ No `dangerouslySetInnerHTML` without sanitization
- ✅ No hardcoded secrets
- ✅ No XSS vulnerabilities

### Performance
- ✅ React.memo for stable components
- ✅ useCallback for event handlers
- ✅ Lazy loading for large components
- ✅ Optimized re-renders

### TypeScript & Types
- ✅ Full type coverage (no `any` types)
- ✅ Props interfaces with JSDoc
- ✅ Event handler signatures
- ✅ State type annotations

## Supported Use Cases

- **Login form**: TextBox (email), TextBox (password), CheckBox (remember), Button (submit)
- **Data table**: DataGrid with sorting, filtering, pagination, row selection
- **Dashboard**: Multiple components orchestrated (header, sidebar, main content, footer)
- **Registration wizard**: Multi-step form with progress indicator and validation

## Troubleshooting

**Common Issues:**

| Issue | Solution |
|-------|----------|
| "Project type not detected" | Ensure `package.json` exists with React dependency |
| "Syncfusion license banner appears" | Add license key via Stage 2 prompt |
| "Build fails after insertion" | Use Syncfusion component skills to resolve failures |
| "Component not rendering" | Verify import paths and ensure parent component imports correctly |

## Additional Resources

### Quick Reference by Use Case

| Need | Reference File |
|------|-----------------|
| Understanding workflow | This SKILL.md file |
| How Stage X works | `references/stage-X-*.md` |
| Validation rules | `assets/validation-rules.md` |
| Accessibility/security | `references/web-standards.md` |

## Support

For issues or questions:
1. Check Syncfusion component skills for common problems
2. Verify your project meets prerequisites (React 18+, Node.js 18+)
3. Ensure Syncfusion license is valid and registered
4. Review generated code compliance report for warnings

---
