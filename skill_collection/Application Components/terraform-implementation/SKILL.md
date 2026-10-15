---
name: "terraform-implementation"
description: "Generate Terraform infrastructure and deployment scaffolding for AWS based on the detected project structure, runtime stack, and explicit infrastructure inputs. Use when a developer wants to deploy an application to AWS using Terraform."
---

# Terraform Implementation

## Provides

- Project-aware Terraform scaffolding
- Runtime and service detection
- Parameterized infrastructure templates
- Runtime-aware deployment script generation based on detected services

## Use When

- A developer asks to generate Terraform infra and deployment setup
- Deploying an application to AWS using Terraform
- Generating Terraform from an existing application structure
- Bootstrapping infrastructure for frontend and backend services
- Producing deployment scaffolding that matches the project layout
- Creating a starting point that developers can refine safely

---

## Inputs

- `services`
  - service paths such as `frontend`, `backend`, `worker`
- `database`
  - optional database type such as `postgres`
- `infrastructure`
  - optional overrides such as region, VPC CIDR, cluster name, deployment style, database class, app name, frontend bucket, or container registry

## Outputs

- `infra/` Terraform files
- deployment scripts matched to the detected services
- execution steps for applying infrastructure and deployment scaffolding

## Instructions

1. Inspect the project structure and identify relevant services such as `frontend`, `backend`, or `worker`.
2. Infer the most likely AWS deployment shape from the project structure, but do not assume one fixed architecture unless the project clearly supports it.
3. Use the files in `templates/` as the Terraform scaffold source and replace placeholder values with project-aware or user-provided values.
4. Use the files in `script-templates/` only when deployment-script generation matches the detected runtime and deployment style.
5. Generate parameterized Terraform files instead of hardcoded environment-specific output.
6. Return the generated files, the next execution steps, and any important assumptions.

## Safety Notes

- Prefer input-driven or detected values over hardcoded infrastructure assumptions.
- Generate scaffolding as a starting point, not a claim of fully production-ready infrastructure.
- Call out unclear areas when the project structure does not provide enough evidence for a confident deployment plan.
- Prefer explicit infrastructure overrides when deployment style cannot be inferred confidently.
- Do not assume AWS deployment always means ECS, ALB, RDS, Docker, or S3 unless the project structure or user input supports that choice.
- Keep the output scaffold-focused and call out the parts that still require developer-specific completion.
