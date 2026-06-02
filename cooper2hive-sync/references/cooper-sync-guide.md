# Cooper2Hive 使用手册

本文档用于指导配置 Cooper2Hive 同步任务的详细参数和注意事项。

## 前置条件

1. 需要有可用的 Cooper 数据源（参考 datadream-datasource skill）
2. 任务负责人需拥有 Cooper 文档的下载权限

## docId 获取方式

Cooper 文档 ID 从文档 URL 中获取，`sheet` 后的数字串即为 docId。

示例 URL：
```
https://cooper.didichuxing.com/doc/YcSAIftpNcle/sheet/1234567890
```

docId = `1234567890`

## 多 sheet 配置

- 多 sheet 同步时，多个 sheet 的表头必须一致
- 需在 `sheetNames` 参数中指定要同步的 sheet 名称列表
- 默认单 sheet 同步

## 标题行配置

- `titleRow` 指定标题所在行，默认第一行
- 每个 sheet 都需单独指定标题行
- 标题行必须连续有值，不能有空单元格

## 字段类型支持

| 类型 | 说明 |
|------|------|
| INT, SMALLINT, BIGINT | 整型 |
| DOUBLE, FLOAT | 浮点型 |
| CHAR, STRING | 字符串型 |
| DATE | 日期类型，格式：yyyy-MM-dd |
| TIMESTAMP | 时间戳类型，格式：yyyy-MM-dd HH:mm:ss |

## 非自动建表分区说明

非自动建表时必须指定写入分区，分区表达式示例：
```
${Y=0}-${M=0}-${D=-1}
```
假设调度时间为 2026-05-28，将写入 Hive 表分区 `dt=2026-05-27`。

## 常见问题

### Q: Cooper 表格增加字段后需要做什么？

A: 需先在 Hive 表中新增对应字段，再修改同步任务的字段映射。

### Q: 多 sheet 同步有什么限制？

A: 所有 sheet 的表头必须完全一致，否则会导致字段映射错乱。

---

*本文档持续更新中，如有问题请联系 DataDream 平台团队。*
