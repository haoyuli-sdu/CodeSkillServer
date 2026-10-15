---
name: "syncfusion-aspnetcore-ui-builder"
description: "Generates production-ready enterprise webpages powered by Syncfusion ASP.NET Core Components. Orchestrates a structured workflow that handles design thinking, component picking, code generation, and validation with built-in WCAG 2.1 AA accessibility and responsive design. Use when the user asks to create web components, build UI pages, design interfaces, or generate frontend code for ASP.NET Core Razor Pages applications."
---

# Syncfusion ASP.NET Core UI Builder

## Overview

The **Syncfusion ASP.NET Core UI Builder** skill is a frontend UI generator that orchestrates an AI agent through 7 stages to generate production-ready Razor Pages powered by Syncfusion.

## What This Skill Does

**✅ Generates:**
- Razor Pages (`.cshtml`) with Syncfusion tag helpers
- PageModel classes (`.cs`) with `[BindProperty]` and form handling
- CSS stylesheets (Tailwind classes, Bootstrap, Material Design, or custom CSS)
- C# interfaces for models and ViewModel classes
- Syncfusion component integration with correct tag helper syntax
- Server-side form validation logic
- WCAG 2.1 AA accessibility markup (ARIA attributes, semantic HTML)
- Responsive CSS with mobile-first breakpoints
- Antiforgery token support

**❌ Does NOT Generate:**
- Backend code (API routes, controllers, middleware)
- Database schemas or Entity Framework models
- Authentication/authorization logic
- Server-side validation (beyond basic model binding)
- Routing configuration
- Environment secrets or infrastructure config
- **Default HTML controls** (without explicit user confirmation) — All controls MUST be Syncfusion ASP.NET Core components

---

## ⭐ CRITICAL RULES (Mandatory - Do Not Skip)

### Rule 1: Syncfusion Controls ONLY
**ALL generated controls must be Syncfusion ASP.NET Core components from `components.csv`.**
- ❌ NO default HTML controls (`<input>`, `<button>`, `<select>`, `<textarea>`, `<table>`, etc.) without explicit user confirmation
- ✅ Always verify component exists in `.apm/skills/syncfusion-aspnetcore-ui-builder/scripts/components.csv` first
- ✅ If HTML control seems necessary, **ASK user for confirmation** before generating
- ✅ Document user's choice if they explicitly approve HTML control usage

**Why:** Syncfusion components provide:
- Professional UI consistency
- WCAG 2.1 AA accessibility built-in
- Theme integration
- Enterprise-grade reliability
- Mobile-responsive design

### Rule 2: Skill File Reference is MANDATORY
**During component selection, code generation, AND build failure diagnostics — ALWAYS consult the relevant component skill files.**
- ✅ Read component skill file BEFORE generating any code using that component
- ✅ Use skill file examples as the source of truth for tag names, attributes, namespaces
- ✅ Compare generated code against skill file examples to verify correctness
- ✅ **Build Failure Protocol:** Error occurs → Find component in `components.csv` → Read skill file → Fix syntax

**Why:** Skill files are the authoritative reference for:
- Exact tag helper syntax (`<ejs-*>` format)
- Correct attribute names (camelCase vs other formats)
- Supported nested elements and templates
- Data binding patterns and requirements
- Required `@using` statements and namespaces
- Correct enum values with proper namespace prefixes

### Rule 3: Build Failure Troubleshooting Protocol (Non-Negotiable)
**When `dotnet build` fails:**

1. **Identify error** (RZ2010, CS0117, CS1061, etc.)
2. **Extract component name** from error message
3. **Find component in `components.csv`** → Get skill file path
4. **Read that component's SKILL.md file** carefully
5. **Compare generated code** against skill examples
6. **Fix syntax based on skill file** (NEVER guess)
7. **Rebuild** and verify
8. **Repeat if needed**

❌ **NEVER:**
- Guess or invent tag/attribute names
- Skip reading skill files
- Assume a component doesn't support something without checking skill file
- Continue without fixing the error
- Use default HTML as a workaround without user confirmation

✅ **ALWAYS:**
- Read the error message carefully
- Consult the relevant skill file
- Use skill file examples as evidence
- Test rebuild after each fix
- Ask user for confirmation before using non-Syncfusion controls

**Reference:** See `pre-generation-checklist.md` Section 1.5 and `stage-8-validation.md` "Build Failure Diagnostics" for detailed protocols.

---

## When to Use

### ✅ USE this Skill for:

