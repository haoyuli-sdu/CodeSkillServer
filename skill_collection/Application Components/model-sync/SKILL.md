---
name: "model-sync"
description: "全栈数据模型同步工具,整合三层模型转换:(1) SQL → ORM (PostgreSQL DDL生成SQLAlchemy实体),(2) ORM → VO/DTO (从ORM生成Pydantic响应/请求模型),(3) DTO/VO → TypeScript (后端模型同步到前端类型)。当用户要求\"同步模型\"、\"生成实体类\"、\"生成VO/DTO\"、\"同步前后端类型\"或\"更新数据模型\"时激活。"
---

# 全栈数据模型同步技能

## 技能概述

提供完整的数据模型生命周期管理,打通从数据库到前端的全链路类型同步:

```
PostgreSQL SQL
    ↓ (1) SQL → ORM
SQLAlchemy ORM 实体类
    ↓ (2) ORM → VO/DTO
Pydantic DTO/VO 模型
    ↓ (3) DTO/VO → TypeScript
前端 TypeScript 类型
```

**核心价值**:
- ✅ **类型一致性**: 确保数据库、后端、前端三层类型完全一致
- ✅ **开发效率**: 自动生成样板代码,减少手工维护成本
- ✅ **增量更新**: 支持覆盖/增量模式,保护现有业务逻辑

## 同步模式

### 模式 1: SQL → ORM

根据 PostgreSQL DDL 生成 SQLAlchemy 实体类。

**输入**:
- `sqlFilePath` (必选): SQL 文件路径,如 `docker/pg/init/*GraphEdu*.sql`
- `ormDir` (可选): ORM 输出目录,默认 `graphedu/common/models/orm`
- `moduleMapping` (可选): 表前缀→模块映射,默认 `{sys_: system, biz_: business, ...}`

**详细规范**: 见 [references/sql-to-orm.md](references/sql-to-orm.md)

### 模式 2: ORM → VO/DTO

从 SQLAlchemy ORM 生成 Pydantic 响应/请求模型。

**输入**:
- `ormModule` (必选): ORM 模块名,如 `system`, `education`
- `dtoDir` (可选): DTO 输出目录,默认 `graphedu/common/models/dto`
- `voDir` (可选): VO 输出目录,默认 `graphedu/common/models/vo`
- `generateDTO` (可选): 是否生成 DTO,默认 `false`
- `generateVO` (可选): 是否生成 VO,默认 `true`

**详细规范**: 见 [references/orm-to-vo-dto.md](references/orm-to-vo-dto.md)

### 模式 3: DTO/VO → TypeScript

同步后端 Pydantic 模型到前端 TypeScript 类型。

**输入**:
- `backendModule` (必选): 后端模块路径,如 `graphedu/api/services/system`
- `frontendTypesDir` (可选): 前端类型目录,默认 `graphedu-ui/src/types/modules`
- `frontendApiDir` (可选): 前端 API 目录,默认 `graphedu-ui/src/api`

**详细规范**: 见 [references/backend-to-frontend.md](references/backend-to-frontend.md)

## 执行流程

### 步骤 1: 确定同步模式

根据用户需求自动识别同步模式:

| 用户指令示例                            | 同步模式          | 触发时机                    |
|----------------------------------------|------------------|---------------------------|
| "同步 PG 数据库表结构" / "生成实体类"    | SQL → ORM        | 数据库 schema 变更后        |
| "从 ORM 生成 VO" / "生成响应模型"       | ORM → VO/DTO     | ORM 变更后,需要 VO/DTO      |
| "同步前后端接口" / "生成前端类型"        | DTO/VO → TS      | 后端模型变更后              |
| "完整同步" / "更新所有模型"             | 全链路 (1→2→3)   | 大版本更新或初次初始化      |

### 步骤 2: 检查现有文件

扫描目标目录,询问用户更新策略:

- **覆盖模式**: 删除现有文件,完全重新生成 (推荐用于大版本更新)
- **增量模式**: 保留现有文件,仅添加/更新对应模型 (推荐用于日常开发)
- **交互模式**: 逐个确认每个模型是否覆盖

### 步骤 3: 执行同步

根据选择的模式调用对应的转换逻辑:

- **模式 1**: 解析 SQL → 生成 ORM 类
- **模式 2**: 读取 ORM → 生成 VO/DTO
- **模式 3**: 扫描 API 路由 → 生成 TypeScript 类型和 API 函数

### 步骤 4: 验证生成结果

- 检查导入路径正确性
- 验证类型注解完整性
- 确认命名转换规则 (snake_case ↔ camelCase)
- 运行 `uv run -m graphedu lint check` 验证代码质量

## 核心转换规则

### 命名转换

| 层级       | 命名风格         | 示例                          |
|-----------|-----------------|------------------------------|
| 数据库表   | snake_case      | `sys_user_detail`            |
| ORM 类名   | PascalCase      | `SysUserDetail`              |
| VO/DTO 类名| PascalCase      | `UserDetailVO`, `UserCreateDTO` |
| TypeScript | PascalCase      | `UserDetailVO`, `UserCreateDTO` |
| 字段 (Python)| snake_case    | `user_id`, `create_time`     |
| 字段 (TS)  | camelCase       | `userId`, `createTime`       |

