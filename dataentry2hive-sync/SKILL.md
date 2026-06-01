---
name: dataentry-sync-task
description: DataDream 同步任务管理。创建和修改数据填报2Hive同步任务。
  触发：当用户说"创建同步任务"、"新建同步任务"、"修改同步任务"、"改字段映射"时使用。
---

# 同步任务管理

## 前置检查

**强制**：先确认 DataDream MCP 服务已安装。未安装则立即结束。

## 能力边界

| 能力 | 支持 |
|------|------|
| 创建同步任务（数据填报2Hive） | ✅ |
| 修改同步任务（字段映射/告警/加密脱敏等） | ✅ |
| 删除、启停、重跑等管理操作 | ❌ 由 datadream-task-management 提供 |
| 其他链路类型（MySQL2Hive等） | ❌ 待扩展 |

## 同步任务模型

```
SyncTask
├── 基本信息：id, name, description, owner, linkType, projectId
├── 来源配置：datasourceId, dataTableId, isMultiSheet, sheetName
├── 去向配置：datasourceId（默认当前项目库）, autoCreateTable, tableName, lifecycle
├── 字段映射：mappings [{ sourceField, targetField, dataType }]
├── 调度配置：triggerType, scheduleType, startTime, retryCount, baselineId
├── 告警配置：errorRecordLimit, writeRowLimit, alertReceivers, alertMethods...
├── 加密脱敏：rules [{ field, type, clearOriginal }]
└── 状态：草稿 / 已提交
```

## 创建同步任务

**触发**："创建同步任务"、"新建同步任务"、"建一个数据填报2hive任务"

### 必填参数

| 参数 | 说明 |
|------|------|
| sourceDatasource | 来源数据源（数易数据填报类型） |
| sourceDataTable | 来源数据填报表 |
| isMultiSheet | 是否多sheet |
| sheetName | 多sheet时必填 |
| autoCreateTable | 是否自动建表 |
| tableName | 自动建表时必填；已有表时从列表选择 |
| triggerType | 手动触发 / 周期调度 |
| scheduleType | 周期调度时必填（天/周/月/小时） |
| baselineId | 关联业务基线 |

### 默认参数

| 参数 | 默认值 |
|------|--------|
| targetDatasource | 当前项目库 |
| lifecycle | 30天 |
| fieldMappings | 全部字段，去向字段英文名与来源一致 |
| startTime | 天→00:00，周→周一00:00，月→1号00:00 |
| retryCount | 3次 |
| throttleLimit | 10M/s |
| errorRecordLimit | 0条 |
| writeRowLimit | 0条 |
| alertReceivers | 任务负责人 |
| alertMethods | 继承任务等级 |

### 创建流程（6步）

1. **收集来源** → 选择数易数据填报数据源 → 选择填报表 → 确认是否多sheet
2. **收集去向** → 确认去向Hive数据源（默认当前项目库）→ 确认是否自动建表 → 设置表名和生命周期
3. **配置字段映射** → 自动建表默认全部映射；已有表需手动指定
4. **配置调度** → 选择触发方式 → 周期调度时设周期和最早执行时间 → 关联业务基线
5. **配置告警**（使用默认值，可修改）→ 阈值、接收人、告警方式
6. **预检查 + 确认创建** → 系统预检查 → 展示配置 → 用户确认 → 提交 → 返回结果

**参考**：[数据填报2Hive使用手册](https://cooper.didichuxing.com/knowledge/share/book/YcSAIftpNcle/2204653102999)

## 修改同步任务

**触发**："修改同步任务"、"改字段映射"

| 可修改 | 不可修改 |
|--------|----------|
| 任务名称、描述 | 来源去向信息 |
| 字段映射（可增加） | 链路类型 |
| 告警配置 | |
| 调度配置（code/周期不可改） | |
| 加密脱敏 | |

流程：查询当前信息 → 收集修改内容 → 校验允许 → 确认 → 更新 → 返回结果。

## 约束与注意事项

- **来源去向不可变**：创建后不可修改
- **多sheet限制**：暂不支持多个sheet同时写入一张Hive表
- **空表限制**：来源填报表必须有数据
- **填报开启**：来源填报表必须在数易侧开启填报
- **字段映射变更**：填报表增加字段后需手动修改同步任务的字段映射

## 详细参考

- 告警配置详解 → [references/alert-config.md](references/alert-config.md)
- 加密脱敏规则 → [references/encrypt-rules.md](references/encrypt-rules.md)
- 调度配置说明 → [references/schedule-config.md](references/schedule-config.md)