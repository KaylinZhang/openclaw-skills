# 告警配置详解

## 配置项说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| errorRecordLimit | int | 0 | 错误记录数超限告警阈值 |
| writeRowLimit | int | 0 | 写入行数超下限告警阈值 |
| alertReceivers | string[] | 任务负责人 | 告警接收人 |
| alertMethods | string[] | 继承任务等级 | 电话/短信/DChat/邮件 |
| alertGroup | string | 无 | odin值班组/DChat群聊 |
| quietHours | string | 无 | 告警免打扰时段（如 22:00-08:00） |
| phoneQuietHours | string | 无 | 电话免打扰时间范围 |

## 告警方式

- **电话**：紧急告警，仅限关键任务
- **短信**：备用通知方式
- **DChat**：推荐方式，支持按人/群/值班表
- **邮件**：非紧急通知

## 告警组

可设置值班表或指定 DChat 群聊，避免个人无法及时处理时任务无人响应。