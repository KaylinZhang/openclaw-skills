#!/usr/bin/env python3
"""
Kafka 消费脚本
获取 Topic 列表或消费消息
"""
import json
import argparse

def list_topics(datasource):
    """
    列出 Kafka 可用的 Topic
    """
    topics = {
        "datasource": datasource,
        "topics": [
            {
                "name": "order_topic",
                "partitions": 12,
                "replication_factor": 3,
                "message_format": "JSON",
                "avg_message_size": 1024
            },
            {
                "name": "user_topic",
                "partitions": 8,
                "replication_factor": 3,
                "message_format": "JSON",
                "avg_message_size": 512
            },
            {
                "name": "payment_topic",
                "partitions": 16,
                "replication_factor": 3,
                "message_format": "Avro",
                "avg_message_size": 2048
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
            {"name": "order_id", "type": "string", "description": "订单号"},
            {"name": "user_id", "type": "long", "description": "用户ID"},
            {"name": "amount", "type": "double", "description": "订单金额"},
            {"name": "timestamp", "type": "long", "description": "时间戳（毫秒）"},
            {"name": "event_type", "type": "string", "description": "事件类型"}
        ],
        "sample_message": {
            "order_id": "ORD20260412001",
            "user_id": 12345,
            "amount": 99.50,
            "timestamp": 1712899200000,
            "event_type": "create"
        }
    }
    return schema

def main():
    parser = argparse.ArgumentParser(description='Kafka 消费工具')
    parser.add_argument('--ds', '--datasource', required=True, help='数据源名称')
    parser.add_argument('--topic', help='Topic 名称')
    parser.add_argument('--mode', choices=['list', 'schema', 'consume'], default='schema', help='操作模式')
    parser.add_argument('--limit', type=int, default=10, help='消费消息数量')
    
    args = parser.parse_args()
    
    if args.mode == 'list':
        result = list_topics(args.ds)
    elif args.mode == 'schema':
        if not args.topic:
            print("Error: --topic is required for schema mode")
            sys.exit(1)
        result = get_topic_schema(args.ds, args.topic)
    else:
        result = {
            "datasource": args.ds,
            "topic": args.topic,
            "messages": []
        }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    import sys
    main()
