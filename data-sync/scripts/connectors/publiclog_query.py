#!/usr/bin/env python3
"""
PublicLog 查询脚本
查询日志数据
"""
import json
import argparse

def list_logstores(datasource):
    """
    列出可用的 Logstore
    """
    logstores = {
        "datasource": datasource,
        "logstores": [
            {
                "name": "app_access_log",
                "description": "应用访问日志",
                "retention_days": 30
            },
            {
                "name": "app_error_log",
                "description": "应用错误日志",
                "retention_days": 90
            },
            {
                "name": "nginx_access_log",
                "description": "Nginx 访问日志",
                "retention_days": 7
            }
        ]
    }
    return logstores

def get_log_schema(datasource, logstore):
    """
    获取日志的字段 Schema
    """
    schema = {
        "datasource": datasource,
        "logstore": logstore,
        "fields": [
            {"name": "__time__", "type": "long", "description": "日志时间戳（秒）"},
            {"name": "ip", "type": "string", "description": "客户端IP"},
            {"name": "method", "type": "string", "description": "请求方法"},
            {"name": "url", "type": "string", "description": "请求URL"},
            {"name": "status", "type": "int", "description": "HTTP状态码"},
            {"name": "latency", "type": "long", "description": "响应时间（毫秒）"},
            {"name": "user_agent", "type": "string", "description": "User Agent"},
            {"name": "referer", "type": "string", "description": "来源页面"}
        ],
        "index_fields": ["ip", "method", "url", "status"],
        "sample_log": {
            "__time__": 1712899200,
            "ip": "10.0.0.1",
            "method": "GET",
            "url": "/api/v1/order/list",
            "status": 200,
            "latency": 150,
            "user_agent": "Mozilla/5.0",
            "referer": "https://example.com"
        }
    }
    return schema

def main():
    parser = argparse.ArgumentParser(description='PublicLog 查询工具')
    parser.add_argument('--ds', '--datasource', default='ds_publiclog_app', help='数据源名称')
    parser.add_argument('--logstore', help='Logstore 名称')
    parser.add_argument('--mode', choices=['list', 'schema', 'query'], default='schema', help='操作模式')
    
    args = parser.parse_args()
    
    if args.mode == 'list':
        result = list_logstores(args.ds)
    elif args.mode == 'schema':
        if not args.logstore:
            print("Error: --logstore is required for schema mode")
            import sys
            sys.exit(1)
        result = get_log_schema(args.ds, args.logstore)
    else:
        result = {"datasource": args.ds, "logstore": args.logstore}
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
