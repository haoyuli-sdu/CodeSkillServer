---
name: "generate-getx-service"
description: "**CODE GEN SKILL** — Generate a GetX service class responsible for API or repository calls. USE FOR: creating the data-access layer for a GetX feature. Triggers on: 'generate service', 'create service', 'getx service', 'generate-getx-service'. DO NOT USE FOR: UI logic (use controller); full feature scaffold (use create-getx-feature)."
---

# Generate GetX Service

Generate a `{FeatureName}Service` extending `GetxService` for API / repository calls.

## Workflow

### Step 1 — Confirm Inputs
- `{feature_name}` — snake_case
- `{FeatureName}` — UpperCamelCase
- Any specific data sources (REST API, Firestore, local DB, etc.)

### Step 2 — Generate Service

```dart
import 'package:get/get.dart';

class {FeatureName}Service extends GetxService {
  // TODO: inject HTTP client, repository, or Firestore instance
  // final _dio = Get.find<Dio>();

  Future<void> fetchData() async {
    // TODO: implement data fetching
  }

  Future<void> saveData(/* params */) async {
    // TODO: implement data persistence
  }
}
```

### Step 3 — Quality Check
- [ ] Extends `GetxService` (ensures singleton lifecycle managed by GetX)
- [ ] No Flutter widget imports
- [ ] No `BuildContext` usage
- [ ] No navigation (`Get.to / Get.back`) — navigation belongs in the controller
- [ ] All public methods are `async` returning `Future<T>`
- [ ] Run `get_errors` to confirm zero errors
