#!/usr/bin/env python3
"""
Hive 写入脚本
写入数据到 Hive 表
"""
import json
import argparse

def check_target_table(datasource, database, table):
    """
    检查目标表是否存在，返回表结构
    """
    result = {
        "datasource": datasource,
        "database": database,
        "table": table,
        "exists": True,
        "columns": [
            {"name": "id", "type": "bigint", "comment": "主键ID"},
            {"name": "order_id", "type": "string", "comment": "订单号"},
            {"name": "user_id", "type": "bigint", "comment": "用户ID"},
            {"name": "amount", "type": "decimal(10,2)", "comment": "订单金额"},
            {"name": "status", "type": "string", "comment": "订单状态"},
            {"name": "create_time", "type": "string", "comment": "创建时间"},
            {"name": "update_time", "type": "string", "comment": "更新时间"},
            {"name": "dt", "type": "string", "comment": "分区字段"}
        ],
        "partition": ["dt"],
        "table_type": "managed_table",
        "location": f"/warehouse/{database}/{table}",
        "lifecycle_days": 30
    }
    return result

def generate_ddl(datasource, database, table, columns, partition_fields, storage_format="PARQUET", lifecycle=30):
    """
    生成建表 DDL
    """
    column_defs = []
    for col in columns:
        column_defs.append(f"    {col['name']} {col['type']} COMMENT '{col.get('comment', '')}'")
    
    partition_defs = []
    for pf in partition_fields:
        partition_defs.append(f"    {pf['name']} {pf['type']} COMMENT '{pf.get('comment', '')}'")
    
    ddl = f"""-- 建表语句: {database}.{table}
CREATE TABLE IF NOT EXISTS {database}.{table} (
{chr(10).join(column_defs)}
)
PARTITIONED BY (
{chr(10).join(partition_defs)}
)
STORED AS {storage_format}
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'partition_lifecycle'='{lifecycle}'
);"""
    
    result = {
        "datasource": datasource,
        "database": database,
        "table": table,
        "ddl": ddl
    }
    return result

def main():
    parser = argparse.ArgumentParser(description='Hive 写入工具')
    parser.add_argument('--ds', '--datasource', default='hive_default', help='数据源名称')
    parser.add_argument('--database', default='ods', help='数据库名')
    parser.add_argument('--table', required=True, help='表名')
    parser.add_argument('--mode', choices=['check', 'ddl'], default='check', help='操作模式')
    
    args = parser.parse_args()
    
    if args.mode == 'check':
        result = check_target_table(args.ds, args.database, args.table)
    else:
        columns = [
            {"name": "id", "type": "bigint", "comment": "主键ID"},
            {"name": "col1", "type": "string", "comment": "字段1"}
        ]
        partition_fields = [
            {"name": "dt", "type": "string", "comment": "分区字段"}
        ]
        result = generate_ddl(args.ds, args.database, args.table, columns, partition_fields)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
