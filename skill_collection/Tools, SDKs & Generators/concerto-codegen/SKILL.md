---
name: "concerto-codegen"
description: "Generate code and schema artifacts from a Concerto .cto model. Use when the user has a model and wants TypeScript, Java, Go, JSON Schema, OpenAPI, GraphQL, PlantUML, or other supported outputs; when generated artifacts are stale relative to the model; or when wiring codegen into a build pipeline."
---

# concerto-codegen

Generate downstream artifacts from [Concerto](https://github.com/accordproject/concerto) models using the Concerto CLI.

## When to use

- The user has a `.cto` model and wants types in another language
- Generated artifacts are out of date relative to the source model
- Setting up codegen as part of a build or CI pipeline

## Supported targets

`typescript`, `java`, `go`, `jsonschema`, `openapi`, `graphql`, `plantuml`, `csharp`, `xmlschema`, `protobuf`, `markdown`, `mermaid`, `avro`, `odata`, `rust`

## Approach

1. **Confirm the target format** with the user.
2. **Pick an output directory** that matches project conventions (`src/generated/`, `gen/`, etc.).
3. **Invoke the CLI:**
   ```
   npx @accordproject/concerto-cli compile \
     --model <models...> \
     --target <target> \
     --output <dir>
   ```
4. **Wire it into the build** — add an npm script like `"generate:types": "concerto-cli compile ..."` so artifacts stay in sync.
5. **Decide on git tracking** — generated files are often `.gitignore`d but checked-in is acceptable; ask the user.

## Reference

- [Concerto CLI generate](https://github.com/accordproject/concerto/tree/main/packages/concerto-cli)
- Tracking issue: [accordproject/concerto#1225](https://github.com/accordproject/concerto/issues/1225)

## Out of scope

- Editing the source model → use `concerto-author`
- Validating instances → use `concerto-validate`
