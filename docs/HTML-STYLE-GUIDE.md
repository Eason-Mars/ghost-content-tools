# 博客 HTML 排版规范（强制）

> 适用：所有个人品牌博客、文章内容

## 强制模板

**使用此文件作为基础**：
```
/Users/dljapan/.openclaw/workspace/personal-brand/content/2026-03-06-ai-enterprise-software-final.html
```

复制此文件，只修改：
- `<title>` — 新标题
- `.hero h1` — 新标题
- `.hero-label` — 分类（如「创业者思考」「系统思考」）
- `.hero-meta` — 日期
- `.page` 内的正文（替换为新内容）

**禁止**：自由创建新 HTML 结构。所有博客必须用上面的模板。

---

## CSS 标准值（不可修改）

### 容器与间距

> 🔴 **Ghost HTML Card 专用铁律（2026-04-13 血泪固化）**
> Ghost HTML Card 有外层容器，`max-width` + `margin: 0 auto` 会造成**双重留白**。
> 必须用以下值，禁止改动：

```css
.page { 
  max-width: 100%;   /* 不设固定宽度，让 Ghost 主题控制 */
  margin: 0;         /* 不居中，Ghost 已有外层容器 */
  background: #fff;
  padding: 40px 20px 60px;  /* 桌面端：上下40/60px，左右20px */
}

@media (max-width: 600px) {
  .page { 
    padding: 32px 16px 52px;  /* 手机端：左右收窄到16px */
  }
}
```

**绝对禁止**：
- ❌ `max-width: 720px` — 双重留白
- ❌ `margin: 0 auto` — 双重留白  
- ❌ `padding: 52px 48px` — 左右过宽
- ❌ `padding: 40px 0 60px` — 左右零会导致文字贴边

### 文字间距

| 元素 | margin-bottom | line-height | 备注 |
|------|---------------|-------------|------|
| `p` | 1.4em | 1.9 | 正文段落 |
| `li` | 0.6em | 1.8 | 列表项 |
| `h2` | 16px（下方） | 1.3 | 大标题，上方 44px margin |
| `h3` | 10px（下方） | 1.3 | 小标题，上方 32px margin |

### 列表（ul/li）

```css
ul, ol { 
  margin: 0.2em 0 1.4em 1.6em;  /* 上下 + 左缩进 */
}

li { 
  margin-bottom: 0.6em;
  line-height: 1.8;
}
```

**强制要求**：列表项 ≥20 个时才能放行（手机端需要充足的垂直空间）

### 表格（.verdict-table）

```css
.verdict-table { 
  width: 100%; 
  border-collapse: collapse; 
  margin: 20px 0;
  font-size: 15px;
}

.verdict-table th { 
  background: #8B3A2A;        /* 棕红 */
  color: #fff;
  padding: 10px 14px;
  text-align: left;
  font-size: 13px;
  font-weight: 700;
}

.verdict-table td { 
  padding: 10px 14px; 
  border-bottom: 1px solid #e0dbd8;
}

.verdict-table tr:nth-child(even) td { 
  background: #faf5f3;        /* 交替行背景 */
}
```

---

## 颜色方案（全局统一）

- **主色**：棕红 `#8B3A2A`
- **深棕**：`#6B2A1A`
- **辅色**：金色 `#C5963A`
- **背景**：暖白 `#f5f3f0` / 内容区 `#fff`
- **表头背景**：暖米灰 `#F0E4D8`
- **交替行**：`#FAF8F6`
- **边框**：暖灰 `#E0DBD8`
- **文字**：深灰 `#1a1a1a`

---

## 内容排版原则

### 长段落拆分（强制）

**规则**：连续 >3 句话的段落必须拆分或改为列表

❌ **错误**：
```html
<p>第一点是 X。第二点是 Y。第三点是 Z。第四点是 W。</p>
```

✅ **正确**：
```html
<p>我有四个要点：</p>
<ul>
  <li>第一点是 X</li>
  <li>第二点是 Y</li>
  <li>第三点是 Z</li>
  <li>第四点是 W</li>
</ul>
```

### 标题层级

- `h2` — 大章节（2-4 个）
- `h3` — 子章节（每个 h2 下 2-3 个）
- 禁止 `h4` 及更深

### 强调元素

```html
<strong>重要文字</strong>    <!-- 黑色加粗 -->
<em>次要说明</em>            <!-- 灰色斜体 -->
<blockquote>引用或总结</blockquote>
```

---

## 特殊组件

### 课程框（.lesson）

```html
<div class="lesson">
  <div class="lesson-num">LESSON 01</div>
  <div class="lesson-text">内容文字</div>
</div>
```

### 备注框（.note-box）

```html
<div class="note-box">重要备注或补充说明</div>
```

### 提醒框（.alert-grid）

```html
<div class="alert-grid">
  <div class="alert-item alert-yellow">⚠️ 黄色提醒</div>
  <div class="alert-item alert-orange">⚠️ 橙色提醒</div>
  <div class="alert-item alert-red">⚠️ 红色提醒</div>
</div>
```

### 结尾签名框（.closing）

```html
<div class="closing">
  <div class="name">Eason Zhang</div>
  <div class="creds">CFA 持证人 · Eason Venture Studio · easonzhang.ai</div>
  <div class="tagline">独立思考，长期主义</div>
</div>
```

---

## 发布前 QC 检查清单

- [ ] 用了标准模板（`2026-03-06-ai-enterprise-software-final.html`）
- [ ] 列表项 ≥20 个或已拆分段落
- [ ] 所有 `<p>` margin-bottom 保留为 1.4em
- [ ] 所有 `<li>` margin-bottom 保留为 0.6em
- [ ] 表格用了 `.verdict-table` 类
- [ ] 在浏览器预览，手机端（600px 以下）排版正常
- [ ] 颜色只用方案中的 6 个（不自创新颜色）
- [ ] `<h1>` 只在 hero 区，正文不要

---

## 草稿标题规范（强制）

**不在右上角加「DRAFT」标识**
- ❌ 错误：`<span class="tag">DRAFT · 2026-04-02</span>`
- ✅ 正确：删掉整个 `<span class="tag">` 或改为空
- 原因：Eason 看完后直接点「Publish」发布，不需要标识提醒

---

## 最后的话

这份规范的目的：让所有内容看起来像来自同一个品牌，同时确保在各种屏幕上都可读。

模板已经测试过，直接用，不要改。
