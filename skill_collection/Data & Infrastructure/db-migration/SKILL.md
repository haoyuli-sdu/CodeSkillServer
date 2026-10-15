---
name: "db-migration"
description: "编写数据库迁移脚本、执行数据库结构变更、使用Prisma/TypeORM/Knex迁移"
---

# 数据库迁移工具

生成数据库迁移脚本，支持多种 ORM

## 使用方式

```
/db-migration <action> [options]
```

**参数说明：**
- `<action>`: 迁移操作 - `create` | `alter` | `drop` | `seed`
- `--orm`: ORM 类型 - `knex` | `prisma` | `typeorm` | `sequelize` (默认 knex)

## 快速生成

### Knex.js 迁移

```bash
# 创建迁移文件
pnpm knex migrate:make create_users_table --knexfile knexfile.ts

# 运行迁移
pnpm knex migrate:latest

# 回滚
pnpm knex migrate:rollback
```

```typescript
// migrations/20240320000000_create_users_table.ts
import { Knex } from 'knex'

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('users', (table) => {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'))
    table.string('username', 50).notNullable().unique()
    table.string('email', 255).notNullable().unique()
    table.string('password_hash', 255).notNullable()
    table.string('nickname', 100)
    table.string('avatar', 500)
    table.enum('status', ['active', 'inactive', 'banned']).defaultTo('active')
    table.timestamp('created_at').defaultTo(knex.fn.now())
    table.timestamp('updated_at').defaultTo(knex.fn.now())

    // 索引
    table.index('email')
    table.index('status')
  })

  // 创建触发器自动更新 updated_at
  await knex.raw(`
    CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
  `)
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('users')
}
```

### Prisma 迁移

```bash
# 创建迁移
pnpm prisma migrate dev --name add_users_table

# 部署迁移
pnpm prisma migrate deploy

# 重置数据库
pnpm prisma migrate reset
```

```prisma
// prisma/schema.prisma
model User {
  id          String   @id @default(uuid())
  username    String   @unique @db.VarChar(50)
  email       String   @unique @db.VarChar(255)
  passwordHash String  @map("password_hash") @db.VarChar(255)
  nickname    String?  @db.VarChar(100)
  avatar      String?  @db.VarChar(500)
  status      Status   @default(ACTIVE)
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  @@map("users")
}

enum Status {
  ACTIVE   @map("active")
  INACTIVE @map("inactive")
  BANNED   @map("banned")
}
```

### TypeORM 迁移

```typescript
// src/migrations/1710921600000-CreateUsersTable.ts
import { MigrationInterface, QueryRunner, Table, TableIndex } from 'typeorm'

export class CreateUsersTable1710921600000 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.createTable(
      new Table({
        name: 'users',
        columns: [
          {
            name: 'id',
            type: 'uuid',
            isPrimary: true,
            default: 'uuid_generate_v4()',
          },
          {
            name: 'username',
            type: 'varchar',
            length: '50',
            isUnique: true,
          },
          {
            name: 'email',
            type: 'varchar',
            length: '255',
            isUnique: true,
          },
          {
            name: 'password_hash',
            type: 'varchar',
            length: '255',
          },
          {
            name: 'created_at',
            type: 'timestamp',
            default: 'now()',
          },
          {
            name: 'updated_at',
            type: 'timestamp',
            default: 'now()',
          },
        ],
      }),
      true,
    )

    await queryRunner.createIndex(
      'users',
      new TableIndex({
        name: 'IDX_users_email',
        columnNames: ['email'],
      }),
    )
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.dropTable('users')
  }
}
```

## 迁移模板

### 创建表模板

```typescript
// {{timestamp}}_create_{{table}}_table.ts
import { Knex } from 'knex'

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('{{table}}', (table) => {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'))
    // {{columns}}
    table.timestamp('created_at').defaultTo(knex.fn.now())
    table.timestamp('updated_at').defaultTo(knex.fn.now())
  })
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('{{table}}')
}
```

### 添加列模板

```typescript
// {{timestamp}}_add_{{columns}}_to_{{table}}.ts
import { Knex } from 'knex'

export async function up(knex: Knex): Promise<void> {
  await knex.schema.alterTable('{{table}}', (table) => {
    // table.string('new_column', 100).nullable()
  })
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.alterTable('{{table}}', (table) => {
    // table.dropColumn('new_column')
  })
}
```

### 种子数据模板

```typescript
// seeds/{{name}}_seed.ts
import { Knex } from 'knex'

export async function seed(knex: Knex): Promise<void> {
  // 清空表
  await knex('{{table}}').del()

  // 插入数据
  await knex('{{table}}').insert([
    {
      id: 'xxx',
      name: 'xxx',
    },
  ])
}
```

## 最佳实践

1. **命名规范**：`{timestamp}_{action}_{table}_table`
2. **可逆性**：每个迁移必须有 down 方法
3. **幂等性**：迁移可重复运行
4. **原子性**：一个迁移只做一件事
5. **测试**：在测试环境验证后再执行