### 类型映射

**PostgreSQL → Python**:
- `BIGINT` → `BigInteger` / `int`
- `VARCHAR(n)` → `String(n)` / `str`
- `JSONB` → `JSONB` / `dict`
- `TIMESTAMP` → `DateTime` / `datetime`
- `UUID` → `UUID(as_uuid=True)` / `UUID`

**Python → TypeScript**:
- `str` → `string`
- `int` → `number`
- `datetime` → `string` (ISO 8601)
- `list[T]` → `T[]`
- `T | None` → `T | null` (添加 `?` 可选标记)

### 字段过滤规则

**VO 模型** (响应):
- ✅ 包含: 业务字段、关联信息 (role_ids, dept_ids)
- ❌ 排除: password, 敏感字段

**DTO 模型** (请求):
- **CreateDTO**: 必填业务字段 (排除 id, create_time)
- **UpdateDTO**: 可选业务字段
- **QueryDTO**: 查询条件字段,继承 `PageQuery`

完整映射表见各模式的参考文档。

## 项目约定

### 目录结构

```
graphedu/common/models/
├── orm/               # SQLAlchemy 实体类
│   ├── system.py      # SysUser, SysRole, ...
│   └── education.py   # EduCourse, EduStudent, ...
├── dto/               # Pydantic 请求模型
│   ├── user.py        # UserCreateDTO, UserUpdateDTO, ...
│   └── auth.py
├── vo/                # Pydantic 响应模型
│   ├── user.py        # UserDetailVO, UserListVO, ...
│   └── auth.py
└── po/                # 持久化对象 (组合 ORM)
    └── user.py        # UserDetail, CurrentUser

graphedu-ui/src/
├── types/modules/     # TypeScript 类型
│   ├── user.ts        # UserDetailVO, UserCreateDTO, ...
│   └── common.ts      # PageResponse, ResponseType
└── api/               # API 请求函数
    ├── user.ts        # getUserList, createUser, ...
    └── auth.ts
```

### 基类继承

- **DTO**: 继承自 `graphedu.common.models.dto.base.DTO`
- **VO**: 使用 `BaseModel` + `ConfigDict(from_attributes=True)`
- **QueryDTO**: 继承自 `PageQuery` (提供分页字段)

### 特殊场景

1. **分页响应**: 统一使用 `PageResponse<T>`
2. **关联字段**: VO 中包含 `role_ids: list[int]`, 但 ORM 通过关系映射
3. **计算字段**: VO 中的 `avatar_url` 不在 ORM 中,由运行时计算
4. **枚举字段**: 使用 `Literal['0', '1']` 严格限制值

## 注意事项

### ⚠️ 覆盖模式风险

- 使用覆盖模式会**删除现有文件**,请确保已提交代码
- 增量模式更安全,但可能产生冗余代码
- 建议首次生成使用覆盖,后续使用增量

### ⚠️ 类型导入

- ORM 导入: `from sqlalchemy.dialects.postgresql import JSONB, UUID`
- VO/DTO 导入: `from pydantic import Field, BaseModel`
- TypeScript 导入: 顺序为 `common` → `模块类型`

### ⚠️ 字段注释

- Python 使用 `Field(description="...")`
- TypeScript 使用 JSDoc `/** ... */`
- 所有字段**必须包含描述**,方便生成文档

## 快速示例

### 示例 1: 仅同步 ORM

```bash
# 用户需求: "数据库新增了 sys_log 表,帮我同步 ORM"
触发: SQL → ORM 模式
输入: sqlFilePath="docker/pg/init/02-GraphEdu-system.sql"
输出: graphedu/common/models/orm/system.py (新增 SysLog 类)
```

### 示例 2: ORM → VO/DTO

```bash
# 用户需求: "从 SysUser ORM 生成 VO 和 DTO"
触发: ORM → VO/DTO 模式
输入: ormModule="system", generateVO=true, generateDTO=true
输出:
  - graphedu/common/models/vo/user.py (UserDetailVO, UserListVO, ...)
  - graphedu/common/models/dto/user.py (UserCreateDTO, UserUpdateDTO, ...)
```

### 示例 3: 完整同步

```bash
# 用户需求: "完整同步用户模块的所有模型"
触发: 全链路模式
步骤:
  1. SQL → ORM: 更新 SysUser 实体类
  2. ORM → VO/DTO: 生成 UserDetailVO, UserCreateDTO, ...
  3. DTO/VO → TS: 生成 user.ts 类型文件和 API 函数
```

## 参考文档

- **SQL → ORM 详细规范**: [references/sql-to-orm.md](references/sql-to-orm.md)
- **ORM → VO/DTO 详细规范**: [references/orm-to-vo-dto.md](references/orm-to-vo-dto.md)
- **DTO/VO → TypeScript 详细规范**: [references/backend-to-frontend.md](references/backend-to-frontend.md)
- **完整类型映射表**: [references/type-mapping-table.md](references/type-mapping-table.md)
