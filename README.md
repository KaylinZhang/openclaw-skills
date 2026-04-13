# OpenClaw Skills

坤坤的 OpenClaw Agent 技能集合。

## 简介

本仓库包含坤坤开发和维护的 OpenClaw Skills，用于扩展 OpenClaw Agent 的能力。

## 可用 Skills

| Skill | 用途 | 安装命令 | 状态 |
|-------|------|----------|------|
| **data-sync** | 数据同步：支持 MySQL、Kafka、MQ、PublicLog、SR、ClickHouse 等数据源到目标存储的同步任务创建与管理 | `skillhub_install install_skill KaylinZhang/openclaw-skills/data-sync` | ✅ 已完成 |

## 安装方法

### 方式一：通过 SkillHub 安装（推荐）

```bash
# 安装单个 Skill
skillhub_install install_skill KaylinZhang/openclaw-skills/data-sync

# 查看所有可用 Skills
skillhub_install list
```

### 方式二：手动安装

```bash
# Clone 仓库
git clone https://github.com/KaylinZhang/openclaw-skills.git

# 复制 Skill 到本地目录
cp -r data-sync ~/.qclaw/skills/
```

## Skill 详细介绍

### data-sync

数据同步专家，用于创建和管理离线数据同步任务。

**支持的数据源方向：**

| 方向 | 数据源类型 |
|------|-----------|
| 数据源同步到目标 | MySQL-binlog、MySQL-快照、Kafka、MQ、PublicLog、SR、ClickHouse |
| 数据源回写到源 | MySQL |

**支持的同步模式：**

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| 全量覆盖 | 每次整表拉取，覆盖写入 | 维度表、配置表 |
| 增量追加 | 基于时间戳/主键，只拉新增 | Fact 表、行为数据 |

**核心功能：**

- 对话式创建同步任务
- 自动生成同步代码
- 调度配置生成
- 告警规则配置
- 任务报错处理

**详细文档：** 请参考 `data-sync/SKILL.md`

## 目录结构

```
openclaw-skills/
├── README.md                   # 本文件
├── data-sync/                 # 数据同步 Skill
│   ├── SKILL.md              # Skill 定义
│   ├── references/           # 参考文档
│   │   ├── sync_modes.md    # 同步模式详解
│   │   ├── datasource_config.md
│   │   └── alert_rules.md
│   └── scripts/              # 执行脚本
│       ├── datasource/
│       ├── connectors/
│       └── generators/
└── ...
```

## 使用示例

```
用户：帮我把订单表同步到 Hive

AI：好的，我来帮你创建同步任务。先确认一下数据源：
    - 你的 MySQL 数据源是哪个？
    - 表名是 order 吗？
    ...

（更多对话示例请参考 SKILL.md）
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- GitHub: [KaylinZhang](https://github.com/KaylinZhang)
- 问题反馈: [Issues](https://github.com/KaylinZhang/openclaw-skills/issues)
