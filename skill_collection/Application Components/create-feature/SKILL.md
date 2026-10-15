---
name: "create-feature"
description: "Generate a complete NestJS feature module from a DBML specification. Use when the user wants to create a new feature with entities, repository, service, controller, DTOs, tests, and module in one go. Input can be DBML + method requirements in conversational format."
---

# Create Feature Skill

Generate a complete, production-ready **NestJS feature module** from a DBML database schema specification and functional requirements. The skill creates a fully-typed, testable, and documented feature following the exact patterns from the `users` module.

## What This Skill Creates

For a single feature request, the skill auto-generates:

1. **Entity** (`entities/<Entity>.entity.ts`) — TypeORM entity with UUID PK, timestamps, relations
2. **Repository** (`repositories/<Entity>.repository.ts`) — Data access layer with CRUD + custom methods
3. **Service** (`services/<feature>.service.ts`) — Business logic layer with validations, error handling, `@Transactional()`
4. **Controller** (`controllers/<feature>.controller.ts`) — HTTP endpoints, Zod validation, full Swagger docs
5. **DTOs** (`dto/<action>-<entity>.dto.ts`) — Zod schemas + TypeScript types + Swagger classes
6. **Unit Tests** (`services/<feature>.service.spec.ts`) — Jest tests covering happy paths + errors
7. **Module** (`<feature>.module.ts`) — NestJS module with imports, providers, exports
8. **Integrations** — Auto-updates `app.module.ts` with imports + exports

**Total**: 7-10 new files, 1 modified file (`app.module.ts`), fully integrated and tested.

---

## How to Use This Skill

### Step 1: Provide Your Feature Specification

Describe your feature in **conversational format** including:

#### A) **Database Schema (DBML format)**

```dbml
Table events {
  id uuid [pk, default: "uuid()"]
  name varchar [not null]
  datetime timestamp [not null]
  status varchar [default: "draft"]
  venue_id uuid [ref: > venues.id]
  created_at timestamp [default: `now()`]
  updated_at timestamp
}

Table venues {
  id uuid [pk, default: "uuid()"]
  name varchar [not null]
  city varchar [not null]
  capacity int
  created_at timestamp [default: `now()`]
  updated_at timestamp
}
```

#### B) **Required Methods / Endpoints**

```
Methods needed:
- createEvent(name, datetime, venueId)
- getEventById(eventId)
- listAllEvents()
- updateEvent(eventId, data)
- deleteEvent(eventId)
- Custom: findEventsByVenue(venueId) → returns array of events for a venue
- Custom: findUpcomingEvents() → returns events where datetime > now
```

#### C) **Validations & Rules (optional)**

```
Validations:
- name: min 3, max 255 chars
- datetime: must be in future
- venueId: must exist in venues table
- Enums: status can be 'draft' | 'published' | 'cancelled'

Error cases:
- 404 if venue doesn't exist
- 400 if datetime is in past
- 409 if event already exists for venue
```

#### D) **Additional Notes (optional)**

```
Authentication: Require AuthGuard
Transactions: Use @Transactional for multi-table updates
Soft delete: Include soft delete support
```

### Step 2: Skill Parses & Plans

The skill will:

1. **Parse DBML** → Extract tables, columns, relations, enums
2. **Infer structure** → Feature folder, Entity class names, method signatures
3. **Present plan**:
   ```
   📋 PLAN: Event Management Feature
   ──────────────────────────────────
   
   Entities to create:
   ✓ Event (from table: events)
   ✓ Venue (from table: venues)
   
   Methods to implement:
   ✓ CRUD: create, getById, listAll, update, delete
   ✓ Custom: findEventsByVenue(venueId), findUpcomingEvents()
   
   DTOs:
   ✓ CreateEventDto (name, datetime, venueId)
   ✓ UpdateEventDto (partial)
   
   Validations:
   ✓ name: z.string().min(3).max(255)
   ✓ datetime: z.coerce.date().refine(d => d > new Date(), ...)
   
   Endpoints:
   ✓ POST   /events               → createEvent
   ✓ GET    /events/:id           → getEventById
   ✓ GET    /events               → listAllEvents
   ✓ PATCH  /events/:id           → updateEvent
   ✓ DELETE /events/:id           → deleteEvent
   ✓ GET    /events/venue/:venueId → findEventsByVenue
   ✓ GET    /events/upcoming       → findUpcomingEvents
   
   Files to create: 9
   Files to modify: 1 (app.module.ts)
   
   ✅ Looks good? (yes / no / changes needed)
   ```

3. **Wait for confirmation** — Allow user to adjust before generating

### Step 3: Skill Auto-Generates All Files

If approved, generates:

**Entity** (`src/events/entities/event.entity.ts`):
- UUID primary key
- All columns from DBML with correct types & decorators
- Relations (@ManyToOne to Venue, etc.)
- timestamps (createdAt, updatedAt)
- Enums (status)

