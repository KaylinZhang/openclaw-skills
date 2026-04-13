---
name: data-sync
description: 数据同步专家。用于创建和管理离线数据同步任务。
支持的数据源方向：
  - 数据源同步到目标：MySQL-binlog / MySQL-快照 / Kafka / MQ / PublicLog / SR / ClickHouse → 目标存储
  - 数据源回写到源：目标存储 → MySQL
触发场景：创建同步任务、管理同步任务、同步任务报错处理、数据源配置。
---

# Data Sync Skill

## 工作流程

当用户要求创建同步任务时，按以下步骤执行：

```
Step 1: 确认数据源
   ↓ 调用 datasource/list.py 获取可用数据源
   ↓ 如果数据源不存在 → 提示注册或询问其他方案

Step 2: 确认源端信息
   ↓ 根据源类型调用对应的连接器脚本获取表结构
   ↓ connectors/mysql_query.py      → MySQL 表结构
   ↓ connectors/kafka_consume.py   → Kafka Topic 信息
   ↓ connectors/mq_consume.py      → MQ Topic 信息
   ↓ connectors/publiclog_query.py → PublicLog Logstore 信息
   ↓ connectors/sr_query.py        → SR 流数据信息
   ↓ connectors/ck_query.py         → ClickHouse 表结构

Step 3: 确认目标端信息
   ↓ connectors/hive_query.py --schema  → Hive 表结构（如存在）
   ↓ connectors/hive_write.py --check   → Hive 目标表检查

Step 4: 确认同步配置（必填项）
   ↓ 询问用户：同步模式、执行方式、基线绑定、分区写入规则等

Step 5: 确认默认项
   ↓ 展示所有默认配置项
   ↓ 用户确认或修改

Step 6: 生成同步配置
   ↓ generators/sync_code.py   → 生成同步代码
   ↓ generators/schedule.py    → 生成调度配置
   ↓ generators/alert.py        → 生成告警配置

Step 7: 汇总确认
   ↓ 必填项：数据源、目标表、同步模式、分区规则、调度配置、基线绑定
   ↓ 默认项：任务备注、负责人、表生命周期、告警配置
   ↓ 用户确认后，完成创建
```

---

## 支持的数据源方向

### 数据源同步到目标（Source → Target）

| 源端类型 | 说明 | 调用脚本 | 获取信息 |
|----------|------|----------|----------|
| **MySQL-binlog** | 增量同步，读取 binlog | mysql_query.py | 表结构、增量字段 |
| **MySQL-快照** | 全量同步，快照读取 | mysql_query.py | 表结构、全量数据 |
| **Kafka** | 消费 Kafka 消息 | kafka_consume.py | Topic 列表、Schema、消息格式 |
| **MQ** | 消费 ddMQ 消息 | mq_consume.py | Topic 列表、Schema、消息格式 |
| **PublicLog** | 读取日志数据 | publiclog_query.py | Logstore 列表、字段定义 |
| **SR** | 读取流数据 | sr_query.py | 流数据列表、Schema |
| **ClickHouse** | 读取 ClickHouse | ck_query.py | 表结构、引擎类型 |

### 数据源回写（Target → MySQL）

| 目标端类型 | 说明 | 调用脚本 |
|------------|------|----------|
| **Hive** | 数据写入 | hive_write.py |
| **MySQL** | 数据回写 | mysql_write.py |

### 内置数据源（无需注册）

| 类型 | 说明 | 使用方式 |
|------|------|----------|
| **ddMQ** | 公司内部 MQ | 默认数据源，直接使用 |
| **Hive** | Hive 数据源 | 默认使用当前项目库 |

---

## 同步模式

| 模式 | 说明 | 适用场景 | 生成代码 |
|------|------|---------|---------|
| **全量覆盖** | 每次整表拉取，覆盖写入 | 维度表、配置表 | INSERT OVERWRITE |
| **增量追加** | 基于时间戳/主键，只拉新增 | Fact 表、行为数据 | INSERT INTO + WHERE |

---

## 分区写入规则（必填项）

对于支持分区的目标存储（如 Hive），必须明确分区写入规则。

### 必填项：分区字段 + 分区值

| 配置项 | 说明 | 示例 |
|--------|------|------|
| **分区字段** | 目标表的分区字段名称 | dt、partition_date、biz_date |
| **分区值** | 数据写入的分区值 | `${bizdate}`（业务日期变量）、`${today}` |

### 分区值规则

| 变量 | 说明 | 示例值 |
|------|------|--------|
| `${bizdate}` | 业务日期（调度日期） | 2026-04-13 |
| `${today}` | 实际执行日期 | 2026-04-13 |
| `${yesterday}` | 昨天日期 | 2026-04-12 |

### 示例

目标表 `ods_order` 使用 `dt` 分区：
- 分区字段：`dt`
- 分区值：`${bizdate}`（表示写入当天业务日期的分区）

