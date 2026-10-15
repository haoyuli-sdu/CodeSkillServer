---
name: "mcp-builder"
description: "为OpenClaw构建MCP服务器，连接外部工具和数据源。给定一个外部服务（Notion/飞书/数据库/搜索API），生成MCP服务器代码并配置到OpenClaw。触发：用户说\"构建MCP服务器\"、\"连接外部API\"、\"创建MCP\"。"
---

# MCP Builder

## 核心能力

为 OpenClaw 构建 MCP（Model Context Protocol）服务器，连接外部工具和数据源。

## 工作流程

### Step 1：确定需求
- 连接什么外部服务？
- 需要哪些 API？
- OpenClaw 如何与该服务交互？

### Step 2：MCP 协议设计
根据外部服务 API 设计 MCP 工具接口。

### Step 3：代码生成
生成 MCP 服务器代码（Node.js / Python）。

### Step 4：配置 OpenClaw
配置到 OpenClaw 的 mcp 配置中。

## MCP 配置示例

OpenClaw 配置文件中添加：

```json
{
  "mcpServers": {
    "my-service": {
      "command": "node",
      "args": ["./mcp-servers/my-service/index.js"]
    }
  }
}
```

## 常用 MCP 服务模板

### Notion
```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/client"]
    }
  }
}
```

### 飞书
```json
{
  "mcpServers": {
    "feishu": {
      "command": "python",
      "args": ["-m", "feishu_mcp"]
    }
  }
}
```

## 输出

- MCP 服务器代码 → `mcp-servers/<name>/`
- OpenClaw 配置更新
- 使用说明文档

## 脚本

- `scripts/mcp-builder.py` — MCP 服务器生成器
