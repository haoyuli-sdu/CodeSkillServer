---
name: "db-migration-generator"
description: "生成数据库迁移脚本"
---

# db-migration-generator

## 输入

- **数据库设计**: SDD 中的数据库设计文档

## 输出

数据库迁移脚本（Flyway/Liquibase/SQL）

## 数据库类型检查

生成脚本前必须检查数据库类型：

```bash
# 检查 pom.xml
grep -E "(mysql|postgresql|oracle)" pom.xml

# 检查 application.yml
cat src/main/resources/application.yml | grep -A 5 "datasource:"
```

**常见数据库类型**：
- MySQL
- PostgreSQL
- Oracle
- SQL Server

**人机协作**：如无法自动检测，询问用户数据库类型。

## 脚本类型选择

检查项目使用的迁移工具：

```bash
# 检查 Flyway
ls src/main/resources/db/migration/ 2>/dev/null

# 检查 Liquibase
ls src/main/resources/db/changelog/ 2>/dev/null

# 检查 pom.xml
grep -E "(flyway|liquibase)" pom.xml
```

**优先级**：
1. 如项目已有 Flyway/Liquibase，使用相同工具
2. 如项目无迁移工具，生成纯 SQL 脚本
3. 询问用户偏好

## Flyway 脚本生成

**命名规范**：
```
V{版本号}__{描述}.sql

示例：
V1.0.0__create_order_table.sql
V1.0.1__add_order_index.sql
V1.1.0__create_user_table.sql
```

**MySQL 脚本**：
```sql
-- V1.0.0__create_order_table.sql

-- 订单表
CREATE TABLE T_ORDER (
    ID BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    ORDER_NO VARCHAR(32) NOT NULL COMMENT '订单号',
    USER_ID BIGINT NOT NULL COMMENT '用户ID',
    TOTAL_AMOUNT DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '订单金额',
    STATUS TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0-待支付，1-已支付，2-已发货，3-已完成，4-已取消',
    DELETED TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    CREATE_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UPDATE_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CREATE_BY BIGINT COMMENT '创建人ID',
    UPDATE_BY BIGINT COMMENT '更新人ID',
    PRIMARY KEY (ID),
    UNIQUE KEY UK_ORDER_NO (ORDER_NO),
    KEY IDX_USER_ID (USER_ID),
    KEY IDX_USER_STATUS (USER_ID, STATUS),
    KEY IDX_CREATE_TIME (CREATE_TIME)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 订单商品表
CREATE TABLE T_ORDER_ITEM (
    ID BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    ORDER_ID BIGINT NOT NULL COMMENT '订单ID',
    PRODUCT_ID BIGINT NOT NULL COMMENT '商品ID',
    PRODUCT_NAME VARCHAR(200) NOT NULL COMMENT '商品名称',
    PRICE DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '单价',
    QUANTITY INT NOT NULL DEFAULT 0 COMMENT '数量',
    SUB_TOTAL DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '小计金额',
    DELETED TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除',
    CREATE_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UPDATE_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (ID),
    KEY IDX_ORDER_ID (ORDER_ID),
    KEY IDX_PRODUCT_ID (PRODUCT_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单商品表';
```

**PostgreSQL 脚本**：
```sql
-- V1.0.0__create_order_table.sql

-- 订单表
CREATE TABLE T_ORDER (
    ID BIGSERIAL PRIMARY KEY,
    ORDER_NO VARCHAR(32) NOT NULL,
    USER_ID BIGINT NOT NULL,
    TOTAL_AMOUNT DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    STATUS SMALLINT NOT NULL DEFAULT 0,
    DELETED SMALLINT NOT NULL DEFAULT 0,
    CREATE_TIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UPDATE_TIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CREATE_BY BIGINT,
    UPDATE_BY BIGINT
);

-- 注释
COMMENT ON TABLE T_ORDER IS '订单表';
COMMENT ON COLUMN T_ORDER.ID IS '主键';
COMMENT ON COLUMN T_ORDER.ORDER_NO IS '订单号';
-- ...

-- 索引
CREATE UNIQUE INDEX UK_ORDER_NO ON T_ORDER(ORDER_NO);
CREATE INDEX IDX_USER_ID ON T_ORDER(USER_ID);
CREATE INDEX IDX_USER_STATUS ON T_ORDER(USER_ID, STATUS);
CREATE INDEX IDX_CREATE_TIME ON T_ORDER(CREATE_TIME);

-- 触发器自动更新时间
CREATE OR REPLACE FUNCTION update_update_time_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.UPDATE_TIME = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_t_order_update_time 
    BEFORE UPDATE ON T_ORDER 
    FOR EACH ROW 
    EXECUTE FUNCTION update_update_time_column();
```

## Liquibase 脚本生成

