# 同步模式详解

## 一、全量覆盖（Full Overwrite）

### 适用场景
- 维度表（数据量小，允许全量刷新）
- 历史数据不需要保留
- 数据量不大，可以接受全量拉取

### 实现方式
```sql
-- 每次执行前先清空当天分区，再写入新数据
INSERT OVERWRITE TABLE ods_order PARTITION (dt='${bizdate}')
SELECT id
     , order_id
     , user_id
     , amount
     , status
     , create_time
     , update_time
     , '${bizdate}' AS dt
FROM order_db.order;
```

### 优缺点
| 优点 | 缺点 |
|------|------|
| 实现简单 | 数据量大时耗时 |
| 数据一致性高 | 浪费资源 |
| 不需要水位标记 | 对源库有压力 |

---

## 二、增量追加（Incremental Append）

### 适用场景
- Fact 表（数据量大，只同步新增）
- 需要保留历史记录
- 源表有时间戳或自增 ID

### 实现方式

#### 方式一：基于时间戳
```sql
-- 只同步新增和变化的数据
INSERT INTO TABLE ods_order PARTITION (dt='${bizdate}')
SELECT id
     , order_id
     , user_id
     , amount
     , status
     , create_time
     , update_time
     , '${bizdate}' AS dt
FROM order_db.order
WHERE update_time >= '${bizdate}'
  AND update_time < '${next_date}';
```

#### 方式二：基于水位标记
```sql
-- 使用 DDS（DataDeltaSign）表记录增量水位
INSERT INTO TABLE ods_order PARTITION (dt='${bizdate}')
SELECT a.*
     , '${bizdate}' AS dt
FROM order_db.order a
JOIN (
    SELECT max_id AS start_id
         , '${bizdate}_max_id' AS end_id
    FROM dds_sync_status
    WHERE table_name = 'order'
) b ON a.id > b.start_id;
```

### 优缺点
| 优点 | 缺点 |
|------|------|
| 性能好 | 需要水位标记 |
| 对源库压力小 | 实现复杂 |
| 保留历史 | 需要去重处理 |

---

## 三、拉链表（SCD Type 2）

### 适用场景
- 需要保留数据历史变化
- 分析数据变化趋势
- 维度表变化较慢

### 实现方式

```sql
-- 拉链表表结构
-- start_date: 记录生效开始日期
-- end_date: 记录失效日期（9999-12-31 表示当前有效）
CREATE TABLE ods_user_scd (
    user_id    BIGINT,
    user_name  STRING,
    city       STRING,
    start_date STRING,
    end_date   STRING
) PARTITIONED BY (dt STRING);

-- Step 1: 保留未变化的记录
INSERT INTO TABLE ods_user_scd PARTITION (dt='${bizdate}')
SELECT a.user_id
     , a.user_name
     , a.city
     , a.start_date
     , CASE WHEN b.user_id IS NOT NULL THEN '${yesterday}' 
            ELSE a.end_date END AS end_date
FROM ods_user_scd a
LEFT JOIN (
    SELECT * FROM ods_user WHERE dt = '${bizdate}'
) b ON a.user_id = b.user_id
WHERE a.end_date = '9999-12-31'
  AND a.dt = '${max_date}';

-- Step 2: 新增和变化的记录
INSERT INTO TABLE ods_user_scd PARTITION (dt='${bizdate}')
SELECT user_id
     , user_name
     , city
     , '${bizdate}' AS start_date
     , '9999-12-31' AS end_date
FROM ods_user
WHERE dt = '${bizdate}';
```

### 拉链表查询

```sql
-- 查询某一天的用户信息
SELECT * FROM ods_user_scd
WHERE '${target_date}' BETWEEN start_date AND end_date;

-- 查询历史变化
SELECT * FROM ods_user_scd
WHERE user_id = 12345
  AND dt <= '${target_date}'
ORDER BY start_date;
```

### 优缺点
| 优点 | 缺点 |
|------|------|
| 保留历史 | 存储膨胀 |
| 分析变化趋势 | 查询复杂 |
| 数据可追溯 | 实现成本高 |

---

## 四、同步模式选择指南

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| 维度表（地区、城市等） | 全量覆盖 | 数据量小，全量简单 |
| 配置表、字典表 | 全量覆盖 | 数据变化少 |
| 订单、交易等事实表 | 增量追加 | 数据量大，只需新增 |
| 用户、产品等缓慢变化维度 | 拉链表 | 需要保留历史变化 |
| 日志、行为数据 | 增量追加 | 只需要最新数据 |

---

## 五、常见问题

### Q1: 源表没有时间戳字段怎么办？
A: 可以考虑以下方案：
- 使用自增 ID 作为水位
- 使用 CDC 工具（如 Debezium）捕获变更
- 使用数据库的变更时间戳（如 MySQL 的 binlog position）

### Q2: 增量同步时出现重复数据怎么办？
A: 处理方式：
- 在 Hive 层使用 DISTINCT 或 GROUP BY 去重
- 使用主键进行 MERGE 操作（Spark/Flink）
- 定期执行全量覆盖清理历史重复

### Q3: 拉链表存储膨胀怎么办？
A: 处理方式：
- 设置历史数据归档策略
- 定期关闭过老的拉链记录
- 使用分区表优化查询
