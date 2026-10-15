---
name: "create-module"
description: "Use this skill only when explicitly referred."
---

# Create Module Flow

Use `src/Modules/ProductCatalog` as the reference for all patterns.

## 1. Create Module Folder

Create `src/Modules/<Module>/` with these files and empty folders:

**Files:**
- `<Module>.csproj` — copy from `ProductCatalog.csproj`, replace all `ProductCatalog` references with `<Module>`
- `Module.cs`:
  ```csharp
  namespace <Module>;
  public class <Module>Module(IHostApplicationBuilder b) : Module(b)
  {
      public override string Key => ModuleConstants.Key;
      protected override void RegisterDbContext() => CommonRegisterDbContext<<Module>DbContext>();
  }
  public static class ModuleConstants { public const string Key = "<Module>"; }
  ```
- `GlobalUsing.cs`:
  ```csharp
  global using SharedKernel.Abstractions.Contracts;
  ```
- `<Module>DbContext.cs` — copy from `ProductCatalogDbContext.cs`, replace the class name and namespace

**Empty folders:**
- `Core/Entities`
- `Core/DTOs`
- `Api`

## 2. Register the Module

**`src/AppHost/AppHost.csproj`** — add a `<ProjectReference>` entry pointing to the new `.csproj`.

**`src/AppHost/Buildings/ModuleList.cs`** — add `using <Module>;` at the top and `new <Module>Module(builder)` to the returned list.

**`Nekomin.slnx`** — add the new project entry under the `Modules` folder group.
