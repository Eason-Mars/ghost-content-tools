# Ghost 发布操作规范（SOP）

> 所有博客文章发布到 Ghost 必须严格遵循本文档。
> 每次发布前过一遍 **发布前检查清单**，不允许凭记忆操作。
> 最后更新：2026-03-09

---

## 一、完整发布链路

```
InSight 写草稿（source HTML）
  ↓
Mars QC → 过第六节检查清单
  ↓
Mars 发 preview 给 Eason 确认
  ↓ Eason 说 OK
Mars 执行统一发布脚本：
  python3 scripts/publish_blog.py <source.html> --slug <slug> --all
  ↓ 自动完成：Ghost版生成→QC→推草稿 + 微信版生成→QC→推草稿
Mars 发 Ghost 预览 URL 给 Eason 验证渲染
  ↓ Eason 在 Ghost 后台 + 微信后台点发布
Mars 准备 X 文案 + 短链接
  ↓ 追加到 x-post-queue.md
Mars 发文案给 Eason → Eason 发 X
  ↓
Mars 更新 CONTEXT_EasonBlog.md 状态表（Ghost ✅ 微信 ✅ X ✅）
```

**统一发布脚本**：`scripts/publish_blog.py`
```bash
# 首次发布（Ghost + 微信同时推）
python3 scripts/publish_blog.py <source.html> --slug <slug> --all

# 仅推 Ghost
python3 scripts/publish_blog.py <source.html> --slug <slug> --ghost

# 仅推微信
python3 scripts/publish_blog.py <source.html> --slug <slug> --wechat

# 更新已有草稿（不新建）
python3 scripts/publish_blog.py <source.html> --slug <slug> \
  --ghost --update-ghost <post_id> \
  --wechat --update-wechat <media_id>
```

**脚本内置**：
- Ghost 版生成（去 nav/x-box/DOCTYPE/外层结构）
- 微信版生成（自定义组件用专用转换器，见脚本 CUSTOM_CONVERTERS 注册表）
- 双端 QC（自动检查 x-box / APAG / 签名等）
- 推送（调用 ghost_auto_publish.py + publish_wechat.py）

**铁律**：
- 🔴 Mars 只推 **draft**（必须带 `--draft` 参数），**绝对不直接发布**
- 发布权在 Eason：Eason 在 Ghost 后台看完草稿确认后，自己点发布
- 有专用微信转换器的文章（见 CUSTOM_CONVERTERS），注册表里登记后自动调用
- QC 未通过 → 脚本自动中止，不推送

---

## 二、环境信息

| 项目 | 值 |
|------|-----|
| Ghost Admin | `https://eason.ghost.io/ghost/` |
| 站点 URL | `https://www.easonzhang.ai/` |
| Ghost 主题 | source v1.5.0 |
| 认证方式 | 浏览器 session（无 Admin API Key），通过 CDP WebSocket 注入 |
| CDP 地址 | `ws://127.0.0.1:18800/devtools/page/{targetId}` |
| 传输方式 | Python websockets → CDP（绕过 browser evaluate 大小限制） |
| Code Injection CSS | `.gh-article-header { display: none !important; }` — 隐藏主题默认文章头 |

---

## 三、Slug 命名规范

Ghost 默认把中文标题转成拼音 slug，**又长又丑**。

**规则**：
- 每篇文章创建时必须手动指定短英文 slug
- 格式：`小写英文-用连字符`，3-4个单词，不超过30字符
- 在 POST 创建时通过 `slug` 字段设置

**示例**：
| 标题 | ❌ 默认 slug | ✅ 手动 slug |
|------|-------------|-------------|
| 我们想把AI Agent分工协作… | `wo-men-xiang-ba-ai-agent-fen-gong...` | `multi-agent-chaos` |
| 棋盘第40格… | `qi-pan-di-40-ge-ge-ren-chuang...` | `chessboard-40` |
| AI不会消灭企业软件… | `aibu-hui-xiao-mie-qi-ye-ruan...` | `ai-vs-enterprise-software` |

