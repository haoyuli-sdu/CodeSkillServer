---
name: "nestjs-module"
description: "Step-by-step guide to create a new NestJS feature module following Kitchy project conventions (entity, DTO, service, controller, module, registration)"
---

## When to use

Use this skill when creating a brand new NestJS feature module from scratch in this project.

## Step-by-step Workflow

### Step 1: Create Entity (`src/<feature>/entities/<feature>.entity.ts`)

```typescript
import {
  Entity,
  PrimaryColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  BeforeInsert,
} from 'typeorm';
import { nanoid10 } from '../../utils/nanoid';

@Entity()
export class Feature {
  @PrimaryColumn({ type: 'varchar', length: 10 })
  id: string;

  // Relations - always add @JoinColumn on owning side
  @ManyToOne(() => ParentEntity, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'parent_id' })
  parent: ParentEntity;

  @Column({ name: 'parent_id', type: 'varchar', length: 10 })
  parentId: string;

  // Business columns
  @Column()
  name: string;

  @Column({ type: 'enum', enum: StatusEnum, default: StatusEnum.DEFAULT })
  status: StatusEnum;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;

  @BeforeInsert()
  generateId() {
    if (!this.id) this.id = nanoid10();
  }
}
```

**Checklist:**

- [ ] Uses `@PrimaryColumn({ type: 'varchar', length: 10 })` (NOT `@PrimaryGeneratedColumn`)
- [ ] Has `@BeforeInsert()` with `nanoid10()`
- [ ] `@JoinColumn` on owning side of every relation
- [ ] No duplicate FK columns (don't define `@Column` + `@ManyToOne` for same DB column unless `@JoinColumn.name` matches `@Column.name`)
- [ ] DB column names in `snake_case`

### Step 2: Create DTOs (`src/<feature>/dto/`)

**create-feature.dto.ts:**

```typescript
import { IsString, IsNotEmpty, IsOptional, IsEnum } from 'class-validator';

export class CreateFeatureDto {
  @IsString()
  @IsNotEmpty()
  parentId: string;

  @IsString()
  @IsNotEmpty()
  name: string;

  @IsOptional()
  @IsEnum(StatusEnum)
  status?: StatusEnum;
}
```

**update-feature.dto.ts:**

```typescript
import { PartialType } from '@nestjs/mapped-types';
import { CreateFeatureDto } from './create-feature.dto';

export class UpdateFeatureDto extends PartialType(CreateFeatureDto) {}
```

**Checklist:**

- [ ] All fields have class-validator decorators
- [ ] Required fields have `@IsNotEmpty()`
- [ ] Optional fields have `@IsOptional()`
- [ ] Enums use `@IsEnum()`
- [ ] Update DTO extends `PartialType(CreateDto)`
- [ ] No sensitive fields exposed (like `createdBy` that should come from JWT)

### Step 3: Create Service (`src/<feature>/<feature>.service.ts`)

```typescript
@Injectable()
export class FeatureService {
  constructor(
    @InjectRepository(Feature)
    private readonly featureRepository: Repository<Feature>,
  ) {}

  async create(dto: CreateFeatureDto): Promise<Feature> {
    const entity = this.featureRepository.create(dto);
    return this.featureRepository.save(entity);
  }

  async findAll(parentId: string): Promise<Feature[]> {
    return this.featureRepository.find({ where: { parentId } });
  }

  async findOne(id: string): Promise<Feature> {
    const entity = await this.featureRepository.findOne({ where: { id } });
    if (!entity) throw new NotFoundException(`Feature #${id} not found`);
    return entity;
  }

  async update(id: string, dto: UpdateFeatureDto): Promise<Feature> {
    const entity = await this.findOne(id);
    Object.assign(entity, dto); // TODO: whitelist fields instead
    return this.featureRepository.save(entity);
  }

  async remove(id: string): Promise<{ message: string }> {
    const entity = await this.findOne(id);
    await this.featureRepository.remove(entity);
    return { message: `Feature #${id} removed` };
  }
}
```

**Checklist:**

- [ ] Throws `NotFoundException` when entity not found
- [ ] Filters by parent (e.g., `storeId`) to prevent cross-tenant access
- [ ] Verifies ownership in methods that modify data

### Step 4: Create Controller (`src/<feature>/<feature>.controller.ts`)

```typescript
@Controller('features')
export class FeatureController {
  constructor(private readonly featureService: FeatureService) {}

  @UseGuards(JwtAuthGuard)
  @Post()
  create(@Body() dto: CreateFeatureDto, @Req() req: any) {
    // TODO: verify ownership of parentId
    return this.featureService.create(dto);
  }

  @UseGuards(JwtAuthGuard)
  @Get()
  findAll(@Query('parentId') parentId: string) {
    return this.featureService.findAll(parentId);
  }

  // ... other CRUD endpoints, all with @UseGuards(JwtAuthGuard)
}
```

**Checklist:**

- [ ] ALL endpoints have `@UseGuards(JwtAuthGuard)` (unless intentionally public)
- [ ] Extracts userId from `req.user?.sub`
- [ ] Passes userId to service for ownership verification

### Step 5: Create Module (`src/<feature>/<feature>.module.ts`)

```typescript
@Module({
  imports: [TypeOrmModule.forFeature([Feature])],
  controllers: [FeatureController],
  providers: [FeatureService],
  exports: [FeatureService], // if other modules need it
})
export class FeatureModule {}
```

### Step 6: Register in `src/app.module.ts`

Add the new module to the `featureModules` array:

```typescript
const featureModules = [
  // ... existing modules
  FeatureModule, // <-- add here
];
```

### Step 7: Verify

Run `npm run build` to check for compilation errors.
