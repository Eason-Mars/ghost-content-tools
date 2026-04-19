# PIPELINE.md — 零写作内容流水线

## 核心逻辑

**你只需要"说"，我来"写"。**

你的输入 → OpenClaw 处理 → 平台草稿 → 你一键确认 → 发布

---

## 5 种触发输入（按摩擦度从低到高）

### ① 语音备忘（最低摩擦）
- 方式：Telegram 发语音，前缀说「内容素材：」
- 我来做：转文字 + 识别支柱主题 + 生成草稿 + 存入 `content/queue/`
- 示例：「内容素材：今天和一个日本投资人聊天，他说他完全不理解为什么中国人喜欢辣，但他的员工都去排队...」

### ② 转发链接 + 一句话（次低摩擦）
- 方式：Telegram 转发任何文章/推文 + 你的1句感想
- 我来做：读取原文 + 结合你的视角 + 写成点评帖子
- 触发词：不需要特定触发词，发链接我就知道

### ③ 项目节点更新
- 方式：「又一家店上了AI系统」/「刚和客户聊完xx」
- 我来做：提问追问细节 → 整理成案例帖
- 频率：项目有进展时自然触发

### ④ 每周 10 分钟对话（最高质量）
- 方式：每周一次，我问你答
- 我来做：半结构化采访 → 整理 2-3 篇内容
- 模板提问：「这周遇到最有意思的一件事？」「有什么认知被更新了？」

### ⑤ 自动生成（无需你的输入）
- 我监控：AI/餐饮/日本市场热点新闻
- 生成：「你视角的评论草稿」存入 queue
- 你只需：确认或放弃

---

## content/queue/ 操作规范

每个草稿文件命名格式：
```
YYYY-MM-DD_[平台]_[支柱编号]_[标题关键词].md
```

例如：
```
2026-03-05_XHS_P1_AI餐厅排班系统上线.md
2026-03-06_Twitter_P3_OpenClaw实战.md
```

文件内容格式：
```markdown
## 元数据
- 平台：小红书
- 支柱：日本AI餐饮
- 状态：待审核
- 预计发布：2026-03-07

## 正文草稿

[内容在这里]

## 配图建议
- 图1：...
- 图2：...

## 话题标签
#在日华人 #AI创业 #日本餐饮
```

---

## 触发命令（在 Telegram 直接说）

| 命令 | 我来做什么 |
|------|----------|
| `/brand 素材：[内容]` | 处理素材 → 生成草稿 |
| `/brand 看队列` | 列出所有待发布草稿 |
| `/brand 发布 [文件名]` | 展示最终版本，确认后手动发 |
| `/brand 写 [主题]` | 我主动生成一篇该主题的草稿 |
| `/brand 周报` | 统计本周内容产出、各平台数据 |
| `/brand 知识库 [链接]` | 把链接内容整理进知识库 |

---

## 发布流程（当前阶段：半自动）

```
草稿生成 → 存入 queue/
    ↓
你查看/修改（Telegram 里直接回复修改意见）
    ↓
确认 → 文件移入 published/ + 标记日期
    ↓
你复制到对应平台发布（小红书/Twitter 目前需手动）
    ↓
（未来）Twitter API 自动发布
```

---

## 知识库维护

`personal-brand/knowledge/` 是我生成内容的"长期记忆"：

- `founder-story.md`：你的经历、金句、态度，我每次写都会参考
- `japan-restaurant.md`：餐厅运营数据、日本市场洞察、实际案例
- `ai-finance.md`：AI投资方法论、海外华人资产配置框架
- `links/`：你发给我的参考链接，整理成结构化知识点

**每次你分享新的背景信息，我都会更新对应知识库文件。**

---

## 微信公众号发布规范（2026-03-21 固化）

### 签名（所有微信文章统一，不得修改）
```
在东京经营几家餐厅，用AI做投资研究和餐饮零售管理——然后把踩过的坑写出来
```
参考：`content/japan-restaurant-leasing-trust.wechat.html`

### 文件规范
- 博客版：`content/<slug>.html`（Ghost 用，带 CSS class）
- 微信版：`content/<slug>.wechat.html`（全 inline style + section 标签，无外部 CSS）
- 不得把博客 HTML 直接推微信

### 草稿更新规范
- 首次：`python3 scripts/publish_wechat.py <file> --draft`（自动保存 media_id 到 .wechat_cache.json）
- 修改：`python3 scripts/publish_wechat.py <file> --update <media_id> --draft`
- 禁止：同一篇文章用 `--force-new` 推新草稿，除非旧草稿已发布或删除


### 签名样式（固化，白底版本）
```html
<section style="background:#fff;padding:20px 0;margin-top:40px;border-top:2px solid #8B3A2A;border-bottom:2px solid #8B3A2A;">
<p style="font-size:17px;font-weight:800;margin-bottom:4px;color:#8B3A2A;">我叫 Eason</p>
<p style="font-size:12px;color:#888;line-height:1.8;margin-bottom:6px;letter-spacing:0.5px;">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</p>
<p style="font-size:14px;color:#333;line-height:1.8;margin:0;">在东京经营几家餐厅，用AI做投资研究和餐饮零售管理——然后把踩过的坑写出来</p>
</section>
```
- 白底 + 棕红上下边线（非深色背景块）
- 参考来源：Eason 截图确认（2026-03-21）
