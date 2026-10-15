---
name: "create-project"
description: "Create a new .NET project or solution using dotnet new. Use when the user asks to scaffold a project, solution, class library, console app, or test project. Never write project files manually."
---

Create a new .NET project or solution using `dotnet new`. Do NOT write or modify `.csproj`, `.sln`, or related files by hand.

## Steps

1. If the template is unclear, list available templates:
   ```bash
   dotnet new --list
   ```

2. Scaffold the project:
   ```bash
   dotnet new <template> --name <name> [--output <path>] [additional options]
   ```

3. If the new project belongs to an existing solution, add it:
   ```bash
   dotnet sln <solution.sln> add <path/to/project.csproj>
   ```

4. Report what was created and where.

## Inputs

Use the template name, project name, and any extra flags provided by the user.
If the request does not make the template and target name clear, ask for the missing details before proceeding.