**XML 格式**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.8.xsd">

    <changeSet id="1" author="developer">
        <createTable tableName="T_ORDER" remarks="订单表">
            <column name="ID" type="BIGINT" autoIncrement="true">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="ORDER_NO" type="VARCHAR(32)" remarks="订单号">
                <constraints nullable="false" unique="true"/>
            </column>
            <column name="USER_ID" type="BIGINT" remarks="用户ID">
                <constraints nullable="false"/>
            </column>
            <column name="TOTAL_AMOUNT" type="DECIMAL(10,2)" 
                    defaultValue="0.00" remarks="订单金额"/>
            <column name="STATUS" type="TINYINT" 
                    defaultValue="0" remarks="状态"/>
            <column name="DELETED" type="TINYINT" 
                    defaultValue="0" remarks="逻辑删除"/>
            <column name="CREATE_TIME" type="DATETIME" 
                    defaultValueComputed="CURRENT_TIMESTAMP" remarks="创建时间"/>
            <column name="UPDATE_TIME" type="DATETIME" 
                    defaultValueComputed="CURRENT_TIMESTAMP" remarks="更新时间"/>
            <column name="CREATE_BY" type="BIGINT" remarks="创建人ID"/>
            <column name="UPDATE_BY" type="BIGINT" remarks="更新人ID"/>
        </createTable>
        
        <createIndex indexName="IDX_USER_ID" tableName="T_ORDER">
            <column name="USER_ID"/>
        </createIndex>
        
        <createIndex indexName="IDX_USER_STATUS" tableName="T_ORDER">
            <column name="USER_ID"/>
            <column name="STATUS"/>
        </createIndex>
    </changeSet>

</databaseChangeLog>
```

**YAML 格式**：
```yaml
databaseChangeLog:
  - changeSet:
      id: 1
      author: developer
      changes:
        - createTable:
            tableName: T_ORDER
            remarks: 订单表
            columns:
              - column:
                  name: ID
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
                    nullable: false
              - column:
                  name: ORDER_NO
                  type: VARCHAR(32)
                  remarks: 订单号
                  constraints:
                    nullable: false
                    unique: true
              # ...
        - createIndex:
            indexName: IDX_USER_ID
            tableName: T_ORDER
            columns:
              - column:
                  name: USER_ID
```

## 纯 SQL 脚本生成

适用于无迁移工具的项目：

```sql
-- =============================================
-- 数据库：order_db
-- 版本：v1.0.0
-- 说明：订单模块初始建表脚本
-- =============================================

-- 订单表
CREATE TABLE T_ORDER (
    ID BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    ORDER_NO VARCHAR(32) NOT NULL COMMENT '订单号',
    USER_ID BIGINT NOT NULL COMMENT '用户ID',
    TOTAL_AMOUNT DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '订单金额',
    STATUS TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0-待支付，1-已支付，2-已发货，3-已完成，4-已取消',
    DELETED TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    CREATE_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UPDATE_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CREATE_BY BIGINT COMMENT '创建人ID',
    UPDATE_BY BIGINT COMMENT '更新人ID',
    PRIMARY KEY (ID),
    UNIQUE KEY UK_ORDER_NO (ORDER_NO),
    KEY IDX_USER_ID (USER_ID),
    KEY IDX_USER_STATUS (USER_ID, STATUS),
    KEY IDX_CREATE_TIME (CREATE_TIME)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 订单商品表
CREATE TABLE T_ORDER_ITEM (
    ID BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    ORDER_ID BIGINT NOT NULL COMMENT '订单ID',
    PRODUCT_ID BIGINT NOT NULL COMMENT '商品ID',
    PRODUCT_NAME VARCHAR(200) NOT NULL COMMENT '商品名称',
    PRICE DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '单价',
    QUANTITY INT NOT NULL DEFAULT 0 COMMENT '数量',
    SUB_TOTAL DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '小计金额',
    DELETED TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除',
    CREATE_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UPDATE_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (ID),
    KEY IDX_ORDER_ID (ORDER_ID),
    KEY IDX_PRODUCT_ID (PRODUCT_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单商品表';

-- 初始化数据（可选）
-- INSERT INTO T_ORDER (...) VALUES (...);
```

## 输出格式

**Flyway**：
```
src/main/resources/db/migration/
├── V1.0.0__create_order_table.sql
├── V1.0.1__create_user_table.sql
└── V1.0.2__add_order_index.sql
```

**Liquibase**：
```
src/main/resources/db/changelog/
├── db.changelog-master.xml
├── changes/
│   ├── db.changelog-1.0.0.xml
│   └── db.changelog-1.0.1.xml
```

**纯 SQL**：
```
db/
└── migration/
    ├── V1.0.0__init.sql
    └── README.md
```

## 注意事项

- 生成前检查数据库类型（MySQL/PostgreSQL/Oracle）
- 检查项目是否已有迁移工具（Flyway/Liquibase）
- 表名、字段名使用大写下划线
- 必须包含逻辑删除和审计字段
- 索引命名规范：IDX_/UK_ 前缀
- 金额使用 DECIMAL，禁止 FLOAT/DOUBLE
- 添加表和字段注释
- 脚本要可重复执行（幂等）