- **Full UI builds** with 3+ Syncfusion components
- **Design system decisions** required (CSS framework, colors, spacing, typography)
- **Complete pages or dashboards** from scratch
- **WCAG 2.1 AA validation** for complex layouts
- **Multi-stage workflows** requiring design → code → validate
- **Team collaboration** on larger page projects
- Examples:
  - Building a complete Razor Pages admin dashboard
  - Designing a multi-form data entry interface
  - Creating a full data management portal with grids and forms
  - Implementing a complex dashboard with charts and data visualization

### ❌ DO NOT USE this Skill for:

- ✋ Configuring a single component (use component skill directly)
- ✋ Quick implementation questions (use component skill directly)
- ✋ Component tutorials or how-tos (use component skill directly)
- ✋ Troubleshooting component issues (use component skill + diagnostic protocol)
- ✋ Backend/API code (out of scope)
- ✋ Non-Syncfusion ASP.NET Core questions (use general ASP.NET Core help)

## Quick Start

### Prerequisites

1. **Active ASP.NET Core project** (Razor Pages, .NET 8 or Above, **Syncfusion.EJ2.AspNet.Core** NuGet package)
2. **.NET SDK 8.0+** installed
3. **Syncfusion ASP.NET Core components library** (auto-installed if missing): Run this command in CLI
   ```cli 
   dotnet add package Syncfusion.EJ2.AspNet.Core --source https://api.nuget.org/v3/index.json
   ```

### Basic Usage

**Example 1: Generate a Login Form**

```
User: "Create a login form with email, password, and remember me checkbox"

Skill executes:
  → Stage 1: Identifies login form page type
  → Stage 2: Detects project structure (Razor Pages, .NET version, etc.)
  → Stage 3-4: AI creates optimal component-mapping → maps to Syncfusion tag helpers
  → Stage 5: Generates Login.cshtml + Login.cshtml.cs with validation
  → Stage 6: Installs NuGet packages
  → Stage 7: Validates WCAG 2.1 AA compliance

Output:
  ✓ Pages/Account/Login.cshtml
  ✓ Pages/Account/Login.cshtml.cs
```

**Example 2: Generate a Dashboard**

```
User: "Build a dashboard with customer overview, recent orders grid, and sales chart"

Output:
  ✓ Pages/Dashboard/Dashboard.cshtml (main layout)
  ✓ Pages/Dashboard/Dashboard.cshtml.cs (PageModel)
  ✓ Components/CustomerOverview.cshtml
  ✓ Components/RecentOrdersGrid.cshtml (with Syncfusion DataGrid)
  ✓ Components/SalesChart.cshtml (with Syncfusion ChartComponent)
  ✓ Mock data included (ViewData or inline in PageModel)
  ✓ Responsive design (mobile-first, grid layout)
  ✓ Full accessibility compliance (WCAG 2.1 AA)
```

## How It Works: 7-Stage AI Orchestration (Simplified)

The skill orchestrates **7 simple stages** with **minimal user decisions**.

**Key Architecture:**
- **Clean and simple**: Generate neat UIs without complex design system
- **Syncfusion themes only**: Bootstrap5, Tailwind3, or Material3
- **1 user decision gate**: Stage 4 (theme selection)
- **Rest automated**: Stages 1-3, 5-7 are fully automated
- **No custom design system**: Use Syncfusion themes as-is

```
User Request
    ↓
[Stage 1: Intent Analysis] 
  AI identifies page type & features
    ↓
[Stage 2: Project Detection]
  AI detects .NET version and Razor Pages structure
    ↓
[Stage 3: Component Mapping] 
  AI selects appropriate Syncfusion components (3+ minimum)
    ↓
[Stage 4: Theme Selection] ⭐ USER DECISION #1
  Pick ONE: Bootstrap5, Tailwind3, or Material3
  Theme selected
    ↓
[Stage 5: Code Generation]
  AI generates clean .cshtml + .cs PageModel + minimal CSS
  Using selected theme (no custom colors)
    ↓
[Stage 6: Dependencies]
  AI lists required NuGet packages
  User confirms installation
    ↓
[Stage 7: Validation] 
  AI validates accessibility and code quality
    ↓
✓ Complete - Clean UI ready
```

**Stage Descriptions:**

