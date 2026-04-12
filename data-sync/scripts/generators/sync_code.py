#!/usr/bin/env python3
"""
同步代码生成脚本
根据源、目标、模式生成同步代码
"""
import json
import argparse

def generate_sync_code(source_type, source_table, target_type, target_table, mode, fields=None, where_condition=None, partition_field='dt', lifecycle=30):
    """
    生成同步代码
    
    参数:
        source_type: 源类型 (mysql_binlog, mysql_snapshot, kafka, hive, etc.)
        source_table: 源表名
        target_type: 目标类型 (hive, mysql, etc.)
        target_table: 目标表名
        mode: 同步模式 (full_overwrite, incremental, scd)
        fields: 同步字段列表
        where_condition: WHERE 条件
        partition_field: 分区字段
        lifecycle: 生命周期（天）
    
    返回:
        生成的同步代码和配置
    """
    result = {
        "source": {
            "type": source_type,
            "table": source_table
        },
        "target": {
            "type": target_type,
            "table": target_table,
            "lifecycle": lifecycle
        },
        "mode": mode,
        "sync_code": "",
        "ddl_code": "",
        "config": {}
    }
    
    # 根据源类型和模式生成代码
    if mode == "full_overwrite":
        # 全量覆盖模式
        if source_type in ["mysql_binlog", "mysql_snapshot"]:
            if fields:
                field_str = ", ".join(fields)
            else:
                field_str = "*"
            
            result["sync_code"] = f"""
-- 全量覆盖同步: {source_table} -> {target_table}
INSERT OVERWRITE TABLE {target_table} PARTITION ({partition_field}='${{bizdate}}')
SELECT {field_str}
     , '${{bizdate}}' AS {partition_field}
FROM {source_table};
"""
        elif source_type == "hive":
            result["sync_code"] = f"""
-- 全量覆盖同步: {source_table} -> {target_table}
INSERT OVERWRITE TABLE {target_table} PARTITION ({partition_field}='${{bizdate}}')
SELECT *
     , '${{bizdate}}' AS {partition_field}
FROM {source_table}
WHERE {partition_field} = '${{bizdate}}';
"""
        elif source_type in ["kafka", "mq", "publiclog", "sr", "ck"]:
            result["sync_code"] = f"""
-- 实时数据落地: {source_type} -> {target_table}
INSERT INTO TABLE {target_table} PARTITION ({partition_field}='${{bizdate}}')
SELECT *
     , '${{bizdate}}' AS {partition_field}
FROM {source_table}_staging;
"""

    elif mode == "incremental":
        # 增量追加模式
        if source_type in ["mysql_binlog", "mysql_snapshot"]:
            if where_condition:
                where_clause = f"WHERE {where_condition} AND update_time >= '${{bizdate}}'"
            else:
                where_clause = "WHERE update_time >= '${bizdate}'"
            
            result["sync_code"] = f"""
-- 增量追加同步: {source_table} -> {target_table}
INSERT INTO TABLE {target_table} PARTITION ({partition_field}='${{bizdate}}')
SELECT *
     , '${{bizdate}}' AS {partition_field}
FROM {source_table}
{where_clause};
"""
        elif source_type == "hive":
            result["sync_code"] = f"""
-- 增量追加同步: {source_table} -> {target_table}
INSERT INTO TABLE {target_table} PARTITION ({partition_field}='${{bizdate}}')
SELECT *
FROM {source_table}
WHERE {partition_field} = '${{bizdate}}';
"""

    elif mode == "scd":
        # 拉链表模式 (Slowly Changing Dimension)
        if target_type == "hive":
            result["sync_code"] = f"""
-- 拉链表同步: {source_table} -> {target_table}
-- Step 1: 关闭历史版本
SET hive.exec.dynamic.partition.mode=nonstrict;

INSERT INTO TABLE {target_table}
PARTITION ({partition_field})
SELECT *
     , '${{bizdate}}' AS {partition_field}
FROM (
    -- 保留未变化的记录
    SELECT a.* FROM {target_table} a
    LEFT JOIN {source_table} b ON a.id = b.id
    WHERE a.{partition_field} = '${{max_date}}'
      AND (b.id IS NULL OR a.hash_md5 = md5(concat_ws('|', a.*)))
    
    UNION ALL
    
    -- 新增和变化的记录
    SELECT id
         , col1, col2, ...
         , '${{bizdate}}' AS start_date
         , '9999-12-31' AS end_date
    FROM {source_table}
    WHERE update_time >= '${{bizdate}}'
) t;
"""

    # 生成 DDL
    if target_type == "hive":
        result["ddl_code"] = f"""
-- 创建目标表: {target_table}
CREATE TABLE IF NOT EXISTS {target_table} (
    -- 字段定义
    id BIGINT COMMENT '主键ID',
    ...
)
PARTITIONED BY ({partition_field} STRING COMMENT '分区日期')
STORED AS PARQUET
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'partition_lifecycle'='{lifecycle}'
);
"""

    # 附加配置
    result["config"] = {
        "mode": mode,
        "batch_size": 10000,
        "parallelism": 5,
        "error_limit": 100,
        "lifecycle_days": lifecycle
    }
    
    return result

def main():
    parser = argparse.ArgumentParser(description='同步代码生成工具')
    parser.add_argument('--source-type', required=True, help='源类型')
    parser.add_argument('--source-table', required=True, help='源表名')
    parser.add_argument('--target-type', required=True, help='目标类型')
    parser.add_argument('--target-table', required=True, help='目标表名')
    parser.add_argument('--mode', required=True, choices=['full_overwrite', 'incremental', 'scd'], help='同步模式')
    parser.add_argument('--fields', help='同步字段，逗号分隔')
    parser.add_argument('--where', help='WHERE 条件')
    parser.add_argument('--partition', default='dt', help='分区字段')
    parser.add_argument('--lifecycle', type=int, default=30, help='生命周期（天）')
    
    args = parser.parse_args()
    
    fields = args.fields.split(',') if args.fields else None
    
    result = generate_sync_code(
        source_type=args.source_type,
        source_table=args.source_table,
        target_type=args.target_type,
        target_table=args.target_table,
        mode=args.mode,
        fields=fields,
        where_condition=args.where,
        partition_field=args.partition,
        lifecycle=args.lifecycle
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
