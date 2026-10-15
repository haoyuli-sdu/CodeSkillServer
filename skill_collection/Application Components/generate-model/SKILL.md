---
name: "generate-model"
description: "Use when creating a new data entity and its corresponding model — creates domain Entity (pure Dart) and data Model (with JSON serialization and entity mapping)"
---

# Generate Model

Create a domain entity and its corresponding data model with serialization.

## Trigger

User says: "create model", "add entity", "new data class", or invokes `/generate-model <name>`.

## Arguments

- `name` (required): Model name in snake_case (e.g., `user`, `product`, `order_item`)

## Quick Mode

When the user provides all arguments upfront or passes `--quick`/says "use defaults", skip all interactive prompts and use these defaults:

- **Feature**: Use the first existing feature found in `lib/features/`, or "core" for shared entities
- **Fields**: Default to `id: String`

Example: `/generate-model user --quick` creates a User entity and UserModel with just an id field in the first feature.

## Process

### Step 1: Gather Information

1. **Feature**: "Which feature?" (list existing features, or "core" for shared entities)
2. **Fields**: "List the fields with types:"
   Example: `id: String, name: String, price: double, isActive: bool, createdAt: DateTime`
   Support types: `String, int, double, bool, DateTime, List<T>, Map<String, T>, custom types`

### Step 2: Create Entity

`lib/features/<feature>/domain/entities/<name>_entity.dart`:
```dart
class <Name> {
  final String id;
  final String name;
  // ... all fields as final

  const <Name>({required this.id, required this.name, ...});
}
```

Rules: pure Dart, no imports except dart:core, immutable, const constructor.

### Step 3: Create Model

`lib/features/<feature>/data/models/<name>_model.dart`:
```dart
import '../../domain/entities/<name>_entity.dart';

class <Name>Model {
  final String id;
  final String name;
  // ... all fields

  const <Name>Model({required this.id, required this.name, ...});

  factory <Name>Model.fromJson(Map<String, dynamic> json) => <Name>Model(
    id: json['id'] as String,
    name: json['name'] as String,
    // Handle type conversions:
    // DateTime: DateTime.parse(json['createdAt'] as String)
    // List<T>: (json['items'] as List).map((e) => T.fromJson(e)).toList()
    // bool: json['isActive'] as bool
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    // DateTime: 'createdAt': createdAt.toIso8601String()
  };

  <Name> toEntity() => <Name>(id: id, name: name, ...);

  factory <Name>Model.fromEntity(<Name> entity) => <Name>Model(
    id: entity.id, name: entity.name, ...
  );
}
```

### Step 4: Report

List files created. Note: entity is in domain (pure Dart), model is in data (serialization).

## Code Generation

When generating entity and model files, apply these standards:

- **Entity**: Pure Dart classes with const constructors, no dependencies
- **Model**: Adds JSON serialization (fromJson, toJson), entity conversion methods
- **Comments**: Explain the separation between Entity (domain) and Model (data)
- **Type Handling**: Support common JSON conversions (DateTime, nested objects, lists)
- **Code Organization**: Entity first (simple), then Model (with serialization logic)

Example comment in generated code:
```dart
/// User entity in the domain layer — pure Dart, no dependencies.
/// This is the core data structure used throughout the application.
class User {
  final String id;
  final String name;
  const User({required this.id, required this.name});
}

/// UserModel for data layer with JSON serialization.
/// The repository converts models to entities via toEntity().
class UserModel {
  final String id;
  final String name;

  /// Convert API JSON response to a UserModel
  factory UserModel.fromJson(Map<String, dynamic> json) => ...

  /// Serialize model to JSON for API requests
  Map<String, dynamic> toJson() => ...

  /// Convert model to domain entity
  User toEntity() => User(id: id, name: name);
}
```

## Rules Reference

- `rules/clean-architecture.md` — entity vs model separation, domain purity
- `rules/core.md` — naming conventions, null safety
