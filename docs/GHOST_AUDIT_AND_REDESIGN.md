# Ghost/Blog 工具链深度审查与重构方案

> **Issue**: [#1](https://github.com/Eason-Mars/ghost-content-tools/issues/1)
> **Author**: Mars (Claude Code)
> **Date**: 2026-04-19
> **Scope**: 审查 `scripts/` 下全部 17 个脚本，生成可直接落地为 PR 的重构方案
> **Revision**: v2（修正 v1 中线数、依赖、浏览器自动化归类等错误，补录 `publish_blog.py` / `blog_qc.sh` / 外部缺失模块分析）

---

## 0. 执行摘要（TL;DR）

### 现状
- 仓库 `scripts/` 下共 **17 个脚本**（16 个 Python + 1 个 Bash），合计 **4,249 行**（Py 4,164 + Sh 85）。
- 职责重叠严重：**Ghost→WeChat 的 HTML 转换存在 5 条独立实现**（`publish_blog.py` / `ghost_to_wechat.py` / `ghost_to_wechat_body.py` / `great_minds_ghost_to_wechat.py` / 3 个 `convert_*_wechat.py` 专用脚本），其中三个专用脚本几乎全量复制同一批 `BRAND_RED / S_P / S_H2 / S_CLOSING_*` 样式常量。
- 微信发布链路其实只有一条（`publish_wechat.py`，stdlib urllib 直连微信 API）；但 `wechat_send.py` 用 macOS `atomacos` 做 UI 自动化发消息，与公众号发布毫无关系，易被误认为同一条线。
- Ghost 发布走浏览器 **CDP + Playwright**（`ghost_auto_publish.py`），不用 Admin API Key，强依赖 OpenClaw 浏览器已登录且打开 `eason.ghost.io/ghost/`。
- 2 个脚本硬编码 **Supabase DB 密码**（`create_blog_posts_table.py:14`、`blog_posts_backfill.py:14`），属于即时安全问题。
- 3 处 import（`raphael_themes`、`supabase_writer`）在当前仓库中**不存在**：`ghost_auto_publish.py:307`、`ghost_backfill_posts.py:86`、`ghost_to_wechat_body.py:46`。要么是历史遗迹，要么需要与上游 `workspace-insight` 建立共享依赖。
- 无 `tests/`，无 `config/`（两目录空），无统一 logger，错误处理是 `print + sys.exit` 模式，重试机制全线缺失。

### 重构原则
1. **先补漏，再重构**：硬编码密钥、缺失模块、文档对不上代码等工程级问题优先于架构调整。
2. **保留 `publish_blog.py` 作为统一入口**：它已经是"Ghost 版 + 微信版生成 + QC + 推送"的 orchestrator，重构方向是给它瘦身、抽模块，而不是推倒。
3. **合并格式常量，不合并发布路径**：三个 `convert_*_wechat.py` 共享 70%+ 样式常量，应由 `wechat_formatter.py` 成为唯一来源；但 Great Minds / 标准文 / 专用组件文 的三条转换路径保留，避免过度抽象。
4. **最小落地粒度**：按"一次 PR 一个可合并粒度"切成 5 个 PR（见第 5 节），总工时 18-26h，可分周交付。

### 关键发现概览
| # | 问题 | 严重度 | PR |
|---|------|-------|-----|
| 1 | `DB_PASSWORD` 硬编码在 2 个脚本 | P0 🔴 | #1 |
| 2 | `raphael_themes` / `supabase_writer` 是外部依赖但未在本 workspace 声明 | P0 🔴 | #1 |
| 3 | 3 个 `convert_*_wechat.py` 样式常量重复 ~150 行 | P1 🟡 | #2 |
| 4 | `publish_blog.py` 内嵌的微信组件映射表与 `wechat_formatter.py` 平行演化 | P1 🟡 | #2 |
| 5 | `ghost_to_wechat.py`（regex）与 `ghost_to_wechat_body.py`（BS4+premailer）职责重叠但实现互斥 | P1 🟡 | #3 |
| 6 | 无统一 logger / 重试机制 / 错误退出码 | P2 🟢 | #4 |
| 7 | 无测试、无 `config/`、无 `.env.example` | P2 🟢 | #5 |

---

## 1. 代码库现状

### 1.1 脚本总览（按实测数据）

| # | 脚本 | 分类 | 行数 | 主要依赖 | 核心职责 |
|---|------|------|------|---------|---------|
| 1 | `publish_blog.py` | Orchestrator | **462** | bs4, subprocess | 统一发布入口（Ghost 版 + 微信版生成 + QC + 推送） |
| 2 | `publish_wechat.py` | WeChat API | 487 | urllib, PIL, hashlib | 微信公众号草稿 API：token / 图片 / 封面 / 草稿幂等更新 |
| 3 | `wechat_formatter.py` | 共享模块 | 368 | re, html | 品牌色常量 + Markdown → 微信内联 HTML |
| 4 | `ghost_auto_publish.py` | Ghost API | 367 | playwright, premailer, bs4 | CDP 连接 Ghost Admin，mobiledoc/lexical 发布 |
| 5 | `ghost_to_wechat_body.py` | 转换器 | 366 | bs4, premailer, **raphael_themes(缺)** | Ghost HTML → 微信正文（premailer inline + 12 步清洗） |
| 6 | `ghost_to_wechat.py` | 转换器 | 308 | re, wechat_formatter | Ghost HTML → 微信（regex，最轻量版） |
| 7 | `great_minds_ghost_to_wechat.py` | 专题转换 | 297 | bs4 | Great Minds 周刊模板专用：masthead / article / other 三段式 |
| 8 | `xhs_card_ai_capability.py` | XHS 卡片 | 279 | - | 生成 1242×1660 小红书 HTML 卡片（7 张）供 Playwright 截图 |
| 9 | `convert_ai_memory_wechat.py` | 专用转换 | 275 | bs4, wechat_formatter | AI Memory 文：step-card/code-block/analogy/alert-grid 专用转换 |
| 10 | `convert_leasing_wechat.py` | 专用转换 | 169 | - | Leasing 文：wall-card / method-list / quote-block 专用转换 |
| 11 | `wechat_send.py` | macOS 自动化 | 179 | atomacos | **给个人微信发消息**（非公众号），UI 自动化 |
| 12 | `convert_ai_capability_wechat.py` | 专用转换 | 147 | - | AI Capability 文：qa-block / insight-box 专用转换 |
| 13 | `ghost_backfill_posts.py` | 运维 | 146 | playwright, **supabase_writer(缺)** | 从 Ghost Admin 回填历史文到 Supabase `content_posts` |
| 14 | `blog_posts_backfill.py` | 运维 | 112 | psycopg2 | 手写 19 篇文的 metadata 插入 `blog_posts` 表 |
| 15 | `create_blog_posts_table.py` | DDL | 103 | psycopg2 | 建表：`blog_posts` schema + trigger |
| 16 | `great_minds_wechat_inline.py` | 专题转换 | 99 | premailer, bs4 | 展开 CSS 变量 + premailer inline（Great Minds 后处理） |
| 17 | `blog_qc.sh` | Bash QC | 85 | grep, sed | 推送前检查：模板结构 / 签名 / 乱码 / 禁区词 |

**总计：4,249 行。** 其中"Ghost→微信"相关（第 1/3/5/6/7/9/10/12/16 号）占 **2,690 行（63%）**，是本仓库真正的复杂度中心。

### 1.2 五大分类

```
┌──────────────────────────────────────────────────────────────────┐
│  A. Orchestrator (462 行 / 1 脚本)                              │
│     publish_blog.py                                              │
│     职责：统一入口，调用 ghost_auto_publish + publish_wechat     │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│  B. 平台发布器 (1,033 行 / 3 脚本)                              │
│     ghost_auto_publish.py   ← Ghost，Playwright CDP              │
│     publish_wechat.py       ← WeChat，urllib + draft API         │
│     wechat_send.py          ← 个人微信 UI，atomacos（独立）      │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│  C. HTML 转换器 (1,562 行 / 6 脚本) — 最冗余的地方              │
│     wechat_formatter.py              ← MD → WeChat（品牌常量）   │
│     ghost_to_wechat.py               ← HTML → WeChat（regex）   │
│     ghost_to_wechat_body.py          ← HTML → WeChat（bs4+主题） │
│     convert_ai_capability_wechat.py  ← 专用（qa-block）         │
│     convert_ai_memory_wechat.py      ← 专用（step-card/code）   │
│     convert_leasing_wechat.py        ← 专用（wall-card）        │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│  D. 专题周刊 (396 行 / 2 脚本)                                   │
│     great_minds_ghost_to_wechat.py   ← Great Minds 三段式模板   │
│     great_minds_wechat_inline.py     ← CSS var 展开 + premailer  │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│  E. 运维 & DDL & XHS (725 行 / 5 脚本)                          │
│     create_blog_posts_table.py   ← 建表                          │
│     blog_posts_backfill.py       ← 手写数据插入                 │
│     ghost_backfill_posts.py      ← 从 Ghost 回填到 Supabase     │
│     blog_qc.sh                   ← Bash QC                       │
│     xhs_card_ai_capability.py    ← 生成 XHS 卡片 HTML           │
└──────────────────────────────────────────────────────────────────┘
```

### 1.3 工作流（实际调用路径，不是文档想象的路径）

```
                        Eason 写 source HTML (带 .hero / .page / .closing / .x-box)
                                          │
                                          ▼
                        ┌────────────────────────────────────┐
                        │    scripts/publish_blog.py         │
                        │    <source.html> --slug <slug>     │
                        │    [--ghost] [--wechat] [--all]    │
                        └────────────────────────────────────┘
                                 │                      │
             ┌───────────────────┤                      ├──────────────────────┐
             │ --ghost           │                      │ --wechat             │
             ▼                   ▼                      ▼                      ▼
  1. generate_ghost_html()  2. qc_ghost()      1. generate_wechat_html()  2. qc_wechat()
     ├─ 去 nav/x-box         ├─ 无 x-box         ├─ DOM 组件映射：          ├─ 有 DOCTYPE
     ├─ 提取 .hero/.page     ├─ 有 "我叫 Eason"  │   wall-card/method-list  ├─ 有签名
     └─ 外挂 site-footer     └─ 无 DOCTYPE       │   highlight-box/quote    └─ 无 x-box
                                                  └─ 写 *.wechat.html
                                                                 │
             ┌───────────────────┐                                ▼
             │ Ghost 推送路径    │                   ┌────────────────────────┐
             ▼                   │                   │   publish_wechat.py    │
  ensure_ghost_browser()         │                   │   urllib → 微信 API    │
  （openclaw browser start）    │                   └────────────────────────┘
                                  │                                │
                                  ▼                                ▼
                   subprocess ghost_auto_publish.py         1. token 缓存（/tmp）
                          │                                  2. 封面上传（.wechat_cache）
                          ▼                                  3. 正文图片 base64/本地
                   Playwright connect_over_cdp(18800)        4. draft/add or draft/update
                   ├─ premailer inline                       5. 回写 draft_media_id
                   ├─ 去 x-box/site-footer                       到 .wechat_cache.json
                   ├─ 抽 base64 图 → 上传到 Ghost
                   ├─ 构建 mobiledoc 或 lexical
                   ├─ POST /ghost/api/admin/posts/
                   ├─ supabase_writer.write_content_post  ← 缺模块
                   └─ 读回 post.html 做验证
```

**真实使用节奏（据 `GHOST_PUBLISHING.md` §一）：**
1. InSight（外部 workspace）产出 `*-ghost.html`
2. Mars 过 `blog_qc.sh` 或 `publish_blog.py --dry-run`
3. `publish_blog.py --slug --all` 同时推 Ghost + 微信草稿
4. Eason 在后台人工点发布（**永远不自动 publish**；所有脚本默认 `--draft`）
5. Mars 起 X 文案 → `x-post-queue.md` → Eason 自发
6. Mars 更新 `CONTEXT_EasonBlog.md` 状态表

### 1.4 依赖矩阵

| 依赖 | 性质 | 使用脚本 | 备注 |
|------|------|---------|------|
| `beautifulsoup4` | pip | publish_blog / ghost_to_wechat_body / great_minds_* / convert_ai_memory / ghost_auto_publish | 5+ 处 |
| `premailer` | pip | ghost_auto_publish, ghost_to_wechat_body, great_minds_wechat_inline | CSS inline |
| `playwright` | pip | ghost_auto_publish, ghost_backfill_posts | CDP 连 OpenClaw 浏览器 |
| `psycopg2` | pip | create_blog_posts_table, blog_posts_backfill | Supabase 直连 |
| `atomacos` | pip（macOS） | wechat_send | 需辅助功能权限 |
| `PIL/Pillow` | pip | publish_wechat | 生成默认封面 |
| `urllib.*` | stdlib | publish_wechat | **非 requests** |
| `subprocess` | stdlib | publish_blog, ghost_to_wechat | 调另一个脚本 |
| `raphael_themes` | **缺失** | ghost_to_wechat_body | `from raphael_themes import get_theme, DEFAULT_THEME` |
| `supabase_writer` | **缺失** | ghost_auto_publish, ghost_backfill_posts | `from supabase_writer import write_content_post` |

**外部服务 / 凭证：**
| 服务 | 认证方式 | 源 | 风险 |
|------|---------|-----|------|
| Ghost Admin | 浏览器 session via CDP | OpenClaw browser 18800 端口 | 浏览器未登录 → 全线失败 |
| WeChat OA | `WECHAT_APP_ID` / `WECHAT_APP_SECRET` | `../.env.wechat` | 未在仓库 → 各端自行准备 |
| Supabase | `DB_PASSWORD` **硬编码** | 脚本源码 | 🔴 立即整改 |
| WeChat 素材库 | access_token（2h TTL） | `/tmp/wechat_token.json` 缓存 | 正常 |

### 1.5 数据持久化

| 文件 | 位置 | 写入者 | 用途 |
|------|------|--------|------|
| `.wechat_cache.json` | `<article_dir>/` | publish_wechat | `draft_media_id` / `thumb_media_id` / `images[]` |
| `/tmp/wechat_token.json` | 全局 | publish_wechat | access_token + expires_at |
| `blog_posts` 表 | Supabase | backfill 脚本 | 历史 19 篇的 slug/title/status |
| `content_posts` 表 | Supabase | `supabase_writer`（缺） | Ghost 推送后回写（best-effort） |
| `/tmp/ghost_upload_{i}.jpg` | 本地 | ghost_auto_publish | 图片上传临时文件 |

---

## 2. 工作流详拆

### 2.1 日常发文（占 80%+ 使用场景）

```bash
# 在 workspace-insight 产出 ghost 版 HTML 之后
python3 scripts/publish_blog.py personal-brand/content/drafts/xyz-ghost.html \
  --slug xyz \
  --all \
  [--update-ghost POST_ID] [--update-wechat MEDIA_ID]
```

**内部 12 步：**
1. 读取 source HTML
2. BeautifulSoup 解析，提取 `<h1>` 作为标题（或 `--title`）
3. 生成 Ghost 版（去 nav / x-box / site-footer，保留 `<style>`）
4. `qc_ghost()` — 检查 6 项禁止 + 2 项必须
5. `ensure_ghost_browser()` — HTTP GET `http://127.0.0.1:18800/json`，失败则 `openclaw browser start`
6. `subprocess` 调用 `ghost_auto_publish.py` → Playwright 连 CDP → premailer inline → mobiledoc HTML Card → `POST /ghost/api/admin/posts/`
7. 解析返回 `ID:` / `URL:` → 回到 orchestrator
8. 生成微信版（`_wechat_node()` 递归 DOM，组件映射表：wall-card / method-list / highlight-box / quote-block / closing / lead / p / h2 / h3 / blockquote / ul-ol）
9. `qc_wechat()` — 检查 4 项禁止 + 3 项必须
10. `subprocess` 调用 `publish_wechat.py --title --author` → 走微信 draft API
11. 从 stdout 捕获 `Draft created:` / `Draft updated:` 的 media_id
12. 打印 JSON 汇总

### 2.2 Great Minds 周刊（每周一次）

```bash
# 每期手动改 great_minds_ghost_to_wechat.py 里的：
#   ISSUE_NUM = "004"
#   ISSUE_DATE = "2026-04-04"
#   html = Path('.../great-minds-004-ghost.html')
python3 scripts/great_minds_ghost_to_wechat.py
# → /tmp/great-minds-004-wechat-body.html
```

注意：这个脚本**没有 argparse**，所有参数在源码里改。它输出"正文片段"（非完整 HTML），需要再跑 `great_minds_wechat_inline.py` 或在微信编辑器里手贴。模块入口是 module-level 代码（非 `main()`），导入即执行，无法作为库引用。

### 2.3 特殊组件文（历史累积）

当某篇文里出现 `ghost_to_wechat.py` 不支持的自定义组件（wall-card / step-card / qa-block / ...），就写一个 `convert_<slug>_wechat.py`：
- `convert_leasing_wechat.py` — wall-card, method-list, quote-block
- `convert_ai_capability_wechat.py` — qa-block, insight-box
- `convert_ai_memory_wechat.py` — step-card, code-block, analogy, alert-grid, faq-item（此脚本 **正确** 从 `wechat_formatter import S_*` 复用样式常量）

**现状问题：** `publish_blog.py` 的 `_wechat_node()` 已经把 wall-card / method-list / highlight-box / quote-block 映射好了，与 `convert_leasing_wechat.py` 功能重叠。但是——
- `publish_blog.py` 的映射是 DOM-based，复用给 Leasing 理论上可行但没人迁移过
- 其他两个专用脚本涉及的组件（qa-block / step-card / code-block）**没有**进 `publish_blog.py` 的映射表

结果是新文来了，Mars 先看组件类型：
1. 无自定义组件 → 用 `publish_blog.py`
2. 有自定义组件但都在 `_wechat_node()` 里 → 用 `publish_blog.py`
3. 有新组件 → 写专用 `convert_<slug>_wechat.py`

这是一个**组件注册表**的缺失。

### 2.4 XHS 卡片

```bash
python3 scripts/xhs_card_ai_capability.py
# → 输出 7 个 HTML 到硬编码路径 /Users/dljapan/.openclaw/workspace/personal-brand/content/drafts/2026-03-19-ai-memory/xhs/
# → 外部用 Playwright 截图成 1242×1660 PNG
# → Eason 手机端手动发
```

与其他脚本一样没有 argparse，换主题要改源码。

### 2.5 触发方式与错误处理

- **全部手动触发**：无 cron / 无 webhook / 无 Ghost 发布事件监听
- **错误恢复**：`publish_wechat.py` 的 draft/update 如果失败会回退到 draft/add（见 L459），是唯一一处自动 fallback
- **重试**：全部脚本都没有重试机制
- **幂等性**：
  - Ghost：靠 `--update POST_ID` 显式传入（orchestrator `publish_blog.py` 从未自动获取 post_id，需要人工记）
  - 微信：靠 `.wechat_cache.json` 存 `draft_media_id`，自动复用
  - Supabase：`ON CONFLICT slug DO NOTHING`

---

## 3. 代码质量评估

### 3.1 评分矩阵（0-5 分，5 最好）

| 维度 | Orchestrator | 发布器 | 转换器 | 专题周刊 | 运维/XHS |
|------|:-----------:|:-----:|:-----:|:-------:|:-------:|
| 错误处理 | 3 | 3 | 1 | 1 | 2 |
| 日志记录 | 2 | 2 | 1 | 1 | 2 |
| 配置管理 | 2 | 3 | 1 | 0 | 0 |
| 可测试性 | 1 | 1 | 1 | 0 | 1 |
| 文档完整 | 3 | 4 | 2 | 3 | 2 |
| API 设计 | 3 | 3 | 2 | 0 | 2 |
| **总分** | 14/30 | 16/30 | 8/30 | 5/30 | 9/30 |

### 3.2 评分证据

**错误处理**
- ✅ `publish_wechat.py` 的 `update_draft` 失败 → None → 调用方 fallback 到 `create_draft`（L456-466）
- ✅ `ghost_auto_publish.py` 尝试 `from supabase_writer` 并 try/except（L304-323）
- ❌ `convert_*_wechat.py` 三件套：全程零 try/except，无输入校验
- ❌ `great_minds_ghost_to_wechat.py`：零异常处理，`Path(...).read_text()` 失败直接崩
- ❌ 所有脚本都是 `print("❌ ...") + sys.exit(1)`，没有退出码分级（容错 vs 不可恢复）

**日志**
- 全部是 emoji print（✅ ❌ ⚠️ 🔍 📤 📦 🟢 📋 🚀 🎉），没有一条用 `logging` 库
- 没有 log level 控制，调试时只能靠注释 print
- 没有日志文件，stdout 一断就丢

**配置**
- ✅ `publish_wechat.py` 用 `../.env.wechat` 读 APP_ID/SECRET
- 🔴 `create_blog_posts_table.py:10-14` 和 `blog_posts_backfill.py:10-14` 硬编码 DB_PASSWORD
- 🔴 `xhs_card_ai_capability.py:9` 硬编码绝对路径 `/Users/dljapan/.openclaw/workspace/...`
- 🔴 `great_minds_ghost_to_wechat.py:160` 硬编码 `/Users/dljapan/.openclaw/workspace/tmp/great-minds-004-ghost.html`
- 🔴 多处硬编码 Ghost URL `https://eason.ghost.io/ghost/` / CDP 端口 18800
- `config/` 目录存在但**完全为空**

**测试**
- `tests/` 目录存在但**完全为空**
- 没有一处 `assert`、没有 pytest 配置、没有 CI
- `publish_blog.py` 里的 `qc_ghost()` / `qc_wechat()` 是关键词计数，算"检查"不算"测试"
- `blog_qc.sh` 同上

**文档**
- ✅ `docs/GHOST_PUBLISHING.md` 416 行，SOP 非常详细，且有 11 条"踩过的坑"
- ✅ `docs/WECHAT_STANDARD.md` 172 行，样式规范完整
- ❌ 没有 `CHANGELOG.md`、没有每个脚本的入口级 `--help` 自检、没有 `README` 描述依赖安装
- ❌ `AGENTS.md` 写"项目状态：待更新"

**API 设计**
- ✅ `publish_blog.py` 的 `_wechat_node(tag)` 递归 DOM 路径清晰
- ✅ `publish_wechat.py` 把 cache / token / upload / draft 分得较干净
- ❌ `great_minds_ghost_to_wechat.py` 是一个 **module-level 脚本**——import 即执行，没有函数封装主流程
- ❌ 三个 `convert_*_wechat.py` 全都是 `wechat_html()` 一个巨型函数

### 3.3 复杂度热点

```
Top 5 最值得瘦身的文件
  487 publish_wechat.py        ← 可分 3 模块：auth / upload / draft
  462 publish_blog.py          ← _wechat_node 是主要复杂度
  368 wechat_formatter.py      ← 设计已经较好，但被下游重复拷贝
  367 ghost_auto_publish.py    ← JS 评估字符串可抽组件
  366 ghost_to_wechat_body.py  ← 12 步清洗可拆成有序函数链
```

### 3.4 重复代码热点

| 常量/逻辑 | 出现于 |
|-----------|--------|
| `BRAND_RED = '#8B3A2A'` | wechat_formatter / publish_blog / ghost_to_wechat / convert_ai_capability / convert_leasing / convert_ai_memory（via import）/ great_minds / xhs |
| `FF = '-apple-system,"PingFang SC",...'` | 同上 7 处 |
| `S_P / S_H2 / S_BQ / S_LEAD / S_CLOSING_*` | convert_ai_capability / convert_leasing 里几乎完整复制一遍 wechat_formatter 的常量 |
| 签名 `我叫 Eason + creds + tagline` | publish_blog / wechat_formatter / convert_ai_capability / convert_leasing / convert_ai_memory 都各自硬编码 |
| Ghost HTML 组件映射（wall-card/method-list/...） | publish_blog._wechat_node 与 convert_leasing 完整重合 |
| premailer inline 逻辑 | ghost_auto_publish / ghost_to_wechat_body / great_minds_wechat_inline 3 处重复 |

---

## 4. 重构方案

为避免"只提一个完美设计但落不了地"，下面给 3 个从保守到激进的方案，再给推荐组合。

### 方案 A（保守）：不改架构，先补漏

**动作：**
1. 把 `DB_PASSWORD` / 硬编码绝对路径 / Ghost URL 挪进 `config/.env.example`
2. 补 `raphael_themes.py`（从 workspace-insight 拷贝进来或删掉该 import）
3. 补 `supabase_writer.py` 同上
4. 给 `great_minds_ghost_to_wechat.py` 加 argparse，让 ISSUE_NUM / DATE / 输入路径可传参
5. 给 `convert_*_wechat.py` 全部改成 `from wechat_formatter import *`（只保留"专用组件"的映射）

**成本：** 1 个 PR，4-6h
**受益：** 解决 P0 安全 + 保证每个脚本能独立跑

### 方案 B（中档）：组件注册表 + 事件驱动

**动作：**

**B1. 组件注册表**
```python
# scripts/wechat_components.py
from typing import Callable, Dict
from bs4 import Tag

ConverterFn = Callable[[Tag], str]
REGISTRY: Dict[str, ConverterFn] = {}

def register(class_name: str):
    def decorator(fn: ConverterFn):
        REGISTRY[class_name] = fn
        return fn
    return decorator

@register('wall-card')
def _wall_card(tag: Tag) -> str: ...

@register('step-card')
def _step_card(tag: Tag) -> str: ...

@register('qa-block')
def _qa_block(tag: Tag) -> str: ...
```

让 `publish_blog._wechat_node()` 先查 REGISTRY，再 fallback 到标准标签处理。三个 `convert_*_wechat.py` 被替换成对 REGISTRY 的贡献。

**B2. Ghost 发布后钩子**
`ghost_auto_publish.py` 发布成功后，检查环境变量 `AUTO_PUSH_WECHAT=1` → 直接调用 `publish_wechat.py`，不用每次手敲 `--all`。但保留默认值为空（Eason 审稿习惯不变）。

**B3. 统一 logger**
```python
# scripts/logger.py
import logging, sys
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers: return logger
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(logging.Formatter('%(asctime)s [%(name)s] %(levelname)s %(message)s'))
    logger.addHandler(h)
    logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))
    return logger
```

所有 `print("❌ ...")` 逐步替换为 `logger.error(...)`；emoji 可以保留，但日志级别要分开。

**成本：** 3 个 PR，10-14h
**受益：** 专用转换脚本从 3 个减到 0（组件全部进 REGISTRY）；约减 400 行重复代码

### 方案 C（激进）：`src/` 包化 + pydantic Settings + pytest

**动作：**
```
ghost-content-tools/
├── src/
│   ├── config.py              # pydantic BaseSettings
│   ├── logger.py
│   ├── publishers/
│   │   ├── ghost.py           # 从 ghost_auto_publish.py 抽
│   │   └── wechat.py          # 从 publish_wechat.py 抽
│   ├── formatters/
│   │   ├── constants.py       # 单一常量来源
│   │   ├── wechat_components.py  # REGISTRY
│   │   └── ghost_to_wechat.py # 合并 regex / bs4 两个实现
│   └── cli/
│       ├── publish_blog.py    # CLI 壳
│       └── publish_great_minds.py
├── tests/
│   ├── test_formatters/
│   ├── test_publishers/
│   └── fixtures/
│       ├── sample-ghost.html
│       └── expected-wechat.html
├── config/
│   ├── .env.example
│   └── settings.yaml
└── scripts/                   # 薄壳，只调 src/
```

**成本：** 5-7 个 PR，25-35h
**风险：** 需要同时修改 `AGENTS.md` / `GHOST_PUBLISHING.md` 里的命令调用，Mars 的 SOP 要全部复习一遍；短期内发文节奏可能受影响

### 推荐组合：A + B，C 推迟

**理由：**
1. P0 问题（硬编码密钥、缺失模块）必须先处理——走 A
2. `convert_*_wechat.py` 的重复是真痛点，组件注册表能真正减少代码——走 B
3. `src/` 包化本身不能让发文更快、更稳；且会对 Mars 的 SOP 引入一次性迁移成本——暂缓 C
4. 等 B 稳定后，如果团队增加（真有第二个开发者），再考虑 C

推荐落地顺序：

```
PR #1 (P0, 4h)   — 安全清理 + 缺失模块补位
PR #2 (P1, 4h)   — 合并样式常量（convert_*_wechat.py 瘦身）
PR #3 (P1, 6h)   — wechat_components.py REGISTRY + publish_blog 迁移
PR #4 (P2, 4h)   — 统一 logger + 重试装饰器
PR #5 (P2, 6h)   — pytest 框架 + 转换器黄金测试
—— 约 24h，可分 3 周交付 ——
```

---

## 5. PR 清单（可直接落地）

### PR #1：P0 安全 + 缺失模块补位

**Title:** `fix: remove hardcoded DB credentials and resolve missing module imports`

**Scope:**
- [ ] 新增 `config/.env.example`，列出 `SUPABASE_DB_URL` / `WECHAT_APP_ID` / `WECHAT_APP_SECRET` / `GHOST_ADMIN_URL` / `GHOST_CDP_PORT` / `XHS_OUTPUT_DIR`
- [ ] 新增 `scripts/_env.py` 导出 `load_env()`，读取 `config/.env`（优先）或 `../.env.wechat`（向后兼容）
- [ ] `create_blog_posts_table.py` 和 `blog_posts_backfill.py` 改用 `load_env()`；当前硬编码密码移至 `.env`（加入 `.gitignore`）
- [ ] 抉择：`raphael_themes` 是保留还是移除
  - 若保留：新建 `scripts/raphael_themes.py`，从 `workspace-insight` 复制 `eason` 主题定义
  - 若移除：`ghost_to_wechat_body.py` 改用 `wechat_formatter` 常量
- [ ] 抉择：`supabase_writer` 同上
  - 若保留：新建 `scripts/supabase_writer.py`，实现 `write_content_post(record)`
  - 若移除：删掉 `ghost_auto_publish.py` L304-323 那段 best-effort 写 DB 的代码
- [ ] `AGENTS.md` 更新"项目状态"小节，列出环境变量要求

**验收：**
- `git grep -n "DB_PASSWORD = \"H6z"` 结果为 0
- `python3 scripts/ghost_auto_publish.py --help` 不再 ImportError
- `python3 scripts/ghost_to_wechat_body.py a b` 不再 ImportError

**工时估算：** 3-4h

---

### PR #2：合并样式常量

**Title:** `refactor: make wechat_formatter the single source of brand constants`

**Scope:**
- [ ] `convert_ai_capability_wechat.py` 顶部重复定义的 `BRAND_RED / FF / P / H2 / STRONG / LEAD / BQ / CLOSING_*` 替换为 `from wechat_formatter import ...`
- [ ] `convert_leasing_wechat.py` 同上
- [ ] `publish_blog.py` 顶部的品牌常量（L27-57）同样改为 `from wechat_formatter import ...`
- [ ] `ghost_to_wechat.py` 删除脚本内部自定义常量，统一从 `wechat_formatter` 拿
- [ ] `wechat_formatter.py` 新增缺失的几个（`S_WALL_*` / `S_METHOD_*` / `S_QA_*` / `S_INSIGHT_*` / `S_CLOSING_DARK_*`）
- [ ] 签名文本（我叫 Eason + creds + tagline）抽成 `wechat_formatter.CLOSING_HTML`，所有脚本用它

**验收：**
- `grep -c "BRAND_RED  = '#8B3A2A'" scripts/*.py` 只在 `wechat_formatter.py` 出现一次
- `grep -c "我叫 Eason" scripts/*.py` ≤ 2（formatter + publish_blog 的 qc 检查）

**工时估算：** 3-4h

---

### PR #3：组件注册表

**Title:** `feat: wechat_components registry replaces per-article convert scripts`

**Scope:**
- [ ] 新增 `scripts/wechat_components.py`，暴露 `REGISTRY` 和 `@register('<class>')` 装饰器
- [ ] 把 `publish_blog._wechat_node()` 的 wall-card / method-list / highlight-box / quote-block / closing / lead 迁移进去
- [ ] 把 `convert_ai_capability_wechat.py` 的 qa-block / insight-box 迁移进去
- [ ] 把 `convert_ai_memory_wechat.py` 的 step-card / code-block / analogy / alert-grid / faq-item 迁移进去
- [ ] `publish_blog._wechat_node()` 改成"先查 REGISTRY，再 fallback 到标签处理"
- [ ] `convert_*_wechat.py` 3 个脚本加一个废弃注释 `# DEPRECATED: use publish_blog.py`，但保留能跑
- [ ] `docs/GHOST_PUBLISHING.md` §十二"专用组件判断标准"更新为"先查 wechat_components.REGISTRY"

**验收：**
- 对 `japan-restaurant-leasing-trust.html`、`ai-capability-verification.html`、`ai-team-memory-system.html` 这 3 篇历史文跑 `publish_blog.py --dry-run`，生成的 `.wechat.html` 与旧 `convert_*` 脚本输出 diff 为空或仅差空白

**工时估算：** 5-7h

---

### PR #4：统一 logger + 重试

**Title:** `feat: introduce shared logger and retry decorator`

**Scope:**
- [ ] 新增 `scripts/_logger.py`，`get_logger(name)` 按上面方案 B3 实现
- [ ] 新增 `scripts/_retry.py`，`@retry(max_attempts=3, backoff=2.0, exceptions=(URLError, TimeoutError))` 装饰器
- [ ] 给 `publish_wechat.py` 的 `get_access_token` / `multipart_upload` / `create_draft` / `update_draft` 加 `@retry`
- [ ] 给 `ghost_auto_publish.upload_file_to_ghost` 加 `@retry`
- [ ] 逐步把 orchestrator + 发布器的关键 `print` 替换为 logger（保留 emoji 作为 formatter 前缀）

**验收：**
- 临时断网后重跑 `publish_wechat.py`，重试 3 次后再失败
- `LOG_LEVEL=DEBUG python3 publish_blog.py ... --dry-run` 能看到 DEBUG 级别细节

**工时估算：** 3-4h

---

### PR #5：pytest 框架 + 黄金测试

**Title:** `test: add pytest framework and golden-file tests for converters`

**Scope:**
- [ ] 新增 `pytest.ini` / `requirements-dev.txt`
- [ ] 新增 `tests/fixtures/`，存入 3 个 source HTML + 3 个 expected wechat HTML + 3 个 expected ghost HTML（从历史发文里取）
- [ ] 新增 `tests/test_publish_blog.py`：对每个 fixture 跑 `generate_ghost_html` / `generate_wechat_html`，和 expected 做 normalize 后字符串比对
- [ ] 新增 `tests/test_wechat_components.py`：对 REGISTRY 里每个 converter 跑单元测试
- [ ] 新增 `tests/test_qc.py`：对 `qc_ghost` / `qc_wechat` 的正反例
- [ ] `.github/workflows/ci.yml`：push 到 PR 时跑 `pytest`

**验收：**
- `pytest` 绿灯，覆盖 orchestrator + 组件 REGISTRY + qc
- `coverage` >= 50%（首轮目标，不求 80%+）

**工时估算：** 5-6h

---

## 6. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| PR #3 合并后 convert_* 输出 diff 不为 0 | 历史文重新生成会变样 | 3 篇黄金样本在 PR #3 内先建 fixtures，diff 为 0 再合 |
| `raphael_themes` 抉择错误 | `ghost_to_wechat_body` 长期断路 | PR #1 里明确给出两条路，让 Eason 在 PR 里选 |
| WeChat API 凭证被其他脚本偷读 | `../.env.wechat` 路径硬编码 | PR #1 里同时提供 `config/.env`（优先级更高）；旧路径保留兼容 |
| 统一 logger 改变 stdout 格式 | `publish_blog.py` 用 regex 解析子进程 stdout | PR #4 不改子进程输出格式，logger 用 stderr |
| `.wechat_cache.json` 在包重构后路径失效 | 发文幂等性丢失 | 所有 cache 路径迁移前保留 copy-on-write |

---

## 7. 验收标准

- [ ] P0：无任何脚本包含明文 `DB_PASSWORD`；所有 import 可 resolve
- [ ] P1：专用 `convert_*_wechat.py` 输出与 `publish_blog.py --dry-run` 完全一致
- [ ] P1：`grep -c "BRAND_RED" scripts/*.py` 仅 `wechat_formatter.py` 有定义
- [ ] P2：`pytest` 至少 20 个测试，关键路径覆盖率 ≥50%
- [ ] P2：所有脚本支持 `LOG_LEVEL` 环境变量
- [ ] 文档：`GHOST_PUBLISHING.md` / `WECHAT_STANDARD.md` / `AGENTS.md` 命令示例与实际脚本参数一致
- [ ] 回归：3 篇历史样本重新发布生成的 HTML diff 为 0（或仅空白差异）

---

## 8. 时间与里程碑

| PR | 工时 | 前置 | 可独立合 |
|----|------|------|---------|
| #1 安全清理 | 3-4h | — | ✅ |
| #2 常量合并 | 3-4h | #1 | ✅ |
| #3 组件注册表 | 5-7h | #2 | ✅ |
| #4 logger + 重试 | 3-4h | #1 | ✅（独立于 #2/#3） |
| #5 pytest | 5-6h | #3 | ✅ |
| **合计** | **19-25h** | | |

建议节奏：
- 第 1 周：#1 + #2（8h 内收工）
- 第 2 周：#3 + #4（10h）
- 第 3 周：#5（6h）

---

## 附录 A：脚本处置清单

| 脚本 | 处置 | 去向 |
|------|------|------|
| `publish_blog.py` | 保留 + 瘦身 | 维持 CLI 入口；内部 `_wechat_node` 改调 REGISTRY |
| `publish_wechat.py` | 保留 + 加 retry | 维持 CLI；加 `@retry` |
| `ghost_auto_publish.py` | 保留 + 补 `supabase_writer` 或删 best-effort DB | — |
| `wechat_formatter.py` | 保留 + 扩充 | 成为唯一常量来源 |
| `ghost_to_wechat.py` | **标记 DEPRECATED** | 引导用 `publish_blog.py`；保留运行 |
| `ghost_to_wechat_body.py` | 保留 | premailer 路径仍有价值（外部 HTML 不走 publish_blog 时） |
| `great_minds_ghost_to_wechat.py` | 重构 | 加 argparse，抽 `main()`，样式常量从 formatter 拿 |
| `great_minds_wechat_inline.py` | 保留 | premailer 后处理独立工具 |
| `wechat_send.py` | 保留 | 独立工具（个人微信 UI 自动化），单独文档一行说明 |
| `xhs_card_ai_capability.py` | 参数化 | OUT_DIR 改 env / argparse |
| `convert_ai_capability_wechat.py` | **DEPRECATED** | 组件进 REGISTRY 后删 |
| `convert_ai_memory_wechat.py` | **DEPRECATED** | 同上 |
| `convert_leasing_wechat.py` | **DEPRECATED** | 同上 |
| `blog_posts_backfill.py` | 保留 + 去硬编码密码 | 运维一次性工具 |
| `create_blog_posts_table.py` | 保留 + 去硬编码密码 | DDL 一次性 |
| `ghost_backfill_posts.py` | 保留 + 补 `supabase_writer` | — |
| `blog_qc.sh` | 保留 | 给非 Python 调用方用 |

## 附录 B：测试 fixtures 候选

从 `content/published/` 选 3 篇代表性文章作为黄金样本：

1. **标准文**（只用基础组件）
   - 文：`ai-killed-khamenei.html` 之类
   - 覆盖：p / h2 / blockquote / ul / hero / closing
2. **复合组件文**（测 REGISTRY）
   - 文：`japan-restaurant-leasing-trust.html`
   - 覆盖：wall-card / method-list / quote-block
3. **代码密集文**（测 pre/code 兜底）
   - 文：`ai-team-memory-system.html`
   - 覆盖：step-card / pre.code-block / analogy / alert-grid

---

## 附录 C：已知坑（来自 GHOST_PUBLISHING.md §十 与 `great_minds_ghost_to_wechat.py` 注释）

在重构中**必须**保留或通过测试验证不退化的历史修复：

1. 微信 `<img>` 字体 family 用单引号（双引号触发样式截断 bug）—— `ghost_to_wechat_body.convert_inline_code`
2. `atob()` 不能直接解 base64 中文 —— `ghost_auto_publish` 用 `Uint8Array + TextDecoder`
3. 微信不支持 `ul/li` —— `ghost_to_wechat_body.convert_lists` 把它们展开为 `section + p`
4. 微信不支持 flex —— `ghost_to_wechat_body.flex_to_table`
5. 微信 `<code>`/`<pre>` 需要换 `section` 纯文字
6. Great Minds 的 FONT 常量必须单引号包裹字体名
7. 图片 hash 必须完整内容 hash（非前 200 字符），否则 JPEG 文件头碰撞
8. `?source=html` 不能用 —— mobiledoc/lexical HTML Card
9. `updated_at` 必须带回传给 Ghost PUT 接口，否则冲突
10. 签名必须硬编码（历史已违反 5+ 次）

这些在 PR #5 的测试里应该有正向断言。

---

## 附录 D：发布后验证清单（来自 `GHOST_PUBLISHING.md §六A`）

每次 Ghost 推送成功后，orchestrator 应当自动或提示人工做：

- [ ] web_fetch 实际 URL，确认 `我叫 Eason` 在页面
- [ ] 页面不含 `Deloitte / ARTI / AMI / 杨国福 / Eason Zhang (签名)`
- [ ] 后台只有一条该 slug 记录，无 `-2` 后缀重复

**当前 `publish_blog.py` 只打印 `Ghost 完成 → 预览: URL`，没有做这一步 web_fetch。** 这应当在 PR #3 或 #4 里补上（`requests.get(url)` + 关键词检查）。

---

## 附录 E：环境准备（供 `config/.env.example` 模板）

```bash
# Ghost Admin (via OpenClaw browser CDP)
GHOST_ADMIN_URL=https://eason.ghost.io/ghost/
GHOST_CDP_PORT=18800

# WeChat Official Account
WECHAT_APP_ID=xxx
WECHAT_APP_SECRET=xxx

# Supabase
SUPABASE_DB_HOST=db.xxx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=xxx

# Logging
LOG_LEVEL=INFO

# XHS output
XHS_OUTPUT_DIR=./personal-brand/content/drafts
```

---

*本文档生成自 2026-04-19 对 scripts/ 目录全量审查。后续每完成一个 PR 同步更新第 5/8 节的完成标记。*
