---
name: cooper2hive-sync
description: DataDream 同步任务管理。创建和修改Cooper2Hive同步任务。
  触发：当用户说"创建Cooper同步任务"、"Cooper2Hive"、"修改Cooper同步任务"时使用。
---

# Cooper2Hive 同步任务管理

## 前置检查

**强制**：第一次调用skill时，先确认 DataDream MCP 服务已安装。未安装则立即结束。

## MCP Tools 工具映射

| 操作 | MCP 工具 |
|------|----------|
| 创建同步任务 | `create_sync_task` |
| 修改同步任务 | `update_sync_task` |
| 查询同步任务详情 | `get_sync_task` |
| 校验表名是否重复 | `check_table_name` |
| 预检查（权限/字段/规范） | `precheck_sync_task` |


---

## 能力边界

| 能力 | 支持 |
|------|------|
| 创建 Cooper2Hive 同步任务 | ✅ |
| 修改同步任务（基本信息/来源去向/字段映射/加密/告警等） | ✅ |
| 查询、删除、启用、停用、下线等管理操作 | ❌ 由 datadream-synctask-management 提供 |

## 创建同步任务

**触发**："创建Cooper同步任务"、"Cooper2Hive"

### 参数配置
| 参数 | 说明 | 是否必填 | 默认值 |
|------|------|:-------:|------|
| taskName | 任务名 | 必填 | `cooper文件名_hive` |
| description | 任务描述 | 非必填 | 无 |
| owner | 任务负责人 | 必填 | `当前用户` |
| linkType | 链路类型 | 必填 | `Cooper2Hive` |
| triggerType | 触发类型 | 必填 | 默认`周期调度`，可选周期调度/手动调度 |
| sourceDatasource | 来源数据源 | 必填 | 默认当前cooper对应数据源，没有数据源时自动创建并关联 |
| cooper | 来源cooper | 必填 | `当前cooper文件` |
| isMultiSheet | cooper是否多sheet | 非必填 | `单sheet` |
| sheetNames | sheet名 | 非必填 | 选择了多sheet时需要指定sheet |
| titleRow | 标题所在行 | 非必填 | 选择了多sheet时需要指定每一个sheet所在行，默认第一行为标题 |
| targetDatasource | 去向数据源 | 必填 | `当前项目库` |
| autoCreateTable | 是否自动建表 | 必填 | `自动建表` |
| tableName | 去向表名 | 必填 | 自动建表时自动生成；已有表时用户指定 |
| lifecycle | 表生命周期 | 必填 | `30天`（自动建表时） |
| partitionField | 分区字段 | 必填 | 非自动建表时根据表分区情况自动填充（如 `${Y=0}-${M=0}-${D=-1}`） |
| fieldMappings | 字段映射 | 必填 | 定义映射关系 |
| is_encrypt | 敏感字段加密 | 非必填 | `关` |
| encrypt_field | 脱敏字段 | 非必填 | 需要敏感字段加密时指定 |
| is_hash | Hash脱敏 | 非必填 | `关` |
| hash_field | 脱敏字段 | 非必填 | 需要hash脱敏时指定 |
| is_covered | 是否原字段置空 | 非必填 | 默认关，选择了加密或者脱敏字段时指定将原字段置为空 |
| schduleCode | 调度code | 非必填 | 系统自动生成 |
| scheduleType | 调度周期 | 必填 | 默认`天`，可选小时/天/周/月 |
| startTime | 最早执行时间 | 非必填 | 默认天→00:00，周→周一00:00，月→1号00:00 |
| baselineId | 关联基线 | 必填 | 默认项目下一级基线 |
| depend_tags | 依赖tags | 非必填 | 无 |
| output_tags | 产出tags | 必填 | 系统默认生成一个 |
| retryCount | 失败重试次数 | 非必填 | `3次` |
| alertReceivers | 告警接收人 | 必填 | `当前用户` |
| alertMethods | 告警方式 | 必填 | 默认`继承任务等级`，可选电话/短信/Dchat/邮件告警 |
| alertGroupType | 告警接收组类型 | 非必填 | 默认无，可选odin值班组/DChat群聊 |
| alertGroup | 告警组 | 非必填 | 一个具体的odin值班组/DChat群聊 |
| isQuietHours | 是否免打扰 | 非必填 | `关` |
| quietHours | 免打扰时间段 | 非必填 | 设置免打扰时段（如 22:00-08:00） |
| delayAlertTime | 延迟告警时间 | 非必填 | 无 |
| errorRowLimit | 错误记录数上限 | 非必填 | `0条` |
| writeRowLimit | 写入数据行数告警下限 | 非必填 | `0条` |


### 创建流程（6步）

1. **收集来源与去向** 
    cooper文件 → 无则引导先提供
    去向Hive数据源（默认当前项目库）→ 确认是否自动建表 → 设置表名/生命周期/分区
    前置校验：调用MCP工具校验自动建表去向表名不能重复
2. **配置字段映射** 
    自动建表时自动生成去向字段名和类型
    非自动建表时自动映射关系 
3. **配置调度** 
    选择触发方式 → 周期调度时设周期和最早执行时间 → 关联业务基线
4. **创建前确认** 
    缺少必填项时不能创建 → 追问，非必填项用默认值
    创建前所有必填项全部返回做确认，非必填项仅当过程中提到时做返回确认
5. **预检查 + 确认创建** 
    系统预检查（下载权限、字段解析、表格规范） → 通过 → 用户确认是否提交 → 返回结果
    预检查不通过 → 返回不通过的检查项和修改意见
6. **是否立刻执行** 任务创建成功询问用户是否立即执行（单次执行，非周期）

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
4. 修改前向用户确认修改内容
5. 调用 MCP 工具更新
6. 返回修改结果并回显新值


## 约束与注意事项

- **来源去向不可变**：创建后不可修改
- **多sheet限制**：多sheet同步时，所有sheet的表头必须一致
- **表格规范**：标题行必须连续有值，不能有空单元格；表头中不能有公式
- **字段映射变更**：Cooper表格增加字段后，需先在Hive表中新增对应字段，再修改同步任务的字段映射
- **权限要求**：任务负责人必须拥有Cooper文档的下载权限
- **修改与删除要求**：未明确授权可修改的参数均不可修改，未明确授权可删除的参数均不可删除

### 详细参考

> 具体产品使用细节可查阅产品手册 →  [references/product-manuals.md](references/product-manuals.md)
