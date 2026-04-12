#!/usr/bin/env python3
"""
SR (Stream Radio/流数据) 查询脚本
查询流数据
"""
import json
import argparse

def list_streams(datasource):
    """
    列出可用的流数据源
    """
    streams = {
        "datasource": datasource,
        "streams": [
            {
                "name": "sr_realtime_order",
                "type": "流数据",
                "description": "实时订单流",
                "format": "JSON"
            },
            {
                "name": "sr_realtime_click",
                "type": "流数据",
                "description": "用户点击流",
                "format": "JSON"
            }
        ]
    }
    return streams

def get_stream_schema(datasource, stream):
    """
    获取流数据的 Schema
    """
    schema = {
        "datasource": datasource,
        "stream": stream,
        "format": "JSON",
        "fields": [
            {"name": "event_time", "type": "timestamp", "description": "事件时间"},
            {"name": "event_type", "type": "string", "description": "事件类型"},
            {"name": "user_id", "type": "string", "description": "用户ID"},
            {"name": "session_id", "type": "string", "description": "会话ID"},
            {"name": "page_url", "type": "string", "description": "页面URL"},
            {"name": "element_id", "type": "string", "description": "元素ID"},
            {"name": "action", "type": "string", "description": "用户行为"}
        ],
        "watermark": "event_time",
        "sample_message": {
            "event_time": "2026-04-12 10:00:00",
            "event_type": "click",
            "user_id": "12345",
            "session_id": "sess_xxx",
            "page_url": "/product/detail/123",
            "element_id": "btn_buy",
            "action": "click"
        }
    }
    return schema

def main():
    parser = argparse.ArgumentParser(description='SR 查询工具')
    parser.add_argument('--ds', '--datasource', default='ds_sr_realtime', help='数据源名称')
    parser.add_argument('--stream', help='流数据名称')
    parser.add_argument('--mode', choices=['list', 'schema'], default='schema', help='操作模式')
    
    args = parser.parse_args()
    
    if args.mode == 'list':
        result = list_streams(args.ds)
    elif args.mode == 'schema':
        if not args.stream:
            print("Error: --stream is required for schema mode")
            import sys
            sys.exit(1)
        result = get_stream_schema(args.ds, args.stream)
    else:
        result = {"datasource": args.ds}
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