- **Stage 1 (Intent Analysis)**: Parse user query, identify page type. Read: `references/stage-1-intent-analysis.md`
- **Stage 2 (Project Detection)**: Auto-detect .NET version and project structure. Read: `references/stage-2-project-detection.md`
- **Stage 3 (Component Mapping)**: Select Syncfusion components for the layout. Read: `references/stage-3-layout-analysis.md`
- **Stage 4 (Theme Selection)**: Choose ONE Syncfusion theme (Bootstrap5, Tailwind3, Material3). Read: `references/stage-4-theming-and-design-system.md`
- **Stage 5 (Code Generation)**: Generate clean Razor Pages using the selected theme. Read: `references/stage-5-code-generation.md`
- **Stage 6 (Dependencies)**: Install required NuGet packages. Read: `references/stage-6-dependencies.md`
- **Stage 7 (Validation)**: Validate code quality and accessibility. Read: `references/stage-7-validation.md`

**User Interaction Summary:**

| Stage | Interaction |
|-------|-------------|
| 1 | None (AI analyzes) |
| 2 | None (AI analyzes) |
| 3 | None (AI analyzes) |
| 4 | Pick theme: **Bootstrap5** / **Tailwind3** / **Material3** |
| 5 | None (AI generates) |
| 6 | Confirm NuGet installation |
| 7 | None (AI validates) |

**Total user decision gates: 1** (Stage 4: theme selection). Rest fully automated.

## Agent Instructions

### When User Requests UI Page Generation

1. **Validate scope**: Confirm request is for Razor Pages UI (not backend/API)
2. **Load guidance**: Read `stage-1-intent-analysis.md` to understand Stage 1
3. **Execute 7-stage flow**: Follow the orchestration flow shown above
4. **Progressive disclosure**: Load stage guides on-demand; load support references only when needed
5. **Maintain conversation history**: Each stage reads previous decisions from conversation context (stateless)

### Stage Execution & Reference Loading

**Stage 1: Intent Analysis**
- Read: `references/stage-1-intent-analysis.md`
- Task: Parse user query, identify page type, resolve ambiguities
- Output: Page type + modifiers + target directory

**Stage 2: Project Detection**
- Read: `references/stage-2-project-detection.md`
- Task: Auto-detect .NET version, Razor Pages structure, CSS strategy
- Output: Project configuration

**Stage 3: Layout Analysis & Component Mapping**
- Read: `references/stage-3-layout-analysis.md`
- Task: Analyze user requirements → create optimal component-mapping → map to Syncfusion tag helpers (3+ minimum)
- Output: Component mapping

**Stage 4: Theming & Design System** ⭐ USER DECISION #1
- Read: `references/stage-4-theming-and-design-system.md`
- Task: Lock CSS framework, Syncfusion theme, color system, spacing, typography, responsive breakpoints
- Output: Design system decisions + User confirmation

**Stage 5: Code Generation**
- Read: `references/stage-5-code-generation.md`
- Task: Generate Razor Pages `.cshtml` + `.cs` PageModel using theming from Stage 4
- Ensure: WCAG 2.1 AA accessibility, responsive design, antiforgery tokens applied
- Output: Generated files ready for review

**Stage 6: Dependencies**  ⭐ USER DECISION #2
- Read: `references/stage-6-dependencies.md`
- Task: Detect required NuGet packages (Syncfusion + CSS framework), resolve version conflicts
- Output: Output installation commands only; do not assume auto-install unless explicitly requested + User confirmation

**Stage 7: Validation**
- Read: `references/stage-7-validation.md` + `assets/validation-rules.md` + `references/web-standards.md`
- Task: Validate against WCAG 2.1 AA, security (antiforgery, XSS), performance, theming integration standards
- Auto-apply fixes where possible
- Output: Binary result (PASS ✓ or FAIL ✗)

### Boundary Rules (CRITICAL)

**AI agents executing this skill MUST:**

1. **UI only**: Never generate backend code (API routes, database schemas, middleware)
2. **Mock data only**: Use ViewData or hardcoded samples in PageModel; no real database calls
3. **No secrets**: Exception: environment variable for `SYNCFUSION_LICENSE_KEY` when user provides
4. **Razor Pages only**: Generate `.cshtml` + `.cshtml.cs` files in Pages directory
5. **Redirect backend requests**: *"This skill generates Razor Pages UI only. Backend integration is your app's responsibility. Ready to generate the frontend?"*
6. **Skill files are the ONLY truth**: Always read `skills/<skill-name>/references/getting-started.md` for EVERY component before generating any tag helper syntax. Never use AI training memory for tag names, attribute names, or child element names.
7. **⛔ NEVER invent tag syntax**: If no skill file exists for a component, STOP and notify the user — do NOT guess or use assumed syntax from memory. Invented tags always cause `RZ2010` / `CS0117` build errors.

### Component Skill File Path (CRITICAL)