**创建草稿时指定**：
```javascript
posts: [{
  title: "文章标题",
  slug: "short-english-slug",  // ← 必须设
  lexical: lexicalJsonString,
  status: "draft",
  tags: [{name: "AI工具实战"}]
}]
```

---

## 四、HTML 源文件规范

### InSight 双版本输出
| 文件 | 用途 | 包含内容 |
|------|------|---------|
| `*-preview.html` | 本地预览 + Telegram 确认 | 完整 HTML（含 nav/x-box/APAG 标签） |
| `*-ghost.html` | Ghost 发布 | 干净 HTML（无 nav/x-box/APAG/DOCTYPE） |

### Ghost 版包含的内容
```
<style>...</style>       ✅（无 .label / .x-box CSS）
<div class="hero">       ✅
<div class="page">       ✅（h2 无 APAG 标签）
<div class="closing">    ✅（签名硬编码在模板里）
<div class="site-footer"> ✅
```

### Ghost 版不得包含
```
<!DOCTYPE html>          ❌
<html><head><body>       ❌
<nav>                    ❌（会显示 "DRAFT" 文字）
<div class="x-box">     ❌（X 简介不上 Ghost）
<span class="label">    ❌（APAG 标签不对读者可见）
```

---

## 五、Ghost API 推送格式

### Lexical JSON + HTML Card
```json
{
  "root": {
    "children": [
      {
        "type": "html",
        "version": 1,
        "html": "<style>...</style><div class=\"hero\">...</div>..."
      }
    ],
    "direction": null,
    "format": "",
    "indent": 0,
    "type": "root",
    "version": 1
  }
}
```

**❌ 不要用 `?source=html`** — 会导致 CSS 乱码。

### 编码传输（中文安全）
```python
import base64
b64 = base64.b64encode(new_lexical.encode("utf-8")).decode("ascii")
```

```javascript
// Ghost 端解码
const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
const lexical = new TextDecoder('utf-8').decode(bytes);
```

**❌ 不要直接用 `atob()`** — 只支持 Latin-1，中文会乱码。

### 创建草稿
```javascript
fetch("https://eason.ghost.io/ghost/api/admin/posts/", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    posts: [{
      title: "文章标题",
      slug: "short-slug",
      lexical: lexicalJsonString,
      status: "draft",
      tags: [{name: "AI工具实战"}]
    }]
  })
})
```

### 更新已有草稿
```javascript
fetch("https://eason.ghost.io/ghost/api/admin/posts/{id}/", {
  method: "PUT",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    posts: [{
      lexical: lexicalJsonString,
      updated_at: "原post的updated_at值"  // 必须传，防冲突
    }]
  })
})
```

---

## 六、发布前检查清单（推送前）

每篇文章推送 Ghost 前，逐项检查：

- [ ] **来源文件**：使用的是 InSight 输出的 `*-ghost.html`？（不是 preview 版）
- [ ] **APAG 标签**：h2 里没有 `<span class="label">`？（`grep 'class="label"'` 结果为零）
- [ ] **APAG CSS**：没有 `.label { ... }` 规则？
- [ ] **x-box**：没有 `<div class="x-box">`？
- [ ] **nav**：没有 `<nav>` 标签？
- [ ] **DOCTYPE/html/head/body**：没有外层包裹？
- [ ] **签名第1行**：`.name` = `我叫 Eason`？（不是 Eason Zhang）
- [ ] **签名第2行**：`.creds` = `CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人`？
- [ ] **签名禁止词**：closing 里无 Deloitte / ARTI / AMI / 杨国福？
- [ ] **内容禁区**：正文无品牌名（杨国福）、无产品名（AMI/ARTI）？
- [ ] **slug**：已设短英文 slug？
- [ ] **标题**：通过 Ghost API `title` 字段设置？
- [ ] **标签**：通过 Ghost API `tags` 字段设置？

