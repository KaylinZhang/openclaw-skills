---
name: cooper2hive-sync
description: DataDream 平台 Cooper2Hive 同步任务的创建和修改。将 Cooper 协作表格数据同步到 Hive 表。当用户提到"创建Cooper同步任务"、"Cooper2Hive"、"Cooper表格同步到Hive"时触发此skill。
triggers:
  - 创建Cooper同步任务
  - Cooper2Hive
  - Cooper表格同步
  - Cooper同步任务
  - 修改Cooper同步任务
---

# Cooper2Hive 同步任务 Skill

创建和修改 DataDream 平台上的 Cooper2Hive 同步任务，将 Cooper 协作表格数据同步到 Hive 表。

## 前置检查

**强制前置检查**：先检查是否已安装 DataDream 相关的 MCP 服务（提供同步任务管理工具的 MCP 服务）。
- 若未安装，**立即结束流程**，不继续执行任何业务步骤。

## 核心概念

- **Cooper2Hive**：将 Cooper 协作表格中的数据同步到 Hive 表。
- **Cooper数据源**：已注册的 Cooper 类型数据源，绑定了一个团队空间和 Token。如果用户项目下没有可用的 Cooper 数据源，需先引导用户创建 Cooper 数据源。

## 当前版本能力边界

### 支持的能力
- 创建 Cooper2Hive 同步任务
- 修改 Cooper2Hive 同步任务（字段映射、告警配置、加密脱敏、负责人等）

### 不支持的能力
- 删除、上下线、启停、重跑等管理操作（由 datadream-synctask-management skill 提供）
- 自动适配 Cooper 表格结构变化（官方限制，需手动修改字段映射）

## 同步任务模型

```
Cooper2Hive 同步任务
├── 基本信息
│   ├── id: 任务唯一标识（系统生成）
│   ├── name: 任务名称（选填，不填时自动生成）
│   ├── description: 任务描述（选填，不填时自动生成）
│   ├── owner: 任务负责人（默认创建人）
│   ├── linkType: 链路类型（默认 "Cooper2Hive"）
│   └── projectId: 所属项目ID（默认当前项目）
│
├── 来源配置
│   ├── datasourceId: 来源Cooper数据源（必填）
│   ├── docId: Cooper文档ID（必填，从URL中sheet后的数字串获取）
│   ├── isMultiSheet: 是否多sheet（默认单sheet）
│   ├── sheetNames: 工作表名称列表（多sheet时必填，多sheet表头必须一致）
│   └── titleRow: 标题所在行（默认第一行，每个sheet都需指定）
│
├── 去向配置
│   ├── datasourceId: 去向Hive数据源（默认当前项目库）
│   ├── autoCreateTable: 是否自动建表（必填）
│   ├── tableName: 目标表名（自动建表时必填；已有表时从列表选择）
│   ├── lifecycle: 表生命周期（自动建表时默认30天）
│   └── partition: 写入分区（非自动建表时必填，如 ${Y=0}-${M=0}-${D=-1}）
│
├── 字段映射
│   ├── mappings: 映射关系列表
│   │   └── { sourceField, targetField, dataType }
│   └── 自动建表：需定义去向字段名和数据类型
│       非自动建表：需指定来源字段与去向字段的映射关系
│
├── 调度配置
│   ├── triggerType: 手动触发 / 周期调度（必填）
│   ├── scheduleType: 周期类型（天/周/月/小时，周期调度时必填）
│   ├── startTime: 最早执行时间（默认：天→00:00，周→周一00:00，月→1号00:00）
│   ├── retryCount: 失败重试次数（默认3次）
│   └── baselineId: 关联业务基线（必填）
│
├── 性能配置
│   └── throttleLimit: 限流值（默认10M/s）
│
├── 告警配置
│   ├── errorRecordLimit: 错误记录数超上限告警（默认0条）
│   ├── writeRowLimit: 写入行数超下限告警（默认0条）
│   ├── alertReceivers: 告警接收人（默认任务负责人，可选值班表/项目成员）
│   ├── alertMethods: 告警方式（默认继承任务等级，可选：电话/短信/DChat/邮件）
│   ├── alertGroup: 告警组（可选：odin值班组/DChat群聊，默认无）
│   ├── quietHours: 告警免打扰时段（默认无，即全天通知）
│   └── phoneQuietHours: 电话免打扰时间范围（默认无）
│
├── 加密脱敏配置
│   └── rules: 字段级脱敏规则列表（默认无配置）
│       └── { field, type: 加密/hash脱敏, clearOriginal: 是否置空原字段 }
│
└── 状态
    └── status: 草稿/已提交（预检查通过后）
```

## 操作参考

### 1. 创建同步任务

**触发意图**：用户说"创建Cooper同步任务"、"把Cooper表格同步到Hive"等

**必填参数**：

