# 加密脱敏规则

## 规则类型

| 类型 | 说明 | 场景 |
|------|------|------|
| 加密脱敏 | 可逆加密，数据可还原 | 手机号、身份证等需要部分展示 |
| Hash脱敏 | 不可逆，用于关联分析 | 用户ID、手机号用于join |
| 置空 | 写入Hive时该字段为空 | 不需要的敏感字段 |

## 配置格式

```json
{
  "rules": [
    {
      "field": "phone",
      "type": "encrypt",   // encrypt / hash / clear
      "clearOriginal": false  // 是否置空原字段
    },
    {
      "field": "user_id",
      "type": "hash",
      "clearOriginal": false
    }
  ]
}
```

## 注意事项

- 同一字段不支持多种脱敏方式
- 加密脱敏后数据可解密还原，适用于需要展示部分信息的场景
- Hash脱敏不可逆，适用于不需要还原的场景（如用户行为分析）