## 六A、发布后验证清单（推送成功后必须执行）🔴

```bash
# 推送成功后，web_fetch 实际 URL 确认以下三项
```

- [ ] **签名验证**：`web_fetch` 实际 Ghost URL，确认「我叫 Eason」出现在页面中
- [ ] **禁止词验证**：页面内容不含 Deloitte / ARTI / AMI / 杨国福 / Eason Zhang（作为签名出现）
- [ ] **无重复帖**：Ghost 后台只有一篇该 slug 的文章，没有 `-2` 后缀重复帖

**以上任一不通过 → 立即用 `--update POST_ID` 重推正确版本，删除错误帖。**

> 历史教训（2026-03-19）：InSight 推了错误签名版到 Ghost，Mars 因为没有 fetch 实际 URL 而未发现，用户看到错误签名。

---

## 七、X 同步流程

每篇文章发布后，同步到 X：

1. **准备文案**：从 preview 版的 x-box 内容改写（中文博客用中文，英文博客用英文）
2. **附短链接**：`https://www.easonzhang.ai/{slug}/`
3. **追加到** `personal-brand/x-post-queue.md`
4. **发给 Eason**，Eason 自行发 X
5. **更新** `CONTEXT_EasonBlog.md` 状态表标记 X ✅

**X 文案要求**：
- 100-200 字，抓眼球的第一句 + 核心观点 + 链接
- 不用 hashtag 堆砌（最多 0-1 个）
- 结尾用 👇 引导点击
- 中英文不混写（同一条内选一种语言）

---

## 八、签名规范 🔴（违反超过5次，属于系统性问题）

### 正确格式（唯一标准，不可修改）

```html
<div class="closing">
  <div class="name">我叫 Eason</div>
  <div class="creds">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</div>
  <div class="tagline">[口语化1-2句，根据文章主题调整]</div>
</div>
```

### 禁止词清单（closing 区块内一个都不能出现）

| 禁止词 | 说明 |
|--------|------|
| `Eason Zhang` | .name 必须是「我叫 Eason」 |
| `Deloitte` | 不写公司名 |
| `ARTI` | 不写产品名 |
| `AMI` | 不写产品名 |
| `杨国福` | 不写品牌名 |
| `四大` | 不写行业标签 |
| `总监` | 不写职级描述 |
| `合伙人` | （除非是 creds 里的「前战略咨询合伙人」）|

### Mars QC 验证步骤（发布后必做）
1. `web_fetch` 实际 URL
2. 确认「我叫 Eason」在页面中存在
3. 确认页面无以上禁止词
4. 不通过 → 立即 `--update` 修复

**这条规则已被违反 5+ 次。没有发布后 web_fetch 验证 = QC 未完成。**

---

## 九、批量操作脚本

| 脚本 | 用途 | 路径 |
|------|------|------|
| `ghost_batch_push.py` | 批量推送 HTML → Ghost 草稿 | `tmp/ghost_batch_push.py` |
| `ghost_fix_xbox2.py` | 批量移除 x-box（旧文章修补用） | `tmp/ghost_fix_xbox2.py` |
| `ghost_fix_labels.py` | 批量移除 APAG 标签（旧文章修补用） | `tmp/ghost_fix_labels.py` |

**正常流程不需要修补脚本** — InSight 的 ghost.html 应该是干净的。
修补脚本只用于处理历史遗留问题。

---

## 十、已踩过的坑（不要重犯）

