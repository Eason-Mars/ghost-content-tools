# Personal Brand — Workspace

> **完全独立于 A股研究院。不共享内容、不交叉引用、不混用推送渠道。**

## 目标

打造支撑 AI 业务的个人品牌矩阵：
- **AI 金融投资**：服务海外华人的 AI 投资智囊团
- **AI 餐饮**：日本高端餐饮 + 连锁餐饮的 AI 重构实践

## 文件夹结构

```
personal-brand/
├── README.md              ← 本文件，总览
├── PROFILE.md             ← 个人定位、账号简介（各平台版本）
├── CONTENT_STRATEGY.md    ← 内容策略、5大支柱、发布节奏
├── PIPELINE.md            ← 零写作内容流水线操作手册
│
├── content/
│   ├── queue/             ← 待审核/待发布的内容草稿
│   ├── drafts/            ← 工作中的草稿
│   └── published/         ← 已发布内容存档（带日期+平台）
│
├── knowledge/             ← 用于内容生成的背景知识库
│   ├── founder-story.md   ← 创始人故事、经历、金句库
│   ├── japan-restaurant.md← 日本餐饮洞察与案例
│   ├── ai-finance.md      ← AI投资智囊团知识库
│   └── links/             ← 用户发来的参考链接整理
│
├── platforms/
│   ├── xiaohongshu.md     ← 小红书账号配置+发布规范
│   ├── twitter.md         ← Twitter/X 账号配置+发布规范
│   └── linkedin.md        ← LinkedIn 账号配置+发布规范
│
└── assets/
    └── (头像、封面图、模板等)
```

## 与 A股研究院的边界

| 维度 | A股研究院 | Personal Brand |
|------|----------|---------------|
| 文件夹 | `skills/a-share-monitor/` | `personal-brand/` |
| 推送渠道 | Eason & Steve 群（-5103092512） | 各SNS平台（单独配置） |
| 内容类型 | 行情分析、龙虎榜、轮动信号 | 个人洞察、创业故事、AI实践 |
| 触发方式 | HEARTBEAT.md + cron | 手动触发 + 内容队列 |
| 知识库 | `knowledge/finance/` | `personal-brand/knowledge/` |

**规则：两个板块的内容、数据、推送渠道严格隔离，互不引用。**
