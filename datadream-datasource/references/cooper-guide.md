# Cooper 数据源配置指引

本文档用于指导配置 Cooper 数据源所需的参数和获取方式。

## 前置条件

1. 需要有效的 Cooper 团队空间
2. 需要申请 Cooper OpenAPI Token

## 参数说明

### spaceId（必填）

Cooper 团队空间 ID，从 Cooper 空间 URL 中获取 `team-file` 后的数字串。

示例 URL：
```
https://cooper.didichuxing.com/team-file/1234567890/...
```

spaceId = `1234567890`

### token（必填）

Cooper OpenAPI Token，需通过 BPM 流程申请。

**申请方式**：
1. 访问 BPM 申请页面：https://bpm.didichuxing.com/process/form/bykey/cooper_open_api?tenantId=Cooper
2. 填写申请表单（需说明用途）
3. 审批通过后，Token 会通过邮件下发
4. 收到邮件后，将 Token 填入数据源配置

⚠️ **注意**：Token 是敏感信息，请妥善保管，不要明文传播。

## 常见问题

### Q: 申请 Token 需要多长时间？

A: 通常 1-2 个工作日，具体取决于审批流程。

### Q: Token 有效期多久？

A: 请参考邮件中的说明，通常为 1 年，到期需重新申请。

### Q: 如果 Token 泄露了怎么办？

A: 立即通过 BPM 申请吊销旧 Token，并重新申请新 Token。

---

*本文档持续更新中，如有问题请联系 DataDream 平台团队。*
