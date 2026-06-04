---
name: cooper2hive-sync
description: DataDream 同步任务管理。创建和修改Cooper2Hive同步任务。
  触发：当用户说"创建Cooper同步任务"、"Cooper2Hive"、"修改Cooper同步任务"、“Cooper导入到Hive”时使用。
---

# Cooper2Hive 同步任务管理

## 前置检查

**强制**
    第一次调用skill时，先确认 DataDream MCP 服务已安装。未安装则立即结束，返回`DataDream MCP 服务未连接，请安装`。

## MCP Tools 工具映射

| 操作 | MCP 工具 |
|------|----------|
| 创建同步任务 | `create_sync_task` |
| 修改同步任务 | `update_sync_task` |
| 查询同步任务详情 | `get_sync_task` |
| 单次执行同步任务 | `run_sync_task` |
| 校验表名是否重复 | `check_table_name` |
| 预检查（权限/字段/规范） | `precheck_sync_task` |


---

## 能力边界

| 能力 | 支持 |
|------|------|
| 创建 Cooper2Hive 同步任务 | ✅ |
| 修改同步任务（基本信息/来源去向/字段映射/加密/告警等） | ✅ |
| 单次执行同步任务（手动触发一次，不能周期调度） | ✅ |
| 查询、删除、启用、停用、下线等管理操作 | ❌ 由 datadream-synctask-management 提供 |

## 创建同步任务

**触发**：「创建Cooper同步任务」「Cooper2Hive」「Cooper导入到Hive」

### 核心参数配置（必填或常用）

| 参数 | 说明 | 是否必填 | 默认值 |
|------|------|:-------:|------|
| taskName | 任务名 | 必填 | `cooper文件名_hive` |
| description | 任务描述 | 非必填 | 无 |
| owner | 任务负责人 | 必填 | 运行时自动获取当前用户 |
| linkType | 链路类型 | 必填 | `Cooper2Hive` |
| triggerType | 触发类型 | 必填 | 默认`手动调度`，可选周期调度/手动调度 |
| sourceDatasource | 来源数据源 | 必填 | 运行时自动获取当前cooper对应数据源，没有数据源时自动创建并关联 |
| cooper | 来源cooper | 必填 | 运行时自动获取当前cooper文件 |
| isMultiSheet | cooper是否多sheet | 非必填 | `单sheet` |
| sheetNames | sheet名 | 非必填 | 选择了多sheet时需要指定sheet |
| titleRow | 标题所在行 | 非必填 | 选择了多sheet时需要指定每一个sheet所在行，默认第一行为标题 |
| targetDatasource | 去向数据源 | 必填 | 运行时自动获取当前项目库 |
| autoCreateTable | 是否自动建表 | 必填 | `自动建表` |
| tableName | 去向表名 | 必填 | 自动建表时自动生成，格式为cooper2hive_mcp_table_{年/月/日/时}；已有表时用户指定 |
| lifecycle | 表生命周期 | 必填 | `30天`（自动建表时） |
| partitionField | 分区字段 | 必填 | 非自动建表时根据表分区情况自动填充（如 `${Y=0}-${M=0}-${D=-1}`） |
| fieldMappings | 字段映射 | 必填 | 定义映射关系 |
| schduleCode | 调度code | 非必填 | 系统自动生成 |
| scheduleType | 调度周期 | 必填 | 默认`天`，可选小时/天/周/月 |
| startTime | 最早执行时间 | 非必填 | 默认天→00:00，周→周一00:00，月→1号00:00 |
| baselineId | 关联基线 | 必填 | 默认项目下一级基线 |
| output_tags | 产出tags | 必填 | 系统默认生成一个 |
| retryCount | 失败重试次数 | 非必填 | `3次` |
| alertReceivers | 告警接收人 | 必填 | 运行时自动获取当前用户 |
| alertMethods | 告警方式 | 必填 | 默认`继承任务等级`，可选电话/短信/Dchat/邮件告警 |
| alertGroupType | 告警接收组类型 | 非必填 | 默认无，可选odin值班组/DChat群聊 |
| alertGroup | 告警组 | 非必填 | 一个具体的odin值班组/DChat群聊 |

> 不主动提供高级参数，当核心参数没有覆盖到时，查阅高级参数列表 [references/advanced-params.md](references/advanced-params.md)

### 流程

| 步骤 | 操作 | 输入 | 输出 | 异常处理 |
|------|------|------|------|----------|
| 1. 来源去向 | 获取cooper链接 + 去向Hive库 | cooper链接、是否自动建表、表名/生命周期 | 确认来源去向配置 | 无cooper → 引导提供；调用MCP校验表名，若重复 → 提示修改 |
| 2. 字段映射 | 自动生成字段映射关系 | 自动建表→自动生成；已有表→自动匹配 | 字段映射表 | 类型不匹配 → 标注问题字段 |
| 3. 调度配置 | 设置触发方式 + 基线 | triggerType、scheduleType、baselineId | 调度配置确认 | - |
| 4. 预检查+创建 | 系统校验权限/字段/规范 → 确认创建 | 用户确认 | 任务创建结果 | 预检查失败 → 返回问题项+修改建议 |
| 5. 立即执行 | 询问是否立即执行一次任务 | 用户确认 | 执行结果（批次ID） | - |

