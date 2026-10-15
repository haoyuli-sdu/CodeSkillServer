---
name: "generate-rails"
description: "Generate Rails CRUD scaffold with Model, Controller, Serializer, Migration, Routes, and RSpec tests"
---

# Generate Rails CRUD Scaffold

Generate a complete Rails CRUD scaffold for the given entity.

## What To Do

1. **Model** with ActiveRecord validations, associations, and scopes
2. **Migration** with typed columns, null constraints, and indexes
3. **Controller** with RESTful actions, strong_params, and before_action callbacks
4. **Serializer** using ActiveModelSerializers or Jbuilder views
5. **Routes** entry with resources :entity_name
6. **RSpec tests**: model spec, request spec, factory definition

## Structure

```
app/
  models/{entity_name}.rb
  controllers/{entity_name_plural}_controller.rb
  serializers/{entity_name}_serializer.rb

db/migrate/
  {timestamp}_create_{entity_name_plural}.rb

spec/
  models/{entity_name}_spec.rb
  requests/{entity_name_plural}_spec.rb
  factories/{entity_name_plural}.rb
```

## Patterns
- strong_params with permit for each allowed attribute
- before_action :set_{entity_name} for show/update/destroy
- frozen_string_literal: true on every generated file
- Guard clauses: render error and return early on validation failure
- Scopes as lambdas on the model

## Arguments
- `<entity-name>`: Entity name in PascalCase (e.g., JobOffer, Candidate)
- `--api`: API-only mode — skips views/serializers, renders JSON directly