**Repository** (`src/events/repositories/event.repository.ts`):
- Extends `Repository<Event>`
- `getRepository(queryRunner?)` helper for transactions
- Methods: `findAll()`, `findOneById()`, `createEntity()`, `updateEntity()`, `softDeleteEntity()`
- Custom: `findEventsByVenue(venueId)`, `findUpcomingEvents()`
- All accept `queryRunner?: QueryRunner` for `@Transactional()` support

**Service** (`src/events/services/events.service.ts`):
- Injects `EventRepository` + `DataSource`
- Methods: `createEvent()`, `getEventById()`, `listAllEvents()`, `updateEvent()`, `deleteEvent()`
- Custom: `findEventsByVenue()`, `findUpcomingEvents()`
- Each with validations, error handling (NotFoundException, BadRequest), `@Transactional()`

**Controller** (`src/events/controllers/events.controller.ts`):
- Route prefix: `/events`
- Endpoints: POST, GET /:id, GET, PATCH /:id, DELETE /:id, GET /venue/:venueId, GET /upcoming
- Full Swagger docs (@ApiOperation, @ApiResponse, @ApiBody)
- ZodValidationPipe for input validation
- Response wrapper: `{ status: 'success', data: {...} }`

**DTOs** (`src/events/dto/create-event.dto.ts` + `update-event.dto.ts`):
- Create DTO:
  - Zod schema: `z.object({ name: z.string().min(3).max(255), datetime: z.coerce.date().refine(...), venueId: z.string().uuid() })`
  - Type: `CreateEventDto = z.infer<typeof CreateEventSchema>`
  - SwaggerDto class: `export class CreateEventSwaggerDto { @ApiProperty() name: string; ... }`
- Update DTO: same but `.partial()`

**Tests** (`src/events/services/events.service.spec.ts`):
- TestingModule setup
- Mocks: EventRepository, DataSource
- Test cases:
  - ✓ createEvent happy path
  - ✓ createEvent validation error (invalid datetime)
  - ✓ getEventById success
  - ✓ getEventById not found
  - ✓ listAllEvents
  - ✓ updateEvent
  - ✓ deleteEvent
  - ✓ findEventsByVenue
  - ✓ findUpcomingEvents

**Module** (`src/events/events.module.ts`):
```typescript
@Module({
  imports: [TypeOrmModule.forFeature([Event, Venue])],
  controllers: [EventsController],
  providers: [EventsService, EventRepository],
  exports: [EventsService],
})
export class EventsModule {}
```

**app.module.ts** (auto-updated):
```typescript
import { EventsModule } from 'src/events/events.module';

@Module({
  imports: [
    // ... existing modules
    EventsModule,  // ← inserted
  ],
})
export class AppModule {}
```

### Step 4: Validation & Checklist

Skill validates:
- ✅ All entities have `id`, `createdAt`, `updatedAt`
- ✅ Types are TypeScript strict (no `any`)
- ✅ Zod schemas cover all DTO fields
- ✅ Service has error handling (RFC9457 ProblemDetails)
- ✅ Tests cover happy paths + error cases
- ✅ Swagger docs are complete
- ✅ Relations are correctly decorated

Then shows checklist:
```
✅ Files Generated:
   - src/events/entities/event.entity.ts
   - src/events/repositories/event.repository.ts
   - src/events/services/events.service.ts
   - src/events/services/events.service.spec.ts
   - src/events/controllers/events.controller.ts
   - src/events/dto/create-event.dto.ts
   - src/events/dto/update-event.dto.ts
   - src/events/events.module.ts
   - src/events/dto/index.ts (exports)

✅ Files Modified:
   - src/app.module.ts

📝 Next Steps:
   1. npm run migration:generate -- src/core/database/migrations/CreateEventsTables
   2. Review and edit migration if needed
   3. npm run migration:run
   4. npm test -- src/events
   5. npm run start:dev
   6. Test endpoints: curl http://localhost:3000/events

🔍 Verify:
   - POST /events returns 201 with created event
   - GET /events/:id returns 200 with event details
   - PATCH /events/:id with invalid datetime returns 400
   - DELETE /events/:id returns 204
```

---

## Pattern Guidelines

All generated code follows strict patterns from the `users` module:

### Entity Pattern
```typescript
@Entity('{table_name}')
export class {EntityClass} {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ ... })
  fieldName!: type;

  @ManyToOne(() => OtherEntity)
  @JoinColumn({ name: 'other_entity_id' })
  otherEntity!: OtherEntity;

  @CreateDateColumn({ name: 'created_at' })
  createdAt!: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt!: Date;
}
```

### Repository Pattern
```typescript
@Injectable()
export class {EntityRepository} extends Repository<{Entity}> {
  constructor(private dataSource: DataSource) {
    super({Entity}, dataSource.createEntityManager());
  }

  private getRepository(queryRunner?: QueryRunner) {
    return queryRunner ? queryRunner.manager.getRepository({Entity}) : this;
  }

  async findOneById(id: string, queryRunner?: QueryRunner): Promise<{Entity} | null> {
    return this.getRepository(queryRunner).findOne({ where: { id }, relations: [...] });
  }

  // ALL methods accept queryRunner for @Transactional support
}
```

