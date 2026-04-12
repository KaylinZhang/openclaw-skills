#!/usr/bin/env python3
"""
调度配置生成脚本
根据执行方式生成调度配置
"""
import json
import argparse
from datetime import datetime

def generate_schedule_config(frequency, time, depends_on=None, earliest_start=None, baseline=None):
    """
    生成调度配置
    
    参数:
        frequency: 执行频率 (manual, daily, hourly, weekly, monthly)
        time: 执行时间 (HH:MM 格式)
        depends_on: 依赖任务列表
        earliest_start: 最早开始时间 (HH:MM)
        baseline: 绑定的基线名称
    
    返回:
        生成的调度配置
    """
    result = {
        "execution_type": frequency,
        "config": {}
    }
    
    if frequency == "manual":
        # 手动执行
        result["config"] = {
            "type": "manual",
            "description": "手动触发执行",
            "cron": None,
            "can_rerun": True
        }
    
    elif frequency == "daily":
        # 每天执行
        hour, minute = time.split(":")
        result["config"] = {
            "type": "周期任务",
            "cron": f"0 {minute} {hour} * * ?",
            "description": f"每天 {hour}:{minute} 执行",
            "time": time,
            "depends_on": depends_on or [],
            "earliest_start": earliest_start,
            "baseline": baseline
        }
    
    elif frequency == "hourly":
        # 每小时执行
        result["config"] = {
            "type": "周期任务",
            "cron": f"0 0 */1 * * ?",
            "description": f"每小时执行一次",
            "interval_hours": 1,
            "depends_on": depends_on or [],
            "earliest_start": earliest_start,
            "baseline": baseline
        }
    
    elif frequency == "weekly":
        # 每周执行
        hour, minute = time.split(":")
        result["config"] = {
            "type": "周期任务",
            "cron": f"0 {minute} {hour} ? * MON",
            "description": f"每周一 {hour}:{minute} 执行",
            "day_of_week": "Monday",
            "time": time,
            "depends_on": depends_on or [],
            "earliest_start": earliest_start,
            "baseline": baseline
        }
    
    elif frequency == "monthly":
        # 每月执行
        hour, minute = time.split(":")
        result["config"] = {
            "type": "周期任务",
            "cron": f"0 {minute} {hour} 1 * ?",
            "description": f"每月1号 {hour}:{minute} 执行",
            "day_of_month": 1,
            "time": time,
            "depends_on": depends_on or [],
            "earliest_start": earliest_start,
            "baseline": baseline
        }
    
    return result

def main():
    parser = argparse.ArgumentParser(description='调度配置生成工具')
    parser.add_argument('--frequency', required=True, choices=['manual', 'daily', 'hourly', 'weekly', 'monthly'], help='执行频率')
    parser.add_argument('--time', default='01:00', help='执行时间 (HH:MM)')
    parser.add_argument('--depends-on', help='依赖任务，逗号分隔')
    parser.add_argument('--earliest-start', help='最早开始时间 (HH:MM)')
    parser.add_argument('--baseline', help='绑定的基线名称')
    
    args = parser.parse_args()
    
    depends = args.depends_on.split(',') if args.depends_on else None
    
    result = generate_schedule_config(
        frequency=args.frequency,
        time=args.time,
        depends_on=depends,
        earliest_start=args.earliest_start,
        baseline=args.baseline
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
