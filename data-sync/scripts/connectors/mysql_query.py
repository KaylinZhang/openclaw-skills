#!/usr/bin/env python3
"""
MySQL 查询脚本
获取表结构或数据
"""
import json
import argparse

def get_mysql_schema(datasource, table):
    """
    获取 MySQL 表结构
    TODO: 对接坤坤的数据开发平台 API
    """
    # 模拟返回表结构
    schema = {
        "datasource": datasource,
        "table": table,
        "columns": [
            {"name": "id", "type": "bigint", "comment": "主键ID"},
            {"name": "order_id", "type": "varchar(64)", "comment": "订单号"},
            {"name": "user_id", "type": "bigint", "comment": "用户ID"},
            {"name": "amount", "type": "decimal(10,2)", "comment": "订单金额"},
            {"name": "status", "type": "tinyint", "comment": "订单状态 1-待支付 2-已支付 3-已取消"},
            {"name": "create_time", "type": "datetime", "comment": "创建时间"},
            {"name": "update_time", "type": "datetime", "comment": "更新时间"}
        ],
        "primary_key": "id",
        "partition": None,
        "indexes": ["order_id", "user_id", "update_time"]
    }
    return schema

def query_mysql_data(datasource, table, where=None, limit=10):
    """
    查询 MySQL 数据
    TODO: 对接坤坤的数据开发平台 API
    """
    # 模拟返回数据
    data = {
        "datasource": datasource,
        "table": table,
        "where": where,
        "sample_data": [
            {"id": 1, "order_id": "ORD20260412001", "user_id": 1001, "amount": 99.50, "status": 2, "create_time": "2026-04-12 10:00:00", "update_time": "2026-04-12 10:30:00"},
            {"id": 2, "order_id": "ORD20260412002", "user_id": 1002, "amount": 199.00, "status": 1, "create_time": "2026-04-12 11:00:00", "update_time": "2026-04-12 11:00:00"},
            {"id": 3, "order_id": "ORD20260412003", "user_id": 1001, "amount": 50.00, "status": 3, "create_time": "2026-04-12 09:00:00", "update_time": "2026-04-12 12:00:00"}
        ],
        "total_count_hint": 1234567
    }
    return data

def main():
    parser = argparse.ArgumentParser(description='MySQL 查询工具')
    parser.add_argument('--ds', '--datasource', required=True, help='数据源名称')
    parser.add_argument('--table', required=True, help='表名')
    parser.add_argument('--mode', choices=['schema', 'data', 'sample'], default='schema', help='查询模式')
    parser.add_argument('--where', help='WHERE 条件')
    parser.add_argument('--limit', type=int, default=10, help='返回条数')
    
    args = parser.parse_args()
    
    if args.mode == 'schema':
        result = get_mysql_schema(args.ds, args.table)
    else:
        result = query_mysql_data(args.ds, args.table, args.where, args.limit)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
