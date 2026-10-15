---
name: "entity-create"
description: "生成实体类的时候使用此skill"
---

# 我的要求
- sql依据`@docs/sql`
- 前端实体类路径：`src/types/{实体}.ts`
  - ts 文件名使用小写
  - 属性命名使用`camelCase`
- 后端实体类路径：`src/**/model/entity/{实体}/{实体}.java`
  - 实体多包一层目录
  -  属性命名使用`camelCase`

# SQL → 实体类 生成 Skill

## 工作流程

1. **解析 SQL** — 从 CREATE TABLE 语句中提取：表名、字段名、字段类型（含精度）、是否 NULL、DEFAULT 值、COMMENT
2. **确认目标语言** — 如果用户没有说明，询问：Python dataclass / Python SQLAlchemy / Java MyBatis-Plus / TypeScript interface / TypeScript class
3. **按模板生成代码** — 严格遵循下方各语言的格式规范
4. **只输出纯代码** — 不加任何解释文字、Markdown 标题、说明段落

---

## 通用解析规则

### 类名（大驼峰）
- 去除表名前缀（如 `t_`、`tb_`），再将 `_` 分隔的每个单词首字母大写
- 示例：`t_user_info` → `UserInfo`，`order_detail` → `OrderDetail`

### 字段类型映射

| SQL 类型 | Python | Java | TypeScript |
|---|---|---|---|
| `INT` / `INTEGER` / `BIGINT` | `int` | `Long` / `Integer` | `number` |
| `TINYINT(1)` | `bool` | `Boolean` | `boolean` |
| `TINYINT`（其余） | `int` | `Integer` | `number` |
| `SMALLINT` | `int` | `Integer` | `number` |
| `VARCHAR` / `CHAR` / `TEXT` / `LONGTEXT` | `str` | `String` | `string` |
| `DATE` | `datetime.date` | `LocalDate` | `string` |
| `DATETIME` / `TIMESTAMP` | `datetime.datetime` | `LocalDateTime` | `string` |
| `FLOAT` / `DOUBLE` | `float` | `Double` | `number` |
| `DECIMAL` | `float` | `BigDecimal` | `number` |
| `JSON` | `str` | `String` | `Record<string, unknown>` |
| `UNSIGNED` 修饰 | 忽略（不影响类型映射） | 同上 | 同上 |

### 默认值规则
- SQL 中有 `DEFAULT xxx`：严格使用该值（字符串加引号，数字直接用）
- SQL 中无 `DEFAULT`：
  - `str` → `''`（空字符串）
  - `int` / `float` → `0`
  - `bool` → `False`
  - `datetime.*` → `None`

### 注释规则
- 有 `COMMENT 'xxx'`：使用 COMMENT 内容
- 无 COMMENT：根据字段名推断语义（如 `create_time` → "创建时间"，`user_id` → "用户ID"）

---

## Python — dataclass 模板

```python
import dataclasses
import datetime


@dataclasses.dataclass
class {ClassName}:
    {field_name}: {type} = {default}  # {注释}
```

**规则：**
- 属性名与 SQL 字段名**完全一致**（保留下划线，不做转换）
- 必须 `import datetime` 如果有日期类型字段
- 输出严格按模板，不加 `__init__`、`__repr__`、`@property` 等额外内容
- `id` 等主键字段默认值为 `0`（int），不特殊处理

**示例输出：**
```python
import dataclasses
import datetime


@dataclasses.dataclass
class UserInfo:
    id: int = 0  # 用户ID
    username: str = ''  # 用户名
    status: bool = False  # 是否启用
    score: float = 0  # 积分
    create_time: datetime.datetime = None  # 创建时间
```

---

## Python — SQLAlchemy 模板

```python
import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean, Float, Text


class Base(DeclarativeBase):
    pass


class {ClassName}(Base):
    __tablename__ = "{table_name}"

    {field_name}: Mapped[{type}] = mapped_column({ColumnType}({size}), default={default})  # {注释}
```

**规则：**
- 主键字段加 `primary_key=True`
- `VARCHAR(n)` → `mapped_column(String(n), ...)`
- `DATETIME` / `TIMESTAMP` → `mapped_column(DateTime, ...)`
- 没有精度的类型（如 `Integer`）不写括号
- 可为 NULL 的字段类型写 `Optional`：`Mapped[Optional[str]]`，并加 `nullable=True`

**示例输出：**
```python
import datetime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean


class Base(DeclarativeBase):
    pass


class UserInfo(Base):
    __tablename__ = "user_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 用户ID
    username: Mapped[str] = mapped_column(String(64), default='')  # 用户名
    status: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否启用
    create_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)  # 创建时间
```

