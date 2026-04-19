# CONTEXT.md — Eason Blog 群专属上下文
> 每次进入 Eason Blog 群时优先读本文件，快速进入个人品牌工作状态。
> 详细文件见 `personal-brand/` 目录。本文件保持 ≤120 行，始终是最新的。

---

## ⚠️ Mars 角色铁律（必读，不可违反）

**Mars 永远是这个群的对话接口。** Telegram binding 永远指向 main agent，不能改。
InSight 是后台 sub-agent，不直接面对用户。工作流：
> Eason 发指令 → Mars 接收 → `sessions_spawn(agentId="insight")` → InSight 执行 → Mars 交付

❌ 绝对不建议把 Eason Blog 群的 binding 切换给 InSight
❌ 绝对不说"切换后 InSight 接管这个群"
❌ **Mars 绝不自己写博客/文章/内容草稿** — 必须 spawn InSight 执行，Mars 只做 QC + Ghost 发布

### 📋 完整工作流（不可省略任何步骤）
1. Eason 发内容任务 → Mars 理解意图、拆解 task
2. `sessions_spawn(agentId: "insight")` 派发给 InSight
   - task 必须包含：「closing 区块从 `template-ghost.html` 原样复制，禁止手写签名」
3. InSight 执行：写草稿 HTML → 存到 `personal-brand/content/drafts/`
4. Mars QC：APAG结构 / 签名格式 / 内容禁区 / 人味
   - 签名 QC 三项必须全过：`.name`=「我叫 Eason」/ `.creds`=「CFA持证人…」/ closing 无禁止词
5. QC PASS → Mars 发草稿文件给 Eason 确认
6. Eason 确认 → Mars 按 `GHOST_PUBLISHING.md` 操作规范推送 Ghost（InSight 无浏览器权限）
   - **推送前**：过 `GHOST_PUBLISHING.md` 第六节检查清单
   - 🔴 **必须带 `--draft` 参数**，推草稿箱，不直接发布
   - Eason 在 Ghost 后台看完确认，自己点发布
   - **发布后**：`web_fetch` 实际 URL，确认「我叫 Eason」在页面中存在（第六A节）

---

## 这个群是干什么的

**Eason Blog** = Eason Zhang 的个人品牌内容工作室。
- 只做个人品牌：Ghost 博文、小红书、Twitter/X、LinkedIn
- 与 A股研究院（Eason Venture Studio）严格隔离，不共享内容/渠道/知识库
- 工作模式：零写作——Eason 说/发素材，Mars 生成草稿，Eason 确认发布

---

## 关于 Eason Zhang（必读背景）

**姓名**：张强 / Eason Zhang（对外用 Eason）
**主域名**：easonzhang.ai（待注册）
**资质**：CFA持证人（2008），英语8级，中日英三语

**职业时间线（精华版）**：
- 德勤战略咨询合伙人 7年 → 服务 MUFG/日立/NTT Data 等日本顶级企业
- 当天金融总裁 → 半年完成重组+对接港股资本化退出
- 一森科技 CEO 8年 → AI营销+日本市场，SaaS 交了学费但资源留下来了
- 2025至今：**杨国福麻辣烫日本**，6家（3开业：神保町/池袋西口等，3装修中）
  - 核心数据：**80%日本本地客 + 80%年轻女性**（不是偶然，是系统结果）
- 2026至今：专注 AI 两个方向（AMI + ARTI）

**差异化标签**：战略框架 × 真实落地 × 日本 × AI × 金融

**金句库**（写作用）：
- 「咨询给了我框架，创业给了我代价，日本给了我耐心」
- 「80%的客人是日本年轻女性——这不是偶然，是系统的结果」
- 「一个有CFA的人，才知道AI投资工具哪里是噱头」
- 「我不写博客，但我每天都在经历值得写的事」

---

## 两个核心产品

### AMI（AI餐饮预订平台）
- 网/朋友/阿米，双端：AMI Go（C端游客）+ AMI Biz（B端餐厅数字前台）
- 核心创新：敬语引擎（Keigo Engineering）+ 动态影子库存
- 目标：连接4000万入境游客与日本餐厅
- 团队：CEO Eason，COO Coco（前Skylark/FIH），CTO Steve（前Google Labs）
- 详细文档：`knowledge/ami-product.md` / `knowledge/AMI-pitch-deck-2026.pdf`

