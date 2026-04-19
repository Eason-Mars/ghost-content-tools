# TEMPLATE.md — 博文 HTML 模板规范

> InSight 和 Mars 生成博文 HTML 时，必须严格按照本文件的模块拼装，不得自行创作签名或结构。
> 最后更新：2026-03-18

---

## 一、页面骨架（每篇固定）

```html
<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[文章标题]</title>
<style>/* 见第三节 CSS 规范 */</style>
</head>
<body>
<nav>
  <span class="logo">easonzhang.ai</span>
  <span class="tag">DRAFT</span>
</nav>
<div class="hero">
  <div class="hero-label">[Topic Tag · Category]</div>
  <h1>[文章标题]</h1>
  <div class="subtitle">[一句话副标题]</div>
  <div class="hero-meta">Eason Zhang · [年份]</div>
  <div class="hero-divider"></div>
</div>
<div class="page">
  <div class="lead">[引言段，150-250字]</div>

  [正文区块，h2 + 内容组件]

  <div class="closing">
    <div class="name">我叫 Eason</div>
    <div class="creds">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</div>
    <div class="tagline">[tagline，见第二节规范]</div>
  </div>
  <div class="x-box">
    <div class="x-label">X · 发布简介</div>
    <p>[Twitter/X 简介，100字以内，结尾"全文在博客："]</p>
  </div>
  <div class="site-footer">easonzhang.ai · Eason Zhang</div>
</div>
</body>
</html>
```

---

## 二、签名规范（固定，不得修改）

```html
<div class="closing">
  <div class="name">我叫 Eason</div>
  <div class="creds">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</div>
  <div class="tagline">[根据文章主题调整，口语化，1-2句]</div>
</div>
```

### Tagline 示例（参考语气，不照抄）
- 在东京，投了几家麻辣烫，现在在探索用AI做投资研究和餐饮运营赋能——然后把这些都写出来。
- 在东京经营 6 家餐厅，同时在用 AI 重构餐饮运营和投资研究——然后把踩过的坑写出来。

### Tagline 禁区
❌ 不写口号式句子（"把经历变成内容，把内容变成资产"之类）
❌ 不提产品名（AMI / ARTI）
❌ 不提品牌名（杨国福）

---