生成的同步代码：
```sql
INSERT INTO TABLE ods_order PARTITION (dt='${bizdate}')
SELECT * FROM order WHERE update_time >= '${bizdate}';
```

---

## 确认默认项（Step 5）

在用户确认必填项后，AI 需要展示所有默认配置项，由用户确认或修改。

### 默认项清单

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 任务备注 | 自动生成（来源→目标） | 任务描述 |
| 负责人 | 创建人 | 任务负责人 |
| 目标表名 | 自动按规则生成 | 如 `ods_order` |
| 同步字段 | 全部字段 | 同步哪些列 |
| 表生命周期 | 30天 | 数据保留天数 |
| 告警接收人 | DC + 电话给负责人 | 通知对象 |
| 告警渠道 | DC + 电话 | 通知渠道组合 |
| 告警免打扰时段 | 无（默认全天通知） | 电话免打扰时间 |

### 确认话术

```
【默认项确认】

以下配置使用默认值，请问需要修改吗？

| 配置项 | 默认值 | 修改？ |
|--------|--------|--------|
| 任务备注 | 同步 order 表到 Hive | [确认/修改] |
| 负责人 | 坤坤 | [确认/修改] |
| 表生命周期 | 30天 | [确认/修改] |
| 告警接收人 | DC + 电话给 坤坤 | [确认/修改] |
| 告警渠道 | DC + 电话 | [确认/修改] |

如无需修改，请回复"确认"或"好的"；
如需修改，请告诉我需要修改哪些项。
```

---

## 数据源配置规范

### MySQL 数据源（需注册）

| 字段 | 说明 | 必填 |
|------|------|------|
| 数据源名称 | 唯一标识名称 | ✅ |
| 维护方式 | DBA维护 / 自有 | ✅ |
| 账号用途 | 读 / 写 | ✅ |
| RDS服务名 | RDS 实例地址 | ✅ |
| 数据库名 | database 名称 | ✅ |
| 账号名 | 格式：账号名(机房IP:Port) | ✅ |
| 连接密码 | 仅写账号需要 | ⚠️ |

### Kafka 数据源（需注册）

| 字段 | 说明 | 必填 |
|------|------|------|
| 数据源名称 | 唯一标识名称 | ✅ |
| Kafka集群 | Kafka 集群标识 | ✅ |
| App ID | 应用 ID | ✅ |
| App Secret | 应用密钥 | ✅ |

### PublicLog 数据源（需注册）

| 字段 | 说明 | 必填 |
|------|------|------|
| 数据源名称 | 唯一标识名称 | ✅ |
| Public Key | 公钥标识 | ✅ |

### SR / ClickHouse 数据源（需注册）

| 字段 | 说明 | 必填 |
|------|------|------|
| 数据源名称 | 唯一标识名称 | ✅ |
| 集群标识 | 集群地址 | ✅ |

---

## 可用工具（Scripts）

### 数据源管理

| 脚本 | 用途 |
|------|------|
| `scripts/datasource/list.py` | 列出所有可用数据源 |

### 数据源同步连接器（Source → Target）

| 脚本 | 用途 | 调用示例 |
|------|------|----------|
| `scripts/connectors/mysql_query.py` | MySQL 表结构/数据查询 | `--ds xxx --table xxx --mode schema` |
| `scripts/connectors/kafka_consume.py` | Kafka Topic 信息查询 | `--ds xxx --topic xxx --mode list/schema` |
| `scripts/connectors/mq_consume.py` | MQ Topic 信息查询 | `--ds xxx --topic xxx --mode list/schema` |
| `scripts/connectors/publiclog_query.py` | PublicLog 查询 | `--ds xxx --logstore xxx --mode list/schema` |
| `scripts/connectors/sr_query.py` | SR 流数据查询 | `--ds xxx --stream xxx --mode list/schema` |
| `scripts/connectors/ck_query.py` | ClickHouse 查询 | `--ds xxx --database xxx --table xxx --mode schema` |

### 数据源回写连接器（Target → MySQL）

| 脚本 | 用途 | 调用示例 |
|------|------|----------|
| `scripts/connectors/hive_query.py` | Hive 表结构/数据查询 | `--ds xxx --table xxx --mode schema` |
| `scripts/connectors/hive_write.py` | Hive 写入检查/DDL生成 | `--ds xxx --table xxx --mode check/ddl` |
| `scripts/connectors/mysql_write.py` | MySQL 写入检查 | `--ds xxx --table xxx --mode check` |

### 配置生成器

| 脚本 | 用途 | 调用示例 |
|------|------|----------|
| `scripts/generators/sync_code.py` | 生成同步代码 | `--source-type xxx --target-type xxx --mode xxx` |
| `scripts/generators/schedule.py` | 生成调度配置 | `--frequency daily --time 01:00` |
| `scripts/generators/alert.py` | 生成告警配置 | `--task xxx --owner xxx` |

