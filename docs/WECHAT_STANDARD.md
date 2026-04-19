# 微信公众号发布规范（2026-03-21 固化）

> 每次发微信文章前必读此文件。违反任何一条都会导致返工。

---

## 一、文件规范

| 用途 | 文件命名 | 格式要求 |
|------|---------|---------|
| Ghost 博客 | `content/<slug>.html` | 外部 CSS class，完整 HTML 结构 |
| 微信公众号 | `content/<slug>.wechat.html` | **全 inline style，section 标签，无 class，无外部 CSS** |

**铁律：博客 HTML 不得直接推微信。必须有独立的 `.wechat.html` 文件。**

---

## 二、微信 HTML 格式规范

参考模板：`content/japan-restaurant-leasing-trust.wechat.html`

### 基础结构
```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:20px;background:#fff;">
<section style="font-family:-apple-system,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',Georgia,serif;font-size:15px;line-height:2.0;color:rgba(0,0,0,0.9);letter-spacing:0.544px;">
  <!-- 内容 -->
</section>
</body>
</html>
```

### 核心样式常量
```
字体：-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",Georgia,serif
正文：15px / line-height:2.0 / letter-spacing:0.544px / color:rgba(0,0,0,0.9)
主色：#8B3A2A（棕红）
金色：#C5963A
```

### 常用组件 inline style

**Hero 标题区**
```html
<section style="text-align:center;padding:32px 16px 24px;border-bottom:2px solid #8B3A2A;margin-bottom:24px;">
<p style="font-size:22px;font-weight:800;line-height:1.4;color:#8B3A2A;margin:0 auto;text-align:center;">标题</p>
</section>
```

**作者行**
```html
<section style="font-size:13px;color:#666;text-align:right;margin:0 16px 24px;line-height:1.8;letter-spacing:0.5px;"><span style="font-weight:700;color:#666;">文｜</span>Eason</section>
```

**正文段落**
```html
<section style="margin:0 0 24px;font-size:15px;line-height:2.0;letter-spacing:0.544px;text-align:justify;">内容</section>
```

**H2 小标题**
```html
<section style="font-size:18px;color:rgba(0,0,0,0.9);margin:36px 0 16px;padding-left:14px;border-left:4px solid #8B3A2A;font-weight:800;line-height:1.75;">标题</section>
```

**高亮框（暖色背景）**
```html
<section style="margin:0 0 24px;padding:16px 20px;background:#F0E4D8;border-radius:4px;font-size:15px;line-height:2.0;letter-spacing:0.544px;color:#5a2a1a;"><p>内容</p></section>
```

**引用框**
```html
<section style="margin:0 0 24px;padding:16px 20px;border-left:4px solid #C5963A;background:#fff8f0;font-size:15px;line-height:2.0;letter-spacing:0.544px;font-style:italic;color:#444;"><p>内容</p></section>
```

**卡片（金色左线）**
```html
<section style="margin:0 0 16px;padding:18px 20px;background:#fff;border-left:4px solid #C5963A;border:1px solid #e0dbd8;border-radius:4px;">内容</section>
```

---

## 三、签名（固化，所有文章统一，不得自行修改）

```html
<section style="background:#fff;padding:20px 0;margin-top:40px;border-top:2px solid #8B3A2A;border-bottom:2px solid #8B3A2A;">
<p style="font-size:17px;font-weight:800;margin-bottom:4px;color:#8B3A2A;">我叫 Eason</p>
<p style="font-size:12px;color:#888;line-height:1.8;margin-bottom:6px;letter-spacing:0.5px;">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</p>
<p style="font-size:14px;color:#333;line-height:1.8;margin:0;">在东京经营几家餐厅，用AI做投资研究和餐饮零售管理——然后把踩过的坑写出来</p>
</section>
```

**禁止**：重新生成签名文字、改成深色背景块、更改任何文字内容。

---

## 四、图片处理规范

1. **格式**：微信不支持 webp → 必须转成 jpg
   ```python
   from PIL import Image
   Image.open('x.webp').convert('RGB').save('x.jpg', 'JPEG', quality=88)
   ```

2. **嵌入方式**：base64 嵌入 HTML（publish_wechat.py 会自动提取上传到微信 CDN）
   ```html
   <img src="data:image/jpeg;base64,{b64}" style="width:100%;display:block;margin:20px 0 6px;border-radius:4px;">
   ```

3. **封面图**：龙虾系列文章统一用 `personal-brand/assets/wechat-covers/lobster-default.jpg`
   - 通过 `--cover` 参数传入，不要替换正文里的图片

---

## 五、发布流程（完整，按顺序执行）

### Step 1：生成博客版 HTML
- 文件：`content/<slug>.html`
- 含完整 CSS、meta charset="UTF-8"

### Step 2：生成微信版 HTML
- 文件：`content/<slug>.wechat.html`
- 全 inline style，参照本规范
- 复制签名 HTML（第三节），不重新生成
- 图片转 jpg，base64 嵌入

### Step 3：首次推草稿
```bash
python3 scripts/publish_wechat.py content/<slug>.wechat.html \
  --title "标题" \
  --author "Eason Zhang" \
  --digest "摘要（80字以内）" \
  --cover personal-brand/assets/wechat-covers/lobster-default.jpg \
  --draft
```
→ 自动保存 media_id 到 `content/.wechat_cache.json`

### Step 4：修改时更新草稿（不推新草稿）
```bash
python3 scripts/publish_wechat.py content/<slug>.wechat.html \
  --title "标题" \
  --author "Eason Zhang" \
  --digest "摘要" \
  --cover personal-brand/assets/wechat-covers/lobster-default.jpg \
  --update <media_id> \
  --draft
```
- media_id 从 `.wechat_cache.json` 或上次输出里取
- **禁止**：同一篇用 `--force-new` 创建新草稿（除非旧草稿已发布/删除）

### Step 5：Eason 在草稿箱确认后发布

---

## 六、常见错误 → 正确做法

| 错误 | 正确 |
|------|------|
| 博客 HTML 直接推微信 | 生成独立 `.wechat.html` |
| 签名重新生成 | 直接复制第三节固定 HTML |
| 图片用 webp | 转成 jpg 再嵌入 |
| 修改时推新草稿 | 用 `--update <media_id>` |
| 龙虾图替换正文第一张图 | 用 `--cover` 参数传封面，正文图不动 |
| 签名用深色背景块 | 白底 + 棕红上下边线（见第三节） |

---

_最后更新：2026-03-21（google-skill-patterns 发布后固化）_