---

## Java — MyBatis-Plus + Lombok 模板

```java
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;

import java.time.LocalDateTime;
import java.math.BigDecimal;

/**
 * {类注释（来自表的 COMMENT，没有则用类名描述）}
 */
@Data
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
@TableName("{table_name}")
public class {ClassName} {
    // {注释}
    @TableId(type = IdType.AUTO)
    private {Type} {fieldName};  // 主键字段用 @TableId

    // {注释}
    @TableField("{column_name}")  // 字段名与属性名不一致时才加；snake_case → camelCase 一致时可省略
    private {Type} {fieldName};
}
```

**规则：**
- 属性名使用**小驼峰**（`camelCase`）：`user_name` → `userName`，`create_time` → `createTime`
- 主键字段（通常是 `id`）加 `@TableId(type = IdType.AUTO)`
- `@TableField` 在字段名与列名不一致时添加（MyBatis-Plus 默认支持驼峰映射，可省略）
- `BIGINT` → `Long`，`INT` → `Integer`
- `DATETIME` / `TIMESTAMP` → `LocalDateTime`，需 `import java.time.LocalDateTime`
- `DECIMAL` → `BigDecimal`，需 `import java.math.BigDecimal`
- 注释写在字段**上方**（`//` 风格，与示例保持一致）
- 不添加任何业务方法

**示例输出：**
```java
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;

import java.time.LocalDateTime;

/**
 * 用户信息
 */
@Data
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
@TableName("user_info")
public class UserInfo {
    // 用户ID
    @TableId(type = IdType.AUTO)
    private Long id;

    // 用户名
    private String username;

    // 是否启用
    private Boolean status;

    // 创建时间
    private LocalDateTime createTime;
}
```

---

## TypeScript — interface 模板

```typescript
/** {类注释} */
export interface {ClassName} {
  /** {注释} */
  {field_name}: {type}
}
```

**规则：**
- 属性名与 SQL 字段名**完全一致**（保留下划线，不做转换）；如果用户指定驼峰则转为 camelCase
- 日期类型（`DATE` / `DATETIME` / `TIMESTAMP`）统一映射为 `string`（ISO 8601 字符串，前端处理格式化）
- 可为 NULL 的字段类型写 `{type} | null`
- `NOT NULL` 且无默认值：类型保持非 nullable
- `ENUM('a','b','c')` 生成联合类型：`'a' | 'b' | 'c'`
- 不加任何方法、装饰器、`constructor`

**示例输出：**
```typescript
/** 用户信息 */
export interface UserInfo {
  /** 用户ID */
  id: number
  /** 用户名 */
  username: string
  /** 是否启用 */
  status: boolean
  /** 积分 */
  score: number
  /** 创建时间 */
  create_time: string | null
}
```

---

## TypeScript — class 模板

适用于需要实例化、赋默认值、或配合装饰器（如 `class-transformer`）使用的场景。

```typescript
/** {类注释} */
export class {ClassName} {
  /** {注释} */
  {field_name}: {type} = {default}
}
```

**默认值规则（TS class）：**
- `string` → `''`
- `number` → `0`
- `boolean` → `false`
- `string | null` / `Record<string, unknown>` → `null`
- SQL 中有 `DEFAULT xxx`：使用该值（字符串加引号，数字直接写，`'0'`/`'1'` 对应 bool 转为 `false`/`true`）

**示例输出：**
```typescript
/** 用户信息 */
export class UserInfo {
  /** 用户ID */
  id: number = 0

  /** 用户名 */
  username: string = ''

  /** 是否启用 */
  status: boolean = false

  /** 积分 */
  score: number = 0

}
```



| 情况 | 处理方式 |
|---|---|
| 联合主键 | Python 照常定义；Java 两个字段都加 `@TableId` 并注明；TS 加注释说明 |
| `AUTO_INCREMENT` | Java 用 `@TableId(type = IdType.AUTO)`；Python / TS 忽略 |
| `UNSIGNED` | 忽略，不影响类型映射 |
| `NOT NULL` 无 DEFAULT | 按"无 DEFAULT"规则处理 |
| `ENUM('a','b')` | Python → `str`；Java → `String`；TS → `'a' \| 'b'` 联合类型 |
| `JSON` 类型 | Python → `str`；Java → `String`；TS → `Record<string, unknown>` |
| 字段名是保留字（如 `type`、`order`） | 直接使用，不做转义 |
| 表名带数字（如 `user2_info`） | 驼峰：`User2Info` |

---

