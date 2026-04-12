#!/usr/bin/env python3
"""
MQ (ddMQ) 消费脚本
获取 Topic 列表或消费消息
"""
import json
import argparse

def list_topics(datasource):
    """
    列出 ddMQ 可用的 Topic
    """
    topics = {
        "datasource": datasource,
        "type": "ddmq",
        "topics": [
            {
                "name": "ddmq.order.create",
                "type": "普通队列",
                "consumer_group": "data_sync_group",
                "message_format": "JSON"
            },
            {
                "name": "ddmq.order.pay",
                "type": "普通队列",
                "consumer_group": "data_sync_group",
                "message_format": "JSON"
            },
            {
                "name": "ddmq.user.action",
                "type": "普通队列",
                "consumer_group": "data_sync_group",
                "message_format": "JSON"
            }
        ]
    }
    return topics

def get_topic_schema(datasource, topic):
    """
    获取 Topic 的消息 Schema
    """
    schema = {
        "datasource": datasource,
        "topic": topic,
        "format": "JSON",
        "fields": [
            {"name": "id", "type": "string", "description": "消息ID"},
            {"name": "biz_id", "type": "string", "description": "业务ID"},
            {"name": "event_type", "type": "string", "description": "事件类型"},
            {"name": "data", "type": "object", "description": "业务数据"},
            {"name": "timestamp", "type": "long", "description": "时间戳"}
        ],
        "sample_message": {
            "id": "msg_xxx",
            "biz_id": "ORD20260412001",
            "event_type": "order_created",
            "data": {"order_id": "ORD20260412001", "amount": 99.50},
            "timestamp": 1712899200000
        }
    }
    return schema

def main():
    parser = argparse.ArgumentParser(description='MQ 消费工具')
    parser.add_argument('--ds', '--datasource', default='ds_ddmq_default', help='数据源名称')
    parser.add_argument('--topic', help='Topic 名称')
    parser.add_argument('--mode', choices=['list', 'schema', 'consume'], default='schema', help='操作模式')
    
    args = parser.parse_args()
    
    if args.mode == 'list':
        result = list_topics(args.ds)
    elif args.mode == 'schema':
        if not args.topic:
            print("Error: --topic is required for schema mode")
            import sys
            sys.exit(1)
        result = get_topic_schema(args.ds, args.topic)
    else:
        result = {"datasource": args.ds, "topic": args.topic, "messages": []}
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
