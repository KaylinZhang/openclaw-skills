#!/usr/bin/env python3
"""
数据源列表脚本
列出当前可用的数据源
"""
import json
import sys

def list_datasources():
    """
    返回当前可用的数据源列表
    TODO: 这里需要对接坤坤的数据开发平台 API
    """
    # 模拟数据源列表
    datasources = {
        "mysql": [
            {
                "name": "ds_mysql_prod",
                "type": "mysql",
                "mode": "binlog",
                "host": "rm-xxx.mysql.rds.aliyuncs.com",
                "port": 3306,
                "database": "order_db",
                "usage": "read",
                "maintainer": "DBA"
            },
            {
                "name": "ds_mysql_write",
                "type": "mysql",
                "mode": "snapshot",
                "host": "rm-yyy.mysql.rds.aliyuncs.com",
                "port": 3306,
                "database": "warehouse",
                "usage": "write"
            }
        ],
        "hive": [
            {
                "name": "hive_default",
                "type": "hive",
                "project": "当前项目",
                "database": "ods"
            }
        ],
        "kafka": [
            {
                "name": "ds_kafka_main",
                "type": "kafka",
                "cluster": "kafka-prod",
                "app_id": "data_sync_app",
                "topics": ["order_topic", "user_topic"]
            }
        ],
        "mq": [
            {
                "name": "ds_ddmq_default",
                "type": "ddmq",
                "description": "公司内部 ddMQ，无需单独配置"
            }
        ],
        "publiclog": [
            {
                "name": "ds_publiclog_app",
                "type": "publiclog",
                "public_key": "LTAIxxxxxxx"
            }
        ],
        "sr": [
            {
                "name": "ds_sr_realtime",
                "type": "sr",
                "cluster": "sr-prod"
            }
        ],
        "ck": [
            {
                "name": "ds_ck_analytics",
                "type": "clickhouse",
                "cluster": "ck-prod"
            }
        ]
    }
    
    print(json.dumps(datasources, indent=2, ensure_ascii=False))
    return datasources

if __name__ == "__main__":
    list_datasources()
