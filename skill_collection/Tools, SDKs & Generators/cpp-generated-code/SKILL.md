---
name: "cpp-generated-code"
description: "Change or review C/C++ generated sources, generator directives, schemas, IDL/protobuf bindings, codegen templates, or generated build outputs. Use when editing a generated file or its generator input."
---

# Generated code

Risk: a direct generated-file edit is overwritten or diverges from its generator.

1. Identify the generator command, source inputs, generated outputs, and repository policy from build files and file headers.
2. Change the generator input/template, not generated output, unless policy explicitly marks the output hand-maintained.
3. Regenerate with the pinned local toolchain; inspect the diff for only expected outputs.
4. Build a consumer of the generated API and keep the generator invocation reproducible.

Do not hand-edit generated code or install an unverified generator version to make regeneration work.