### Service Pattern
```typescript
@Injectable()
export class {Service} {
  constructor(
    private readonly repository: {Repository},
    private readonly dataSource: DataSource,
  ) {}

  @Transactional()
  async create(data: CreateDto, queryRunner?: any): Promise<Entity> {
    // business logic
    return this.repository.createEntity(data, queryRunner);
  }

  async getById(id: string): Promise<Entity> {
    const entity = await this.repository.findOneById(id);
    if (!entity) throw new NotFoundException({...});
    return entity;
  }
}
```

### Controller Pattern
```typescript
@Controller('route')
@UseGuards(AuthGuard)
export class {Controller} {
  @Post()
  @ApiOperation({ summary: '...', description: '...' })
  @ApiBody({ type: SwaggerDto })
  @ApiResponse({ status: 201, schema: { example: {...} } })
  async create(
    @Body(new ZodValidationPipe(Schema)) body: Dto,
  ): Promise<ApiSuccess<Entity>> {
    return { status: 'success', data: await this.service.create(body) };
  }
}
```

### DTO Pattern
```typescript
// Zod schema (validation)
export const CreateSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
});

// Type (inferred)
export type CreateDto = z.infer<typeof CreateSchema>;

// Swagger class (documentation)
export class CreateSwaggerDto {
  @ApiProperty({ type: 'string', minLength: 2, maxLength: 100 })
  name: string;

  @ApiProperty({ type: 'string', format: 'email' })
  email: string;
}
```

---

## Example Complete Conversation

```
USER:
I need a new feature called "Rooms" for event venues.

DBML:
Table rooms {
  id uuid [pk, default: "uuid()"]
  name varchar [not null]
  capacity int [not null]
  venue_id uuid [not null, ref: > venues.id]
  created_at timestamp [default: `now()`]
  updated_at timestamp
}

Methods:
- createRoom(name, capacity, venueId)
- getRoomById(roomId)
- listRoomsByVenue(venueId)
- updateRoom(roomId, data)
- deleteRoom(roomId)

Validations:
- name: min 3, max 100 chars
- capacity: min 1, max 10000

SKILL (Phase 2):
[Presents plan]
📋 PLAN: Room Management Feature
- Entity: Room (from table rooms)
- Methods: CRUD + listRoomsByVenue
- DTOs: CreateRoomDto, UpdateRoomDto
- Endpoints: POST, GET/:id, GET/venue/:venueId, PATCH/:id, DELETE/:id
- Files: 8, Modifications: 1

✅ Ready? 

USER: Yes!

SKILL (Phase 3-4):
[Auto-generates all files]
✅ 8 files created
✅ 1 file modified (app.module.ts)
✅ All validations passed

🔄 Next Steps:
1. npm run migration:generate -- CreateRoomsTable
2. npm run migration:run
3. npm test -- src/rooms
4. npm run start:dev

USER: Done! Tests pass, endpoints work 🎉
```

---

## What This Skill Does NOT Do

- ❌ Generate database migrations (user creates based on DBML)
- ❌ Create E2E tests (only unit tests in .service.spec.ts)
- ❌ Generate documentation in `/doc`
- ❌ Deploy or configure infrastructure

---

## Architecture Decisions

| Decision | Why |
|----------|-----|
| Input: Conversational + DBML | Maximum flexibility; agentcan understand context |
| Output: Auto-generate everything | Accelerates dev; patterns are predictable |
| No migration generation | DBAs/devs often customize; TypeORM auto-gen imperfect |
| Tests: Service layer only | Max coverage of business logic |
| Zod + SwaggerDto separate | Each tool is specialized for its job |
| @Transactional decorator | Guarantees atomicity for multi-table ops |

---

## Commands After Generation

```bash
# 1. Create migration based on DBML changes
npm run migration:generate -- src/core/database/migrations/Create<Feature>Table

# 2. Apply migration
npm run migration:run

# 3. Run unit tests for your feature
npm test -- src/<feature>

# 4. Development server (watch mode)
npm run start:dev

# 5. Type check
npx tsc --noEmit
```

---

## Troubleshooting

**Q: Skill generated Entity but relations don't work**
A: Verify DBML refs are correct and both entities exist. Skill creates @ManyToOne/@OneToMany automatically.

**Q: Tests fail due to mock mismatch**
A: Review .service.spec.ts mock objects vs actual service method signatures.

**Q: Swagger docs missing endpoint details**
A: Skill includes @ApiOperation, @ApiBody, @ApiResponse; custom endpoints may need manual @ApiResponse.

**Q: app.module.ts not updated with imports**
A: If error, manually add: `import { NewModule } from 'src/new-feature/new-feature.module'` and add to imports array.

---

## Next: Use This Skill

Simply describe your feature in conversational format with DBML + methods, and the skill will generate everything! 🚀

Example prompts:
- _"Create a Comments feature with tables comments, replies. Methods: create, get, list by post, update, delete"_
- _"I need a Gallery feature: images table, methods to upload, list, delete. Image must belong to event."_
- _"Build an Invitations feature: users can invite other users to events. Track RSVP status."_