## 三、CSS 规范（必须包含，直接复制）

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, "Noto Sans SC", "PingFang SC", "Helvetica Neue", Arial, sans-serif; background: #f5f3f0; color: #1a1a1a; line-height: 1.8; }
nav { background: #8B3A2A; color: #fff; padding: 14px 32px; display: flex; align-items: center; justify-content: space-between; font-size: 14px; }
nav .logo { font-weight: 700; letter-spacing: 0.5px; }
nav .tag { font-size: 11px; font-weight: 700; letter-spacing: 1.5px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 2px; text-transform: uppercase; }
.hero { background: #8B3A2A; color: #fff; padding: 56px 32px 44px; text-align: center; }
.hero-label { font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; opacity: 0.7; margin-bottom: 12px; }
.hero h1 { font-size: 28px; font-weight: 800; line-height: 1.45; max-width: 680px; margin: 0 auto 16px; }
.hero .subtitle { font-size: 16px; opacity: 0.8; max-width: 540px; margin: 0 auto 8px; line-height: 1.6; }
.hero-meta { font-size: 13px; opacity: 0.60; margin-top: 10px; }
.hero-divider { width: 40px; height: 3px; background: rgba(255,255,255,0.3); margin: 24px auto 0; border-radius: 2px; }
.page { max-width: 700px; margin: 0 auto; padding: 48px 24px 72px; }
.lead { font-size: 17px; line-height: 1.95; margin-bottom: 36px; color: #333; border-bottom: 1px solid #e0dbd8; padding-bottom: 28px; }
h2 { border-left: 4px solid #8B3A2A; padding-left: 14px; font-size: 20px; font-weight: 700; margin: 44px 0 18px; color: #1a1a1a; line-height: 1.6; }
h3 { font-size: 16px; font-weight: 700; color: #6B2A1A; margin: 32px 0 10px; }
p { font-size: 16px; line-height: 1.9; margin-bottom: 16px; color: #2a2a2a; }
.closing { background: #8B3A2A; color: #fff; padding: 28px 32px; margin-top: 48px; border-radius: 4px; }
.closing .name { font-size: 20px; font-weight: 800; margin-bottom: 8px; }
.closing .creds { font-size: 12px; opacity: 0.70; line-height: 1.8; margin-bottom: 8px; font-family: Arial, sans-serif; letter-spacing: 0.5px; }
.closing .tagline { font-size: 13px; opacity: 0.85; line-height: 1.7; }
.x-box { background: #f5f3f0; border: 1px solid #e0dbd8; border-radius: 6px; padding: 20px 24px; margin-top: 28px; }
.x-box .x-label { font-size: 11px; letter-spacing: 2px; color: #8B3A2A; font-family: Arial, sans-serif; font-weight: 700; margin-bottom: 10px; }
.x-box p { font-size: 15px; margin: 0; color: #1a1a1a; }
.site-footer { margin-top: 48px; padding-top: 20px; border-top: 1px solid #e0dbd8; font-size: 12px; color: #aaa; font-family: Arial, sans-serif; text-align: center; }
```

---

## 四、允许使用的内容组件（白名单）

> ⚠️ 只能使用下列组件。使用白名单之外的自定义 class，发布脚本无法处理微信版。

### 4.1 wall-card（信息墙/门槛卡片）
**适用**：列举多个障碍/规则/维度，每项有标题+说明。

```html
<div class="wall-card">
  <div class="wall-num">Wall 01</div>
  <div class="wall-title">标题文字 <span class="jp">副文字（日文/英文）</span></div>
  <div class="rule">表面规则：……</div>
  <div class="fear-label">墙后面真正的顾虑</div>
  <p class="fear">……</p>
</div>
```
**CSS（需加入 `<style>`）**：
```css
.wall-card { background: #fff; border: 1px solid #E0DBD8; border-radius: 8px; padding: 22px 26px; margin-bottom: 16px; position: relative; overflow: hidden; }
.wall-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #C5963A; }
.wall-card .wall-num { font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #C5963A; margin-bottom: 4px; }
.wall-card .wall-title { font-size: 17px; font-weight: 700; color: #8B3A2A; margin-bottom: 6px; }
.wall-card .wall-title .jp { font-size: 13px; color: #aaa; font-weight: 400; margin-left: 6px; }
.wall-card .rule { font-size: 13px; color: #888; margin-bottom: 8px; line-height: 1.7; }
.wall-card .fear-label { display: inline-block; font-size: 11px; font-weight: 700; color: #8B3A2A; letter-spacing: 1px; margin-bottom: 4px; text-transform: uppercase; }
.wall-card .fear { font-size: 15px; color: #333; line-height: 1.8; margin-bottom: 0; }
```

---

### 4.2 method-list（方法/行动列表）
**适用**：步骤、方法、行动清单，每项有 icon + 标题 + 说明。

```html
<ul class="method-list">
  <li>
    <span class="icon">📄</span>
    <div class="content">
      <strong>方法标题</strong>
      <span>方法说明文字……</span>
    </div>
  </li>
</ul>
```
**CSS**：
```css
.method-list { list-style: none; padding: 0; margin: 20px 0; }
.method-list li { background: #fff; border: 1px solid #E0DBD8; border-radius: 6px; padding: 16px 20px; margin-bottom: 10px; display: flex; gap: 14px; align-items: flex-start; }
.method-list li .icon { font-size: 18px; flex-shrink: 0; line-height: 1.4; }
.method-list li .content { flex: 1; }
.method-list li .content strong { display: block; font-size: 15px; font-weight: 700; color: #8B3A2A; margin-bottom: 4px; }
.method-list li .content span { font-size: 14px; color: #555; line-height: 1.8; }
```

---

### 4.3 highlight-box（高亮结论框）
**适用**：单段核心结论、总结、强调。

```html
<div class="highlight-box">
  <p>核心结论文字，可包含 <strong>加粗</strong>。</p>
</div>
```
**CSS**：
```css
.highlight-box { background: #F0E4D8; border-radius: 8px; padding: 22px 26px; margin: 28px 0; }
.highlight-box p { font-size: 15px; margin-bottom: 0; color: #5a2a1a; line-height: 1.85; }
```

---

### 4.4 quote-block（引用块）
**适用**：关键金句、引用、需要突出的单段话。

```html
<div class="quote-block">
  <p>引用文字……</p>
</div>
```
**CSS**：
```css
.quote-block { background: #fff; border-left: 4px solid #C5963A; padding: 20px 24px; margin: 28px 0; border-radius: 0 8px 8px 0; box-shadow: 0 1px 6px rgba(0,0,0,0.06); }
.quote-block p { font-size: 17px; margin-bottom: 0; color: #333; font-style: italic; line-height: 1.85; }
```

---

### 4.5 lead（引言段）
**适用**：每篇文章开头的引言，与正文视觉区隔。

```html
<div class="lead">
  引言文字，可用 <strong>加粗</strong> 和 <br><br> 分段。
</div>
```

---

## 五、禁止事项

| 禁止 | 原因 |
|------|------|
| `<span class="label">A</span>` 等 APAG 字母标签 | APAG 是内部框架，绝不对读者可见 |
| 白名单之外的自定义 class | 发布脚本无法处理微信转换 |
| 品牌名：杨国福 | 博客内容不提品牌 |
| 产品名：AMI / ARTI | 博客内容不提产品 |
| 凭记忆写签名 | 必须从本文件第二节复制 |

---

## 六、发布流程（Mars 执行）

```bash
# 一条命令完成 Ghost + 微信双端适配推送
python3 scripts/publish_blog.py <source.html> --slug <slug> --all

# 更新已有草稿（不新建）
python3 scripts/publish_blog.py <source.html> --slug <slug> --all \
  --update-ghost <ghost_post_id> --update-wechat <wechat_media_id>
```

脚本自动完成：
- Ghost版生成（去 nav/x-box/DOCTYPE）
- 微信版生成（内联样式，白名单组件自动转换）
- 双端 QC（x-box / APAG / 签名 / 品牌名全检查）
- 推送到草稿箱

---

## 七、Mars QC 检查清单（发布前必过）

- [ ] 签名：`我叫 Eason` / `CFA持证人…` / tagline（从本文件复制）
- [ ] x-box 存在且有 X 简介文字
- [ ] 无 APAG 字母标签（`grep 'class="label"'` 结果为零）
- [ ] 无品牌名（杨国福 / AMI / ARTI）
- [ ] 所有自定义组件在白名单内（4.1–4.5）
- [ ] `publish_blog.py --dry-run` QC 全部 ✅

---

*本文档由 Mars 维护。白名单组件新增须同步更新 `scripts/publish_blog.py` 的组件映射表。*