| # | 坑 | 后果 | 正确做法 |
|---|-----|------|---------|
| 1 | `?source=html` 推送完整 HTML | CSS 乱码 | 用 Lexical JSON + HTML Card |
| 2 | `atob()` 直接解码 | 中文乱码 | `Uint8Array` + `TextDecoder('utf-8')` |
| 3 | HTML Card 包含 `<nav>` | 编辑器显示 "DRAFT" | 去掉 nav |
| 4 | HTML Card 包含标题 | 标题重复显示 | Code Injection CSS 隐藏主题 header |
| 5 | 推送后才清理 APAG 标签/x-box | 多次往返修补 | 用 InSight ghost 版，推送前零修改 |
| 6 | 签名凭记忆写 | 违规 5+ 次（03-08/12/18/19） | 模板硬编码，永远不手写；dispatch 时明确要求 InSight 从 template-ghost.html 复制 closing |
| 7 | slug 用默认拼音 | 链接长达 80+ 字符 | 创建时手动指定短英文 slug |
| 8 | 微信版包含 x-box | 读者看到"X · 发布简介" | 微信转换时去掉 x-box（平台专用） |
| 9 | 微信草稿用 `--force-new` 而非 `--update` | 草稿箱出现重复篇 | 草稿已存在时用 `--update MEDIA_ID` 覆盖；cache 文件里有 `draft_media_id` |
| 10 | 发布后未 fetch 实际 URL 验证签名 | 错误签名对用户可见（2026-03-19） | 推送成功后必执行第六A节：web_fetch 实际 URL，确认「我叫 Eason」存在 |
| 11 | 专用转换器自写样式体系 | 与标准格式不一致，来回改9轮（2026-03-23） | 任何专用转换器必须 `from wechat_formatter import` 使用标准常量，不能自写；参考 convert_ai_memory_wechat.py |

---

## 十一、预览与验证

- 草稿预览 URL：`https://www.easonzhang.ai/p/{uuid}/`
- UUID 从 Ghost API 响应的 `posts[0].uuid` 获取
- 推送后必须在预览页确认：hero / 正文 / 签名 / 无重复标题 / 无 APAG 标签

---

## 十二、微信公众号发布 SOP

### 完整流程
```
博客 HTML（japan-xxx.html）
  ↓ 检查：文章是否有自定义组件（wall-card / method-list / highlight-box 等）？
  ├─ 是 → 写专用转换脚本（scripts/convert_xxx_wechat.py），不用 ghost_to_wechat.py
  └─ 否 → 用 scripts/ghost_to_wechat.py 转换
  ↓ 产出 *.wechat.html
  ↓ 检查微信版必须去掉的内容（见下）
  ↓ 检查 .wechat_cache.json 是否已有 draft_media_id
  ├─ 有 → python3 publish_wechat.py ... --update {media_id}（更新，不新建）
  └─ 没有 → python3 publish_wechat.py ...（首次创建）
  ↓ 去草稿箱确认渲染
  ↓ Eason 在后台发布
```

### 微信版必须去掉的内容
```
<div class="x-box">    ❌ X 简介是 Ghost/博客专用，微信读者不需要
<nav>                  ❌ 导航栏
DRAFT 标签             ❌
```

### 微信版必须包含
```
完整 <!DOCTYPE html><html><head><body> 外层结构  ✅
内联样式（无外部 CSS 依赖）                       ✅
签名区（我叫 Eason + creds + tagline）             ✅
```

### 自定义组件判断标准
博客 HTML 里如果有以下 class，`ghost_to_wechat.py` 会处理不了，必须写专用脚本：
- `.wall-card` / `.method-list` / `.highlight-box` / `.quote-block`
- `.step-card` / `.analogy` / `.alert-grid` / `.faq-item` / `pre.code-block`
- 任何 `display:flex` / `display:grid` 的卡片组件

### 专用转换器铁律（2026-03-23 沉淀）
**任何专用转换器必须 `from wechat_formatter import` 使用标准样式常量，不能自写样式体系。**

