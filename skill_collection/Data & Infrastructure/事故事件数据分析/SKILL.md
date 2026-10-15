---
name: "事故事件数据分析"
description: "用于动力电池工厂事故事件数据的智能查询与分析。当用户查询事故事件详情、统计趋势、指标分析时，自动生成SQL查询数据库，计算统计指标，并进行综合分析总结。"
---

# 事故事件数据分析技能

## 概述

本技能用于动力电池工厂事故事件数据的智能查询与分析，包含三个核心阶段：

1. **SQL生成与执行** - 根据用户自然语言问题生成SQL并查询数据库
2. **指标计算** - 分析需要的统计指标，生成Python代码计算并执行
3. **分析总结** - 对所有信息进行综合分析，输出用户友好的报告

## 使用流程

### 第一阶段：SQL生成与执行

使用 `scripts/nl2sql_enhanced.py` 完成以下步骤：

**输入项：**
1. **用户原始问题** - 用户的自然语言查询
2. **结构化Schema** - 自动从数据库提取表结构
3. **业务规则映射** - 从 `references/business_rules.md` 读取
4. **查询边界约束** - 从 `references/query_constraints.md` 读取
5. **Few-shot示例** - 从 `references/few_shot_examples.md` 读取

**执行步骤：**
1. 自动连接数据库并提取Schema信息
2. 结合业务规则和约束条件生成SQL
3. 执行SQL获取原始数据
4. 返回SQL语句、执行结果、结果Schema

### 第二阶段：指标计算

使用 `scripts/metrics_calculator_enhanced.py` 完成以下步骤：

**输入项：**
1. **SQL原始结果** - 第一阶段的查询结果
2. **结果Schema** - 字段含义说明
3. **指标定义清单** - 根据用户问题自动分析需要的指标
4. **计算上下文** - 业务背景信息
5. **执行约束** - 安全执行约束

**执行步骤：**
1. 分析用户问题，确定需要计算的统计指标
2. 生成Python计算代码
3. 安全执行代码获取指标结果
4. 返回指标值、计算公式、原始数据

### 第三阶段：分析总结

基于前两阶段结果生成最终报告：

**输入项：**
1. **用户原始问题** - 锚定回答方向
2. **SQL数据摘要** - 数据覆盖范围、样本量、异常说明
3. **Python计算结果** - 指标值、计算公式、推导过程
4. **数据可信度标记** - 控制措辞强度
5. **输出格式要求** - 结构化呈现

**输出格式：**
```markdown
## 查询摘要
[简要说明查询范围和数据量]

## 核心指标
| 指标名称 | 数值 | 单位 | 说明 |
|---------|------|------|------|
| XXX | YYY | 次 | ... |

## 数据分析
[详细分析，使用结构化表述]

## 关键发现
- **发现1**: [高亮重点结论]
- **发现2**: [高亮重点结论]

## 行动建议
1. [可执行的建议]
2. [可执行的建议]
```

## 脚本使用说明

### nl2sql_enhanced.py

```python
from scripts.nl2sql_enhanced import IncidentNL2SQL

with IncidentNL2SQL() as nl2sql:
    result = nl2sql.execute("最近30天各类型事故数量统计")
    print(result["sql"])
    print(result["data"])
```

### metrics_calculator_enhanced.py

```python
from scripts.metrics_calculator_enhanced import IncidentMetricsCalculator

with IncidentMetricsCalculator() as calc:
    metrics = [
        {"name": "事故总数", "field": "id", "method": "count"},
        {"name": "平均严重度", "field": "severity", "method": "mean"}
    ]
    result = calc.calculate("SELECT * FROM incidents WHERE ...", metrics)
    print(result["metrics"])
```

## 配置文件

所有配置通过环境变量读取：
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME - 数据库配置
- ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY - API配置
- MODEL_ID - 使用的模型ID

## 注意事项

1. **安全第一** - 生成的SQL会经过安全检查，禁止危险操作
2. **边界约束** - 默认查询时间范围不超过90天
3. **错误处理** - 数据库连接失败时给出清晰提示
4. **数据隐私** - 不输出敏感字段（如人员姓名等）
