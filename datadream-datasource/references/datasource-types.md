# 数据源类型扩展说明

## 当前已支持

### 数易数据填报（`datae_dataentry`）

- **用途**：作为同步任务来源
- **配置项**：shuyiProjectSpace（必填）
- **可修改字段**：仅名称
- **环境约束**：DataDream 和数易必须同环境

## 待扩展类型

### MySQL（`mysql`）

- **用途**：同步任务来源或去向
- **配置项**：host, port, database, username, password
- **状态**：待 MCP 支持后开放

### Kafka（`kafka`）

- **状态**：规划中

### Hive（`hive`）

- **用途**：同步任务去向（默认当前项目库）
- **状态**：已内置，无需单独创建