All Syncfusion component skills are located at:
```
skills/<skill-name>/references/getting-started.md
```

The `skill` field in `component-mapping.json` (set by the component search script in Stage 3) contains the exact `<skill-name>`. Always use this to construct the file path before Stage 5 code generation.

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
- `web-standards.md` → When validating in Stage 7
- `assets/validation-rules.md` → When validating in Stage 7

**Result**: Initial load ~400 lines (SKILL.md only). Full spec available on-demand, never exceeding Agent Skills context limits.

## Configuration & User Customization

### Auto-Detected Settings

During **Stage 2 (Project Detection)**, AI automatically detects:

- **.NET Version**: .NET 8, .NET 9, .NET 10
- **Project Type**: Razor Pages, MVC
- **CSS Strategy**: Tailwind CSS, Bootstrap, Material Design, or Custom CSS
- **Formatting**: EditorConfig rules (indentation, naming conventions)
- **Pages Directory**: `Pages/`, `Views/`, or custom

### User Override Options

In **Stage 2**, user can override any detected setting:

```
Detected Settings:
  .NET Version: .NET 8
  Project Type: Razor Pages
  CSS: Tailwind CSS
  Pages Directory: Pages/

[Confirm] [Override Each] [Cancel]
```

### Syncfusion License Configuration

The skill handles license key setup:

1. **Check** for existing `SYNCFUSION_LICENSE_KEY` in configuration
2. **If missing**, prompt user: *"Get a free Community License at https://www.syncfusion.com/account/manage-trials"*
3. **If provided**, add to `appsettings.json` + register in Program.cs
4. **If skipped**, proceed but warn that watermark will appear in preview

---

## Code Generation Standards

All generated code includes:

### Accessibility (WCAG 2.1 AA)
- ✅ Semantic HTML5 with tag helpers (`<form>`, `<label>`, `<input>`, `<button>`)
- ✅ ARIA labels and descriptions
- ✅ Keyboard navigation (tab order, focus management)
- ✅ Color contrast ≥ 4.5:1
- ✅ Focus indicators on interactive elements

### Security
- ✅ Antiforgery tokens (`@Html.AntiForgeryToken()`)
- ✅ Input validation via model binding (`[BindProperty]`)
- ✅ No `Html.Raw()` without sanitization
- ✅ No hardcoded secrets

### Responsive Design
- ✅ Mobile-first CSS (320px base, then scale up)
- ✅ Flexbox/Grid layouts (no fixed widths)
- ✅ Media queries at 768px, 1024px+ breakpoints
- ✅ Touch-friendly buttons (44x44px minimum)

### Performance
- ✅ Async/await for database operations
- ✅ ViewData/TempData used appropriately
- ✅ No unnecessary script includes

### C# & Types
- ✅ Strong typing with PageModel/ViewModel classes
- ✅ XML documentation comments
- ✅ Proper null handling

## Supported Use Cases

- **Login page**: TextBox (email), TextBox (password), CheckBox (remember), Button (submit)
- **Data table page**: DataGrid with sorting, filtering, pagination, row selection
- **Dashboard page**: Multiple components orchestrated (header, sidebar, main content, footer)
- **Registration page**: Multi-form with progress indicator and validation

## Troubleshooting

**Common Issues:**

| Issue | Solution |
|-------|----------|
| "Project type not detected" | Ensure `.csproj` exists with Razor Pages SDK |
| "Syncfusion license banner appears" | Add license key via Stage 2 prompt |
| "Build fails after insertion" | Use Syncfusion component skills to resolve failures |
| "Component not rendering" | Verify tag helper registration in `_ViewImports.cshtml` |

## Additional Resources

### Quick Reference by Use Case

| Need | Reference File |
|------|-----------------|
| Understanding workflow | This SKILL.md file |
| How Stage X works | `references/stage-X-*.md` |
| Validation rules | `assets/validation-rules.md` |
| Accessibility/security | `references/web-standards.md` |
| Theme implementation | `references/syncfusion-themes.md` |

### Build Prevention Resources (NEW)

| Topic | Reference File |
|-------|-----------------|
| **Stage 2 prevention checks** | `references/stage-2-project-detection.md` |
| **Stage 5 prevention checks** | `references/stage-5-code-generation.md` |
| **Stage 6 build verification** | `references/stage-6-dependencies.md` |

## Support

For issues or questions:
1. Check Syncfusion component skills for common problems
2. Verify your project meets prerequisites (.NET 6+, Razor Pages)
3. Ensure Syncfusion license is valid and registered
4. Review generated code compliance report for warnings
