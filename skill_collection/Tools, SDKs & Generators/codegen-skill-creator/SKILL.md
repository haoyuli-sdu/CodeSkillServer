---
name: "codegen-skill-creator"
description: "Scans a project's Facade implementation to reverse-engineer its architecture and generate a reusable \"Code Generation Skill\" that accepts DDL, Technical Docs, or Requirements as input. Use this when you want to create a new Skill that automates the creation of vertical slices (Facade -> Service -> DAO) based on an existing, proven pattern in your codebase."
---

# Codegen Skill Creator

This skill analyzes a reference Facade implementation to understand your project's architecture, then generates a custom Skill that can replicate that structure for new features.

## Architecture Scope (Terminology)

### 1. Facade (The Entry Point)
A **Facade** is the outermost exposure layer of a functional unit. It is not limited to specific protocols but includes any component that triggers business logic, such as:
- **Synchronous API**: Web Controllers (REST/MVC), Dubbo/JSF Providers (RPC).
- **Asynchronous Triggers**: MQ Consumers (Message Listeners), Event Bus Subscribers.
- **Automated Tasks**: Scheduled Jobs (Cron/ElasticJob/EasyJob).
- **Other Proxies**: Gateway Handlers, GraphQL Resolvers.

### 2. The Vertical Slice (The Chain)
The "Vertical Slice" refers to the complete **Dependency Trace** starting from the Facade. 
- **The Depth is dynamic**: It follows the injection chain (Facade -> Service -> Manager -> Dao).
- **The Termination (Sink) is adaptive**: The chain ends whenever it reaches a **Persistence Layer** (DAO/Mapper) OR an **External Integration Point** (RPC Client/HTTP Client/MQ Producer).

## Workflow

### Phase 1: Input Collection & Validation

1.  **Ask for the Reference Facade Implementation Class**:
    - Get fully qualified name
    - (Optional) Get target skill name (default: `code-generator`)

2.  **Validate Reference Class Quality**:
    The reference class provided by the user should be a **clean, standard implementation** that represents the desired pattern for future code.
    Before using as reference, check:
    - [ ] Class has clear single responsibility
    - [ ] Uses standard framework annotations (Spring, etc.)
    - [ ] Has proper error handling
    - [ ] Follows team naming conventions

    **If reference class has issues:**
    > "The provided reference class has some issues (e.g., [list issues]). Should I:
    > 1. Use it anyway and document the issues in the skill?
    > 2. Find a better reference class in the codebase?
    > 3. Proceed with abstraction and note the issues?"

### Phase 2: Deep Chain Analysis (MANDATORY)

1. **Locate & Read**: Use search codebase tool to find and read the Reference Facade Class.
2. **Analyze Structure**:
   - Identify the **Module Structure** (relative paths for Facade API, Facade Impl, Service, DAO, Domain).
   - Identify **Naming Conventions** (e.g., `*FacadeImpl`, `*Service`, `*Mapper`).
3. **Trace Dependencies** (The "Vertical Slice"): Recursively follow the call graph until a Terminal Component is reached.
   - **Interface**: The Facade Interface and DTOs (Request/Response).
   - **Facade Component**: Including but not limited to JSF providers, JMQ consumers, Jobs, and Web Controllers.
   - **Service Component**: Injected Services or Managers.
   - **Terminal Component**: Data Layer (DAOs, Mappers, and Domain Entities) OR External Service Client (RPC/HTTP).
   - **Configuration**: Spring XML/Annotations, Mapper XMLs.
   - **Tests**: Associated Unit/Integration tests.

### Phase 3: Abstraction Strategy

Transform the specific code into generic templates using these rules:
- **Entity Name**: Replace `UserCoupon` with `{{Entity}}`.
- **Variable Name**: Replace `userCoupon` with `{{entity}}`.
- **Package**: Replace `com.example...` with `{{basePackage}}...`.
- **Preserve**: Annotations, imports (generic ones),  base class extensions, and structural logic.
- **Dynamic Content**: For fields and methods specific to the business logic, instruct the target skill to **adapt** them based on the input DDL/Requirement, rather than creating complex template loops.

### Phase 4: Skill Generation

Generate the new skill in `skills/code-generator/`:

1.  **Generate Assets**: Save the abstracted code as templates in `assets/java/` and `assets/xml/`.
    - Example: `assets/java/FacadeImpl.java`, `assets/xml/Mapper.xml`.
2.  **Generate SKILL.md**:
    - Read [`assets/code_generator_skill_template.md`](assets/code_generator_skill_template.md).
    - **Resolve Paths**: Replace path placeholders (e.g., `{{facade_impl_module_path}}`) with the **actual relative paths** discovered in Phase 2 (e.g., `marketing-facade/src/main/java`).
    - **Write File**: Save the fully resolved content to `skills/code-generator/SKILL.md`.

### Phase 5: Final Verification (MANDATORY)

Generated skills should be tested before delivery.

Before reporting completion:

1.  **Verify generated files**:
    - Check `SKILL.md` has correct structure
    - Check all `assets/` files exist and are valid

2.  **Check template completeness**:
    - All placeholders should be resolvable
    - No hardcoded values that should be parameterized
   
3.  **Report with evidence**:
    > "Skill generation verified:
    > - SKILL.md: created with <N> sections
    > - Assets: <N> template files
    > - Template structure: OK
    > - Placeholder resolution: OK
    > - Verification: passed"

## Guardrails

**NEVER:**

- Skip Phase 1 (Input Collection) - always get reference class first
- Skip Phase 2 (Deep Chain Analysis) - trace all dependencies
- Proceed without understanding the full vertical slice
- Generate skill without verify it
- Accept poorly structured reference code as-is (flag issues to user)
- Hardcode values that should be parameterized

**If you catch yourself doing any of these: STOP and restart the phase.**

**NO EXCUSE:**

| Excuse | Reality |
|--------|---------|
| "Reference class is clear, no deep analysis needed" | Clear ≠ complete - dependencies matter |
| "Template abstraction is simple" | Missing placeholders = broken skill |
| "Generated skill should work" | Without verification, it won't |
| "I understand the pattern, skip analysis" | Understanding ≠ correct abstraction |
| "Skip verification to save time" | Broken skill wastes more time |

**If you catch yourself thinking any of these: STOP and complete all phases.**
