---
name: "migrate"
description: "生成数据库迁移文件。当用户需要创建表、修改表结构、添加索引等数据库变更时使用此 skill。"
---

# Database Migration Skill

生成符合项目规范的 golang-migrate 迁移文件。

## 工作流程

1. 询问用户迁移需求（创建表/修改表/添加索引等）
2. 读取 `migrations/` 目录，确定下一个可用序号
3. 生成 up.sql 和 down.sql 文件对
4. 提示用户使用 `make migrate-up` 执行迁移

## 命名规范

```text
migrations/{yyyymmddhhiiss}{3位序号}_{snake_case描述}.up.sql
migrations/{yyyymmddhhiiss}{3位序号}_{snake_case描述}.down.sql
```

格式说明：
- `yyyymmddhhiiss` - 年月日时分秒（14位）
- `3位序号` - 同一秒内的序号（001-999）

示例：`20251229035300001_create_users_table.up.sql`

## SQL 规范

### 创建表 (up.sql)

```sql
CREATE TABLE IF NOT EXISTS `table_name` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(100) NOT NULL COMMENT '名称',
    `status` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用, 1-正常',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表注释';
```

### 删除表 (down.sql)

```sql
DROP TABLE IF EXISTS `table_name`;
```

### 添加字段 (up.sql)

```sql
ALTER TABLE `table_name` ADD COLUMN `field_name` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '字段说明' AFTER `existing_field`;
```

### 删除字段 (down.sql)

```sql
ALTER TABLE `table_name` DROP COLUMN `field_name`;
```

### 添加索引 (up.sql)

```sql
ALTER TABLE `table_name` ADD INDEX `idx_field` (`field_name`);
-- 或唯一索引
ALTER TABLE `table_name` ADD UNIQUE KEY `uk_field` (`field_name`);
```

### 删除索引 (down.sql)

```sql
ALTER TABLE `table_name` DROP INDEX `idx_field`;
```

## 字段类型规范

| 用途     | 类型                              | 示例                              |
| -------- | --------------------------------- | --------------------------------- |
| 主键     | `BIGINT UNSIGNED AUTO_INCREMENT`  | `id`                              |
| 外键     | `BIGINT UNSIGNED`                 | `user_id`                         |
| 短字符串 | `VARCHAR(n)`                      | `name VARCHAR(100)`               |
| 长文本   | `TEXT`                            | `content`                         |
| 枚举状态 | `TINYINT UNSIGNED`                | `status TINYINT UNSIGNED DEFAULT 1` |
| 金额     | `DECIMAL(10,2)`                   | `price`                           |
| 时间戳   | `TIMESTAMP`                       | `created_at`, `updated_at`        |
| 日期     | `DATE`                            | `birth_date`                      |
| 布尔     | `TINYINT(1)`                      | `is_active TINYINT(1) DEFAULT 1`  |
| JSON     | `JSON`                            | `metadata`                        |

## 索引命名规范

| 类型     | 前缀   | 示例             |
| -------- | ------ | ---------------- |
| 普通索引 | `idx_` | `idx_user_id`    |
| 唯一索引 | `uk_`  | `uk_email`       |
| 联合索引 | `idx_` | `idx_user_status`|

## 必要规则

1. 所有字段必须有 COMMENT
2. 表必须有表级 COMMENT
3. up.sql 使用 `IF NOT EXISTS` / `IF EXISTS`
4. down.sql 必须能完全回滚 up.sql 的更改
5. 使用 InnoDB 引擎
6. 使用 utf8mb4 字符集

## 执行迁移

```bash
# 执行所有迁移
make migrate-up

# 回滚上一个
make migrate-down

# 查看当前版本
make migrate-version
```
