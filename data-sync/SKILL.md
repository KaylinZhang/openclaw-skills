---
name: data-sync
description: 数据同步专家。用于创建和管理离线数据同步任务。
支持的数据源方向：
  - 入湖：MySQL-binlog / MySQL-快照 / Kafka / MQ / PublicLog / SR / ClickHouse → Hive
  - 出湖：Hive → MySQL
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
   
Step 4: 确认同步配置
   ↓ 询问用户：同步模式、执行方式、基线绑定等
   
Step 5: 生成同步配置
   ↓ generators/sync_code.py   → 生成同步代码
   ↓ generators/schedule.py    → 生成调度配置
   ↓ generators/alert.py        → 生成告警配置
   
Step 6: 汇总确认
   ↓ 将配置汇总展示给用户
   ↓ 用户确认后，完成创建
```

---

## 支持的数据源方向

### 入湖（Source → Hive）

| 源端类型 | 说明 | 调用脚本 | 获取信息 |
|----------|------|----------|----------|
| **MySQL-binlog** | 增量同步，读取 binlog | mysql_query.py | 表结构、增量字段 |
| **MySQL-快照** | 全量同步，快照读取 | mysql_query.py | 表结构、全量数据 |
| **Kafka** | 消费 Kafka 消息 | kafka_consume.py | Topic 列表、Schema、消息格式 |
| **MQ** | 消费 ddMQ 消息 | mq_consume.py | Topic 列表、Schema、消息格式 |
| **PublicLog** | 读取日志数据 | publiclog_query.py | Logstore 列表、字段定义 |
| **SR** | 读取流数据 | sr_query.py | 流数据列表、Schema |
| **ClickHouse** | 读取 ClickHouse | ck_query.py | 表结构、引擎类型 |

### 出湖（Hive → Target）

| 目标端类型 | 说明 | 调用脚本 |
|------------|------|----------|
| **Hive** | 入湖写入 | hive_write.py |
| **MySQL** | 出湖回写 | mysql_write.py |

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
| **拉链表** | 保留历史状态 + 最新状态 | 缓慢变化维度 | SCD Type 2 |

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

### 入湖连接器（Source → Hive）

| 脚本 | 用途 | 调用示例 |
|------|------|----------|
| `scripts/connectors/mysql_query.py` | MySQL 表结构/数据查询 | `--ds xxx --table xxx --mode schema` |
| `scripts/connectors/kafka_consume.py` | Kafka Topic 信息查询 | `--ds xxx --topic xxx --mode list/schema` |
| `scripts/connectors/mq_consume.py` | MQ Topic 信息查询 | `--ds xxx --topic xxx --mode list/schema` |
| `scripts/connectors/publiclog_query.py` | PublicLog 查询 | `--ds xxx --logstore xxx --mode list/schema` |
| `scripts/connectors/sr_query.py` | SR 流数据查询 | `--ds xxx --stream xxx --mode list/schema` |
| `scripts/connectors/ck_query.py` | ClickHouse 查询 | `--ds xxx --database xxx --table xxx --mode schema` |

### 出湖连接器（Hive → Target）

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

AI：收到。确认同步配置：
    - 来源：ds_mysql_prod / order 表
    - 目标：Hive / 当前项目库 / order_hive
    - 同步模式：？（全量覆盖/增量追加/拉链表）
    - 执行方式：？（每天凌晨/手动执行）
    - 绑定基线：？

用户：增量追加，每天凌晨 1 点，绑定基线 order_baseline

AI：好的，生成同步任务：
    
    【同步代码】
    INSERT INTO TABLE order_hive PARTITION (dt='${bizdate}')
    SELECT * FROM order WHERE update_time >= '${bizdate}';
    
    【调度配置】
    Cron: 0 1 * * *
    
    【告警配置】
    失败通知：DC + 电话给 [你的名字]
    
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
    
    Hive 目标表你希望叫什么？同步模式用增量追加还是全量？

用户：表名叫 ods_order_topic，模式用增量追加

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
    
    同步模式用全量还是增量？

用户：增量，按 dt 分区字段同步每天数据
```

---

## References

详细的配置规范和数据源定义请参考：

- `references/sync_modes.md` - 同步模式详解（全量/增量/拉链）
- `references/datasource_config.md` - 数据源配置规范
- `references/alert_rules.md` - 告警规则说明