### 创建前确认模版

创建前返回以下全部信息确认：

```
📋 创建Cooper2hive同步任务确认

【来源】
• Cooper文件：{文件名} {链接}
• Sheet：单sheet/多sheet {sheet名，单sheet时省略}
• 文件标题所在行：{第一行}

【去向】
• 建表方式：{自动建表/已有表}
• 去向表名：{table_name}
• 生命周期：{30天}（仅自动建表时显示）

【字段映射】
| Cooper字段 | Hive字段 | 字段类型 |
|------------|----------|------|
| {字段1} | {字段1} | string |
| {字段2} | {字段2} | bigint |
| ... | ... | ... |

【调度】
• 触发方式：{周期调度/手动调度}
• 调度周期：{天} 00:00（仅周期调度时显示）
• 关联基线：{基线名称}

【告警】
• 接收人：{当前用户}
• 告警方式：{查询项目下一级基线后返回}

---
确认以上配置无误回复「确认」，需要修改请指出。
```

> 字段映射表超过10个字段时显示「...等N个字段」，不全部列出

### 约束

- 缺少必填项 → 追问，不继续下一步
- 非必填项 → 使用默认值，不追问
- 预检查失败 → 返回问题项，不创建
- **权限要求**：任务负责人必须拥有Cooper文档的下载权限
- **多sheet限制**：多sheet同步时，所有sheet的表头必须一致
- **表格规范**：标题行必须连续有值，不能有空单元格；表头中不能有公式

## 单次执行同步任务

**触发**：「执行一次Cooper同步任务」「手动跑一次」「立刻执行任务」

### 流程
1. 确认目标任务（任务名+任务ID）
2. 调用MCP工具触发单次执行
3. 返回执行结果（成功/失败 + 预计等待执行时间 + 任务批次名）

### 约束
- 执行失败时返回失败原因，不自动重试

## 修改同步任务

**触发**："修改Cooper同步任务"、"改字段映射"

### 修改项说明

| 可修改参数 | 不可修改参数 |
|-----------|-------------|
| **taskName** 任务名称 | **id** 任务ID，系统生成 |
| **description** 任务描述 | **linkType** 链路类型，固定为 Cooper2Hive |
| **owner** 任务负责人 | **projectId** 项目ID |
| **triggerType** 触发类型（周期/手动） | **datasourceId** 来源数据源ID |
| **partitionField** 分区字段（仅非自动建表） | **cooperId** Cooper文件ID |
| **fieldMappings** 字段映射（仅增加新字段，已生效的不可改） | **isMultiSheet** 多sheet标识 |
| **is_encrypt / encrypt_field** 加密开关/字段 | **sheetNames** sheet名称列表 |
| **is_hash / hash_field** Hash脱敏开关/字段 | **titleRow** 标题行位置 |
| **is_covered** 原字段置空 | **datasinkId** 去向数据源ID |
| **startTime** 最早执行时间 | **tableName** 去向表名 |
| **retryCount** 失败重试次数 | **lifecycle** 表生命周期 |
| **baselineId** 关联基线 | **scheduleCode** 调度code，系统生成 |
| **depend_tags** 依赖tags | **output_tags** 产出tags |
| **alertReceivers / alertMethods** 告警接收人/方式 | **scheduleType** 调度周期 |
| **alertGroupType / alertGroup** 告警组类型/组 | |
| **isQuietHours / quietHours** 免打扰开关/时段 | |
| **delayAlertTime** 延迟告警时间 | |
| **errorRowLimit** 错误记录数上限 | |
| **writeRowLimit** 写入行数告警下限 | |


### 流程
1. 查询当前信息
2. 收集修改内容
3. 校验修改项是否允许
4. 修改前向用户二次确认修改内容
5. 调用 MCP 工具更新
6. 返回修改结果并回显新值

### 约束

- **修改与删除要求**：未经明确授权可修改的参数均不可修改，未经明确授权可删除的参数均不可删除
- **字段映射变更**：Cooper表格增加字段后，需先在Hive表中新增对应字段，再修改同步任务的字段映射

## 约束与注意事项

- **MCP异常处理**：MCP调用失败时，返回原因和任务流程的进展情况

## 详细参考

> 不主动加载reference，当遇到咨询使用问题、功能介绍、功能口径等时查阅产品手册 →  [references/product-manuals.md](references/product-manuals.md)
