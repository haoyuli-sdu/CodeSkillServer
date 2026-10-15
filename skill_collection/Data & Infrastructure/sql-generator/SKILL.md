---
name: "sql-generator"
description: "Lingman-Starter 框架 SQL 生成助手。当用户需要：(1) 生成建表 SQL（CREATE TABLE）(2) 生成改表 SQL（ALTER TABLE）(3) 生成统计查询 SQL (4) 生成 MyBatis Mapper XML 中的 SQL 片段 (5) 生成数据库迁移脚本 时触发此技能。不要在以下场景触发：生成 Java 代码类（由 crud-generator 处理）、纯文档查询（由 doc-qa 处理）。"
---

# SQL 生成指南

## 生成范围

本 Skill 负责生成数据库相关的 SQL 语句：

| SQL 类型 | 示例 |
|---------|------|
| DDL - 建表 | `CREATE TABLE t_xxx (...)` |
| DDL - 改表 | `ALTER TABLE t_xxx ADD COLUMN ...` |
| DML - 查询 | `SELECT ... FROM ... WHERE ...` |
| DML - 统计 | 聚合查询、分组统计 |
| Mapper XML | MyBatis 的 `<select>` / `<update>` 片段 |

## 建表规范

参见 [db-spec.md](../lingman-core/db-spec.md)。生成建表 SQL 时，优先遵循以下规则：

- 表名必须使用 `t_业务表名` 形式，例如 `t_course`；表名使用小写蛇形命名。
- 主键字段使用 `"id" int8 NOT NULL`，并保留主键约束：`CONSTRAINT "pk_t_业务表名" PRIMARY KEY ("id")`。
- 如需生成序列，序列名不要带 `t_` 前缀，例如表 `t_course` 对应 `course_seq`。
- 每个业务表都必须包含公共字段：`creator`、`create_time`、`updater`、`update_time`、`deleted`，字段定义必须与规范模板保持一致。
- 建表语句中不要添加任何普通索引、外键约束或业务唯一约束；索引可以作为“建议开发者确认后添加”的补充说明单独列出，只有开发者同意后才生成索引 SQL。
- 不要在 `CREATE TABLE` 中定义外键；关联字段只保留字段本身，例如 `college_id int8`。

## 生成步骤

1. 用户描述业务实体和字段需求
2. 生成符合规范的 PostgreSQL 建表 SQL（含必备公共字段和字段注释）
3. 如存在高频查询字段或关联字段，只给出索引建议，并明确说明“需开发者确认后再添加索引 SQL”
4. 如有需要，生成示例查询 SQL

## 参考文档

| 场景 | 参考文档 |
|------|----------|
| 建表规范、字段约定 | [db-spec.md](../lingman-core/db-spec.md) |
| 常见 SQL 示例 | [sql-examples.md](references/sql-examples.md) |