必须使用的常量：
```python
from wechat_formatter import (
    BRAND_RED, FF, S_BODY, S_HERO, S_HERO_TITLE, S_META, S_META_LABEL,
    S_PAGE, S_LEAD, S_H2, S_H3, S_P, S_BQ, S_HR, S_STRONG, S_CODE,
    S_CLOSING, S_CLOSING_NAME, S_CLOSING_CREDS, S_CLOSING_TAG, esc
)
```

**微信格式规范（对标 google-skill-patterns.wechat.html）**：
- Hero：`S_HERO` 样式（棕红标题居中 + 底部2px分隔线）
- 作者行：`S_META` + `S_META_LABEL` 右对齐，`文｜Eason`
- 正文：`<section>` 嵌套，`S_BODY` + `S_PAGE` 体系
- 签名：`S_CLOSING` 白底双棕红线，`S_CLOSING_NAME/CREDS/TAG`
- 跳过：x-box / site-footer / nav / DRAFT 标签

### 脚本路径
| 脚本 | 用途 |
|------|------|
| `scripts/ghost_to_wechat.py` | 标准 Ghost HTML → 微信（无自定义组件时用） |
| `scripts/publish_wechat.py` | 推送到微信草稿箱 |
| `scripts/convert_leasing_wechat.py` | japan-restaurant-leasing-trust.html 专用转换 |
| `scripts/convert_ai_memory_wechat.py` | ai-team-memory-system 专用（step-card/pre.code-block等，2026-03-23）|

### 封面图规则
| 文章类型 | 封面图路径 |
|---------|-----------|
| 🦞 AI协作 / AI工具 / 个人经历类（默认） | `personal-brand/assets/wechat-covers/lobster-default.jpg` |
| 其他主题 | 推送前问 Eason 指定 |

推送命令加 `--cover personal-brand/assets/wechat-covers/lobster-default.jpg`（AI协作类文章直接用，不自动截图生成）

### cache 文件
- 路径：`personal-brand/content/.wechat_cache.json`
- 内容：`draft_media_id`（已有草稿的 ID）+ `thumb_media_id`（封面图）
- **每次推送前先查这个文件**，有 `draft_media_id` 就用 `--update`

---

*本文档由 Mars 维护。任何新踩的坑立即补充到第十节。*

---

## 附：固化标准（Mars 执行约束）

**说"固化/沉淀/标准化"必须同时指出写进了哪个文件的哪一节。**
说不出来 = 没有固化 = 空话。
Eason 可以凭此直接打回要求补做。

---

## 十三、小红书发布 SOP（2026-03-19 建立）

### 工作流
```
InSight 写文章 → Mars 生成 XHS 卡片（HTML→截图 PNG）
  ↓
Mars 发文案 + 7张PNG给 Eason（Telegram）
  ↓
Eason 在手机小红书 App 手动发布（现阶段）
  ↓
Mars 更新 CONTEXT_EasonBlog.md 状态表 XHS ✅
```

### 卡片规范（v5 已固化）
- 尺寸：1242×1660（竖版）
- 封面：上半龙虾图（`assets/wechat-covers/lobster-default.jpg`）+ 下半白底大字标题
- 内容页：暖米白底（#F7F4EF）+ 品牌红标题 + 全文原文，不缩写
- 脚本：`scripts/xhs_card_ai_capability.py`（参考模板，每篇新建专用脚本）
- 截图：Playwright，viewport 1242×1660

### 文案规范
- 标题：≤30字，直接用文章标题
- 正文：核心论点列举 + 结论金句，≤500字
- Hashtag：5个以内，#AI工具 #AI效率 #AI协作 + 主题相关2个
- **不写「全文在博客」**（小红书用户不喜欢被导流出站）

### 🦞 封面图规则
所有文章默认用龙虾图封面，除非 Eason 另行指定。


## XHS 话题标签规范（2026-03-19 Eason 确认）
- 账号专属话题：#openclaw养龙虾 #openclaw #驯服AI
- 通用话题：#AI工具 #AI效率 #AI协作
- 每篇固定带账号专属话题，通用话题可调整