| 参数 | 说明 |
|------|------|
| sourceDatasource | 来源Cooper数据源（如无可用数据源，先引导创建） |
| docId | Cooper文档ID（从URL中sheet后的数字串获取） |
| autoCreateTable | 是否自动建表 |
| tableName | 目标表名（自动建表时必填；已有表时从列表选择） |
| partition | 写入分区（非自动建表时必填，如 ${Y=0}-${M=0}-${D=-1}） |
| triggerType | 手动触发 / 周期调度 |
| scheduleType | 周期类型（周期调度时必填） |
| baselineId | 关联业务基线 |

**默认参数**：

| 参数 | 默认值 |
|------|--------|
| name | 自动生成 |
| description | 自动生成 |
| owner | 创建人 |
| linkType | Cooper2Hive |
| targetDatasource | 当前项目库 |
| lifecycle | 30天（自动建表时） |
| isMultiSheet | 单sheet |
| titleRow | 第一行 |
| fieldMappings | 自动建表需定义去向字段名和类型；非自动建表需指定映射关系 |
| startTime | 天→00:00，周→周一00:00，月→1号00:00 |
| retryCount | 3次 |
| throttleLimit | 10M/s |
| errorRecordLimit | 0条 |
| alertReceivers | 任务负责人 |
| alertMethods | 继承任务等级 |
| alertGroup | 无 |
| quietHours | 无 |
| phoneQuietHours | 无 |
| encryptRules | 无 |

**创建流程**：

1. **检查 Cooper 数据源**
   - 查询当前项目下是否有可用的 Cooper 数据源
   - 如无可用数据源，引导用户先创建 Cooper 数据源（调用 datadream-datasource skill）

2. **收集来源信息**
   - 选择来源 Cooper 数据源
   - 获取 Cooper 文档 ID：
     - 如果用户已提供，直接使用
     - 如果未提供，引导用户从 Cooper 文档 URL 中获取（sheet 后的数字串）
   - 确认是否多 sheet：
     - 默认单 sheet
     - 如需多 sheet，多个 sheet 的表头必须一致
   - 指定标题所在行（默认第一行）

3. **收集去向信息**
   - 选择去向 Hive 数据源（默认当前项目库）
   - 确认是否自动建表
     - 自动建表：输入目标表名，设置生命周期（默认30天）
     - 已有表：从当前 Hive 数据源下选择目标表，并指定写入分区（如 ${Y=0}-${M=0}-${D=-1}）

4. **配置字段映射**
   - 自动建表：需定义去向字段名和数据类型
   - 非自动建表：需指定来源字段与去向字段的映射关系
   - 注意：Cooper 表格标题行必须连续有值，不能有空单元格

5. **配置调度**
   - 选择触发方式：手动触发 / 周期调度
   - 周期调度时：选择周期类型（天/周/月/小时）
   - 设置最早执行时间
   - 关联业务基线

6. **配置告警**（使用默认值，用户可修改）

7. **配置加密脱敏**（默认无配置，可选配置字段级脱敏规则）

8. **预检查**
   - 检查 Cooper 文档下载权限（任务负责人需有下载权限）
   - 检查字段解析是否成功
   - 检查表格规范（标题行连续有值、无缺列空列）

9. **确认创建**
   - 向用户展示完整配置信息
   - 用户确认后提交创建
   - 返回创建结果

**参考文档**：见 references/cooper-sync-task.md

### 2. 修改同步任务

**触发意图**：用户说"修改Cooper同步任务"、"改一下字段映射"等

**可修改字段**：
- 任务名称、描述
- 任务负责人
- 字段映射（可增加映射，已存在的映射不支持修改）
- 加密脱敏配置
- 告警配置

**不可修改字段**：
- 来源去向信息
- 任务类型、链路类型

**流程**：

1. 查询任务当前信息
2. 收集用户要修改的内容
3. 校验修改项是否允许
4. 向用户确认修改内容
5. 调用 MCP 工具更新
6. 返回修改结果

## 约束与注意事项

- **项目归属**：所有同步任务操作默认在当前项目下进行
- **来源去向不可变**：同步任务的来源数据源、文档ID、去向表一旦创建不可修改
- **权限要求**：任务负责人必须拥有 Cooper 文档的下载权限
- **多sheet约束**：多 sheet 同步时，所有 sheet 的表头必须一致
- **表格规范**：
  - 标题行必须连续有值，不能有空单元格
  - 相邻列名之间不允许存在缺列或空列
  - 表头中不能有公式
- **字段变更**：Cooper 表格新增字段后，需先在 Hive 表中新增对应字段，再修改同步任务的字段映射
- **非自动建表分区**：非自动建表时必须指定写入分区，如 ${Y=0}-${M=0}-${D=-1}，假设调度时间为今日，将同步 Hive 库表分区为 {"dt":"2026-05-28"} 的所有数据
- **字段类型支持**：
  - 整形（INT, SMALL INT 等）
  - 浮点型（DOUBLE、FLOAT 等）
  - 字符串型（CHAR、STRING 等）
  - 日期类型（DATE 格式：yyyy-MM-dd，TIMESTAMP 格式：yyyy-MM-dd HH:mm:ss）
- **预检查**：创建时系统会发起预检查，检查常见错误原因