---

## 对话示例

### 示例 1: MySQL → Hive 同步

```
用户：帮我把订单表同步到 Hive

AI：好的，我来帮你创建同步任务。先确认一下数据源：
    - 你的 MySQL 数据源是哪个？（我看到有 ds_mysql_prod）
    - 密码是多少？
    - 表名是 order 吗？
    - Hive 用当前项目的库？

用户：MySQL 用 ds_mysql_prod，密码 xxx，表名是 order，Hive 用当前项目

AI：收到。确认必填项：
    - 来源：ds_mysql_prod / order 表
    - 目标：Hive / 当前项目库 / order_hive
    - 同步模式：？（全量覆盖/增量追加）
    - 执行方式：？（每天凌晨/手动执行）
    - 绑定基线：？
    - 分区字段：？（如 dt、partition_date）
    - 分区值：？（如 ${bizdate}）

用户：增量追加，每天凌晨 1 点，绑定基线 order_baseline，分区字段 dt，分区值 ${bizdate}

AI：收到！以下配置使用默认值，请问需要修改吗？

【默认项确认】
| 配置项 | 默认值 | 修改？ |
|--------|--------|--------|
| 任务备注 | 同步 order 表到 Hive | [确认/修改] |
| 负责人 | 坤坤 | [确认/修改] |
| 表生命周期 | 30天 | [确认/修改] |
| 告警接收人 | DC + 电话给 坤坤 | [确认/修改] |
| 告警渠道 | DC + 电话 | [确认/修改] |

用户：确认

AI：好的，生成同步任务：

    【同步代码】
    INSERT INTO TABLE ods_order PARTITION (dt='${bizdate}')
    SELECT * FROM order WHERE update_time >= '${bizdate}';

    【调度配置】
    Cron: 0 1 * * *

    【告警配置】
    失败通知：DC + 电话给 坤坤

    需要我现在创建吗？
```

### 示例 2: Kafka → Hive 同步

```
用户：帮我把 Kafka 的订单 Topic 同步到 Hive

AI：好的，我来确认一下 Kafka 数据源和 Topic 信息。
    - 你的 Kafka 数据源是哪个？
    - Topic 名称是？

用户：数据源是 ds_kafka_main，Topic 是 order_topic

AI：收到，让我查一下 Topic 信息：
    【order_topic Schema】
    - format: JSON
    - fields: order_id, user_id, amount, timestamp, event_type

    请确认必填项：
    - 目标表名：？（如 ods_order_topic）
    - 同步模式：？（全量覆盖/增量追加）
    - 分区字段：？（如 dt）
    - 分区值：？（如 ${bizdate}）

用户：表名叫 ods_order_topic，模式用增量追加，分区字段 dt，分区值 ${bizdate}

AI：收到！以下配置使用默认值，请问需要修改吗？

【默认项确认】
| 配置项 | 默认值 | 修改？ |
|--------|--------|--------|
| 任务备注 | 同步 order_topic 到 Hive | [确认/修改] |
| 表生命周期 | 30天 | [确认/修改] |
| 告警接收人 | DC + 电话给 坤坤 | [确认/修改] |

用户：确认

AI：好的，生成同步任务：
    【同步代码】
    INSERT INTO TABLE ods_order_topic PARTITION (dt='${bizdate}')
    SELECT * FROM kafka_order_topic
    WHERE dt = '${bizdate}';

    需要我现在创建吗？
```

### 示例 3: ClickHouse → Hive 同步

```
用户：帮我把 ClickHouse 的用户行为表同步到 Hive

AI：好的。先确认一下：
    - ClickHouse 数据源是哪个？
    - 数据库和表名是？

用户：数据源是 ds_ck_analytics，数据库是 analytics，表名是 user_events

AI：收到，让我查一下表结构：
    【user_events Schema】
    - engine: MergeTree
    - partition: dt
    - columns: id, user_id, event_type, properties, created_at, dt

    请确认必填项：
    - 目标表名：？
    - 同步模式：？（全量覆盖/增量追加）
    - 分区字段：？（如 dt）
    - 分区值：？（如 ${bizdate}）

用户：增量，按 dt 分区字段同步每天数据

AI：收到！以下配置使用默认值，请问需要修改吗？

【默认项确认】
| 配置项 | 默认值 | 修改？ |
|--------|--------|--------|
| 任务备注 | 同步 user_events 到 Hive | [确认/修改] |
| 表生命周期 | 30天 | [确认/修改] |

用户：确认
```

---

## References

详细的配置规范和数据源定义请参考：

- `references/sync_modes.md` - 同步模式详解（全量/增量）
- `references/datasource_config.md` - 数据源配置规范
- `references/alert_rules.md` - 告警规则说明
