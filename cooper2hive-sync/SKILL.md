---
name: cooper2hive-sync
description: DataDream 同步任务管理。创建和修改Cooper2Hive同步任务。
  触发：当用户说"创建Cooper同步任务"、"Cooper2Hive"、"修改Cooper同步任务"时使用。
---

# Cooper2Hive 同步任务管理

## 前置检查

**强制**：先确认 DataDream MCP 服务已安装。未安装则立即结束。

## 能力边界

| 能力 | 支持 |
|------|------|
| 创建 Cooper2Hive 同步任务 | ✅ |
| 修改同步任务（字段映射/告警/加密等） | ✅ |
| 删除、启停、重跑等管理操作 | ❌ 由 datadream-task-management 提供 |

## 同步任务模型

```
SyncTask
├── 基本信息：id, name, description, owner, linkType="Cooper2Hive", projectId
├── 来源配置：datasourceId, docId, isMultiSheet, sheetNames, titleRow
├── 去向配置：datasourceId（默认当前项目库）, autoCreateTable, tableName, lifecycle, partition
├── 字段映射：mappings [{ sourceField, targetField, dataType }]
├── 调度配置：triggerType, scheduleType, startTime, retryCount, baselineId
├── 告警配置：errorRecordLimit, writeRowLimit, alertReceivers, alertMethods...
├── 加密脱敏：rules [{ field, type, clearOriginal }]
└── 状态：草稿 / 已提交
```

## 创建同步任务

**触发**："创建Cooper同步任务"、"Cooper2Hive"

### 必填参数

| 参数 | 说明 |
|------|------|
| sourceDatasource | 来源Cooper数据源（如无则先引导创建） |
| docId | Cooper文档ID（从URL中sheet后的数字串获取） |
| autoCreateTable | 是否自动建表 |
| tableName | 自动建表时必填；已有表时从列表选择 |
| partition | 非自动建表时必填（如 `${Y=0}-${M=0}-${D=-1}`） |
| triggerType | 手动触发 / 周期调度 |
| scheduleType | 周期调度时必填（天/周/月/小时） |
| baselineId | 关联业务基线 |

### 默认参数

| 参数 | 默认值 |
|------|--------|
| targetDatasource | 当前项目库 |
| lifecycle | 30天（自动建表时） |
| isMultiSheet | 单sheet |
| titleRow | 第一行 |
| fieldMappings | 自动建表需定义去向字段名和类型；非自动建表需指定映射关系 |
| startTime | 天→00:00，周→周一00:00，月→1号00:00 |
| retryCount | 3次 |
| throttleLimit | 10M/s |
| errorRecordLimit | 0条 |
| writeRowLimit | 0条 |
| alertReceivers | 任务负责人 |
| alertMethods | 继承任务等级 |

### 创建流程（6步）

1. **检查Cooper数据源** → 无则引导先创建
2. **收集来源** → 选择Cooper数据源 → 获取docId → 确认是否多sheet → 指定标题行
3. **收集去向** → 确认去向Hive数据源（默认当前项目库）→ 确认是否自动建表 → 设置表名/生命周期/分区
4. **配置字段映射** → 自动建表需定义去向字段名和类型；非自动建表需指定映射关系
5. **配置调度** → 选择触发方式 → 周期调度时设周期和最早执行时间 → 关联业务基线
6. **预检查 + 确认创建** → 系统预检查（下载权限、字段解析、表格规范）→ 展示配置 → 用户确认 → 提交 → 返回结果

**参考**：[Cooper2Hive使用手册](https://cooper.didichuxing.com/knowledge/share/book/YcSAIftpNcle/2199600127171)

## 修改同步任务

**触发**："修改Cooper同步任务"、"改字段映射"

| 可修改 | 不可修改 |
|--------|----------|
| 任务名称、描述、负责人 | 来源去向信息 |
| 字段映射（可增加） | 链路类型 |
| 告警配置 | |
| 调度配置（周期不可改） | |
| 加密脱敏 | |

流程：查询当前信息 → 收集修改内容 → 校验允许 → 确认 → 更新 → 返回结果。

## 约束与注意事项

- **来源去向不可变**：创建后不可修改
- **多sheet限制**：多sheet同步时，所有sheet的表头必须一致
- **表格规范**：标题行必须连续有值，不能有空单元格；表头中不能有公式
- **字段映射变更**：Cooper表格增加字段后，需先在Hive表中新增对应字段，再修改同步任务的字段映射
- **权限要求**：任务负责人必须拥有Cooper文档的下载权限

## 详细参考

- Cooper使用手册 → [references/cooper-sync-guide.md](references/cooper-sync-guide.md)
- 告警配置详解 → [references/alert-config.md](references/alert-config.md)
- 加密脱敏规则 → [references/encrypt-rules.md](references/encrypt-rules.md)
- 调度配置说明 → [references/schedule-config.md](references/schedule-config.md)