### ARTI（AI金融投资平台）
- AI Agent + Round Table + Investment
- 面向海外华人高净值投资者，机构级AI决策平台
- 战略合作：德林控股 DL Holdings（1709.HK），香港SFC持牌
- 双中心：东京（技术）+ 香港（营销/合规）
- 详细文档：`knowledge/ai-finance.md` / `knowledge/ARTI-pitch-deck-2026.pptx`

---

## 内容策略（快速参考）

### 5大内容支柱
| # | 主题 | 平台 | 频率 |
|---|------|------|------|
| 1 | 🍜 日本AI餐饮实录 | 小红书、Twitter | 每周2条 |
| 2 | 💰 海外华人资产配置 | 小红书 | 每周2条 |
| 3 | 🤖 AI工具实战 | Twitter、LinkedIn | 每周1条 |
| 4 | 🧭 创业者思考 | LinkedIn、Twitter | 每两周1条 |
| 5 | 🇯🇵 日本生活观察 | 小红书 | 每周1条 |

### 写作框架：APAG（所有文章默认使用）
- **A（Attention）**：第一句话抓住人——数字/反直觉/问题/好处
- **P（Perspective）**：描绘"敌人"——读者持有的错误观点，引发共鸣
- **A（Advantage）**：描绘"英雄"——正确方向，建立可信度
- **G（Gamify）**：给出可操作步骤 + 明确CTA
- 短篇简化：A+P（高共鸣）或 A+G（高转化）

### Twitter 语言策略
- **英文为主**：AI/Japan/餐饮科技 → 触达国际圈
- **中文穿插**：资产配置/华人投资圈内容
- 同一条不中英混写；同一观点可发两条

### 内容禁区
❌ 纯转发行情图（隔离原则）
❌ 具体投资建议或股票推荐
❌ 德勤客户具体信息（保密协议）
❌ 大量AI生成感强的内容（要有"人味"）
❌ **任何品牌名**（杨国福等合作方品牌，一律不点名）
❌ **任何产品名**（AMI、ARTI 等自有产品，一律不提及）
→ 代替写法：「我在日本经营的麻辣烫连锁」/「我们的AI餐饮预订平台」/「我们的AI投资决策工具」

---

## 知识库文件索引

| 文件 | 内容 |
|------|------|
| `knowledge/founder-story.md` | 创始人完整经历、金句、写作禁区 |
| `knowledge/japan-restaurant.md` | 餐厅运营数据、日本市场洞察 |
| `knowledge/ai-finance.md` | AI投资方法论、华人资产配置框架 |
| `knowledge/ami-product.md` | AMI产品全貌 |
| `knowledge/AMI-pitch-deck-2026.pdf` | AMI Pitch Deck |
| `knowledge/ARTI-pitch-deck-2026.pptx` | ARTI Pitch Deck |
| `knowledge/eason-cv-2026.docx` | 完整简历（参考用） |
| `knowledge/links/` | 用户分享的参考链接知识点 |

---

## 内容队列现状

> ⚠️ 本表最后更新 2026-04-06，共 37 篇已发布（sitemap 为准）。
> **Supabase `blog_posts` 表滞后**：截至 2026-03-30 同步了 33 篇，3/31 后新发 4 篇尚未回填。
> 此表仅作快速参考，Ghost sitemap 为 single source of truth。

