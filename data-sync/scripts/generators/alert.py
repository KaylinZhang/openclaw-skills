#!/usr/bin/env python3
"""
告警配置生成脚本
生成告警规则和通知配置
"""
import json
import argparse

def generate_alert_config(task_name, owner, receivers=None, quiet_hours=None, channels=None):
    """
    生成告警配置
    
    参数:
        task_name: 任务名称
        owner: 任务负责人
        receivers: 告警接收人列表
        quiet_hours: 告警免打扰时段
        channels: 通知渠道
    
    返回:
        生成的告警配置
    """
    # 默认接收人
    if receivers is None:
        receivers = [owner]
    
    # 默认通知渠道
    if channels is None:
        channels = ["DC", "phone"]
    
    result = {
        "task_name": task_name,
        "rules": [
            {
                "name": f"{task_name}_fail",
                "type": "task_failure",
                "description": "任务执行失败告警",
                "channels": channels,
                "receivers": receivers,
                "quiet_hours": quiet_hours,
                "enabled": True
            },
            {
                "name": f"{task_name}_data_delay",
                "type": "data_delay",
                "description": "数据延迟告警",
                "threshold_minutes": 120,
                "channels": ["DC"],
                "receivers": receivers,
                "quiet_hours": quiet_hours,
                "enabled": True
            },
            {
                "name": f"{task_name}_data_quality",
                "type": "data_quality",
                "description": "数据质量异常告警",
                "rules": {
                    "null_ratio_threshold": 0.1,
                    "duplicate_ratio_threshold": 0.01
                },
                "channels": ["DC"],
                "receivers": receivers,
                "quiet_hours": quiet_hours,
                "enabled": False
            }
        ],
        "channels": {
            "DC": {
                "type": "内部消息",
                "description": "DataCenter 内部消息通知"
            },
            "phone": {
                "type": "电话",
                "description": "自动拨打电话（紧急告警）"
            },
            "sms": {
                "type": "短信",
                "description": "短信通知"
            },
            "email": {
                "type": "邮件",
                "description": "邮件通知"
            }
        },
        "default_config": {
            "owner": owner,
            "receivers": receivers,
            "channels": channels,
            "quiet_hours": quiet_hours or "无"
        }
    }
    
    return result

def main():
    parser = argparse.ArgumentParser(description='告警配置生成工具')
    parser.add_argument('--task', required=True, help='任务名称')
    parser.add_argument('--owner', required=True, help='任务负责人')
    parser.add_argument('--receivers', help='告警接收人，逗号分隔')
    parser.add_argument('--quiet-hours', help='告警免打扰时段，格式: 22:00-08:00')
    parser.add_argument('--channels', help='通知渠道，逗号分隔 (DC/phone/sms/email)')
    
    args = parser.parse_args()
    
    receivers = args.receivers.split(',') if args.receivers else None
    channels = args.channels.split(',') if args.channels else None
    
    result = generate_alert_config(
        task_name=args.task,
        owner=args.owner,
        receivers=receivers,
        quiet_hours=args.quiet_hours,
        channels=channels
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
