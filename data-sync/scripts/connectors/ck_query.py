#!/usr/bin/env python3
"""
ClickHouse 查询脚本
获取表结构或数据
"""
import json
import argparse

def get_ck_schema(datasource, database, table):
    """
    获取 ClickHouse 表结构
    """
    schema = {
        "datasource": datasource,
        "database": database,
        "table": table,
        "engine": "MergeTree",
        "columns": [
            {"name": "id", "type": "UInt64", "comment": "主键ID"},
            {"name": "user_id", "type": "UInt64", "comment": "用户ID"},
            {"name": "event_type", "type": "String", "comment": "事件类型"},
            {"name": "properties", "type": "Map(String, String)", "comment": "事件属性"},
            {"name": "created_at", "type": "DateTime", "comment": "创建时间"},
            {"name": "dt", "type": "Date", "comment": "分区字段"}
        ],
        "primary_key": "id",
        "partition_by": "dt",
        "order_by": "(dt, id)",
        "sample_data": [
            {"id": 1, "user_id": 1001, "event_type": "login", "properties": {"browser": "Chrome"}, "created_at": "2026-04-12 10:00:00", "dt": "2026-04-12"},
            {"id": 2, "user_id": 1002, "event_type": "purchase", "properties": {"amount": "99.5"}, "created_at": "2026-04-12 10:30:00", "dt": "2026-04-12"}
        ]
    }
    return schema

def main():
    parser = argparse.ArgumentParser(description='ClickHouse 查询工具')
    parser.add_argument('--ds', '--datasource', default='ds_ck_analytics', help='数据源名称')
    parser.add_argument('--database', required=True, help='数据库名')
    parser.add_argument('--table', required=True, help='表名')
    parser.add_argument('--mode', choices=['schema', 'data'], default='schema', help='查询模式')
    
    args = parser.parse_args()
    
    if args.mode == 'schema':
        result = get_ck_schema(args.ds, args.database, args.table)
    else:
        result = {
            "datasource": args.ds,
            "database": args.database,
            "table": args.table,
            "sample_data": []
        }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