**已发布 Ghost（37 篇，按发布时间倒序）**：
| # | 日期 | 标题 | Ghost slug |
|---|------|------|-----------|
| 37 | 2026-04-04 | 这周，聪明人在想什么 \| Issue 004 | `great-minds-004` | ✅ Ghost + X + 微信草稿 |
| 36 | 2026-04-03 | （待补标题） | `strategy-competition-trap-2` |
| 35 | 2026-04-01 | （待补标题） | `harness-engineering-first-person` |
| 34 | 2026-03-31 | （待补标题） | `framework-transfer` |
| 33 | 2026-03-30 | MARS STATION 升级事故：AI 系统是怎样学会先想清楚再动手的 | `mars-station-upgrade` |
| 32 | 2026-03-29 | 改 prompt 没用，试试这个工程方法 | `harness-engineering` |
| 31 | 2026-03-28 | 这周，聪明人在想什么 \| Issue 003 | `great-minds-003` |
| 30 | 2026-03-27 | 我决定给每个新入职的员工配一只龙虾 | `openclaw-guide` |
| 29 | 2026-03-26 | AI时代，团队应该长什么样 | `ai-team-design` |
| 28 | 2026-03-26 | 这周，聪明人在想什么 \| Issue 002 | `great-minds-002` |
| 27 | 2026-03-26 | 从1到6：一个人怎么管一支AI团队 | `ai-team-structure` |
| 26 | 2026-03-24 | 大模型时代，最贵的错误是把 AI 当主角 | `ai-native-app-development` |
| 25 | 2026-03-23 | 手把手教程：给你的 AI 搭一套真正记得住你的记忆系统 | `ai-team-memory-system` |
| 24 | 2026-03-22 | 养一只龙虾，然后一起进化 | `ai-governance-evolution` |
| 23 | 2026-03-21 | 这周，聪明人在想什么 \| Issue 001 | `great-minds-001` |
| 22 | 2026-03-21 | Google 总结了5种 Agent Skill 设计模式 | `google-skill-patterns` |
| 21 | 2026-03-19 | AI说"完成了"的那一刻，才是真正的工作开始 | `ai-capability-verification` |
| 20 | 2026-03-18 | 你以为 AI 学会了，下次它还是那样 | `ai-memory` |
| 19 | 2026-03-18 | 在东京租到一家店，需要的不是钱，是信任 | `tokyo-leasing-trust` |
| 18 | 2026-03-16 | 龙虾不能炒股 | `not-for-quant` |
| 17 | 2026-03-15 | 从1到6：一个人怎么管一支AI团队（旧版） | `ai-team-of-six` |
| 16 | 2026-03-12 | 龙虾军团 🦞🦞🦞 两个人的 AI 协作 | `lobster-collaboration` |
| 15 | 2026-03-10 | 我把十几年咨询方法论教给了AI | `consulting-ai-first-report` |
| 14 | 2026-03-10 | 我不写日记，我写战损报告 | `ai-war-journal` |
| 1-13 | 2026-03-08 及更早 | （早期文章13篇）详见 Supabase blog_posts 表 | — |

| 33 | 2026-03-30 | MARS STATION 升级事故：AI 系统是怎样学会先想清楚再动手的 | `mars-station-upgrade` | ✅ Ghost + X |

**草稿（0 篇）**：无

**微信已发布**：
- `在东京租到一家店，需要的不是钱，是信任` ✅ 2026-03-18
- `这周，聪明人在想什么 | Issue 004` — 草稿已推送 ✅ 2026-04-06（待 Eason 发布）

**小红书已发布**：
| # | 标题 | 话题 |
|---|------|------|
| 1 | AI说"完成了"的那一刻，才是真正的工作开始 | #openclaw养龙虾 #openclaw #驯服AI |

**X 文案存档**：`personal-brand/x-post-queue.md`

### 小红书发布 SOP（2026-03-19 固化）
- 每篇文章同步发小红书图文卡片
- Mars 生成 7 张 PNG（封面+内容页+结尾）→ 发文案+图片给 Eason → Eason 手机 App 上传发布
- 卡片规范：1242×1660，封面用龙虾图，内容页全文不缩写
- 话题标签固定：**#openclaw养龙虾 #openclaw #驯服AI**（Eason 2026-03-19 确认）
- 详细规范：`personal-brand/GHOST_PUBLISHING.md` 第十三节

---

## 可用搜索能力

| 工具 | 用途 | 调用方式 |
|------|------|---------|
| **qmd** | 搜索知识库/历史内容/素材 | `qmd query "AI 创业 日本"` |
| **ddgr** | 搜索外部参考/行业趋势 | `ddgr --noua --json --num 5 "关键词"` |
| **web_fetch** | 读取具体网页内容 | `web_fetch URL` |

**工作流**：写文章前先 `qmd query` 查内部素材 → `ddgr` 补外部参考 → 生成草稿

---

## 触发命令（Eason Blog 群内使用）

| 命令 | 执行内容 |
|------|---------|
| `/brand 素材：[内容]` | 处理素材 → 生成草稿 |
| `/brand 看队列` | 列出所有待发布草稿 |
| `/brand 写 [主题]` | 主动生成该主题草稿 |
| `/brand 知识库 [链接]` | 把链接整理进知识库 |
| `/brand 周报` | 统计本周产出 |

---

## 待确认事项（截至2026-03-04）

- [x] `easonzhang.ai` 域名已注册 ✅
- [x] Ghost 自定义域名已关联 ✅（2026-03-05）
- [x] Twitter/X handle 确认：`@easontravelalot` ✅（2026-03-05）
- [x] 小红书账号开通 ✅（2026-03-19）账号名：Eason的走南闯北
- [ ] 杨国福品牌名是否在内容中点名（品牌授权）

---

*详细策略见：`personal-brand/CONTENT_STRATEGY.md` / `PIPELINE.md` / `PROFILE.md`*
