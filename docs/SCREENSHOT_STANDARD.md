# SCREENSHOT_STANDARD.md — 文章配图（截图）标准

> 建立日期：2026-03-14
> 适用范围：所有 InSight 输出的博客/文章/社交媒体内容

## 核心原则

**真实 > 美观。** 读者要看到的是"你真的在用 AI"，不是渲染图。
截图是最强的信任信号——对话记录、执行过程、实际输出，都比文字描述有力 10 倍。

---

## 配图密度标准

| 内容类型 | 配图数量 | 说明 |
|---------|---------|------|
| Ghost 博客（>1500字）| 3-6 张 | Hero 1张 + 正文每 600-800 字插 1 张 |
| Ghost 博客（800-1500字）| 2-4 张 | Hero 1张 + 正文 1-3 张 |
| 小红书 | 3-9 张 | 封面1张 + 内容图 + 金句图 |
| Twitter/X Thread | 1-3 张 | 关键截图，不要每条都配 |
| LinkedIn | 1-2 张 | 开头1张抓眼球即可 |

---

## 截图类型优先级

### Tier 1：对话截图（最高优先）
- Eason ↔ Mars/Agent 的 Telegram 对话
- 体现"指令 → 执行 → 结果"的完整闭环
- **要求**：保留时间戳、头像、对话气泡完整性
- **示例场景**：Eason 说"帮我分析深南电路" → Mars 派发 → 研报回来

### Tier 2：执行过程截图
- 终端执行输出（脚本跑数据、API 返回）
- 浏览器抓取页面（数据源网站）
- Agent 编排过程（子 Agent spawn → 完成）
- **要求**：关键数据可读，非关键部分可裁剪

### Tier 3：输出成果截图
- 生成的 HTML 报告渲染效果
- 数据表格/图表
- Ghost 已发布文章的页面截图
- **要求**：展示最终质量，体现专业度

### Tier 4：架构/流程图（最低优先）
- 系统架构示意
- 工作流流程图
- **当前用 ASCII/文字描述替代，AI 生图能力建立后升级**

---

## 截图采集方法

### 方法 1：browser 工具截图
```
# 截取当前页面
browser(action="screenshot", fullPage=true)

# 截取特定元素
browser(action="screenshot", selector=".report-container")
```
适用：网页内容、HTML 报告渲染效果、Ghost 页面

### 方法 2：Telegram 对话截图
- Eason 手动截图发给 Mars
- 或用 node screen_record 截取桌面

### 方法 3：终端输出保存
```bash
# 执行时 tee 到文件，再用 browser 渲染成图
script -q /tmp/terminal_output.txt command_here

# 或直接保存关键输出到 HTML，browser 截图
```

### 方法 4：canvas 渲染截图
```
# 把 HTML 内容渲染为截图
canvas(action="present", url="file:///path/to/report.html")
canvas(action="snapshot")
```
适用：报告/图表的高质量截图

---

## 截图处理流水线

### 必做步骤（对外发布前）
1. **打码** — 所有截图必须过 `redact_screenshots.py`
   ```bash
   python3 scripts/redact_screenshots.py screenshot.png --keywords ARTI
   ```
   - 默认打码：ARTI
   - 按需追加：API Key、个人手机号、敏感金额等

2. **压缩** — 默认 600px 宽、quality 75（脚本自动处理）

3. **命名** — `{slug}-{序号}-{描述}.jpg`
   - 例：`ai-research-01-dispatch.jpg`
   - 例：`ai-research-02-report-output.jpg`

### 存储路径
```
personal-brand/images/{slug}/
  ├── {slug}-01-hero.jpg
  ├── {slug}-02-conversation.jpg
  ├── {slug}-03-terminal.jpg
  └── {slug}-04-output.jpg
```

---

## 写作时的截图决策树

```
写到某个段落 → 问自己：这里有"眼见为实"的机会吗？
  │
  ├── 有对话？ → Tier 1 对话截图
  ├── 有执行过程？ → Tier 2 终端/浏览器截图
  ├── 有输出成果？ → Tier 3 报告/数据截图
  ├── 需要解释架构？ → Tier 4 文字描述（暂）
  └── 纯观点/论述 → 不配图，文字足够
```

---

## InSight 执行规范

InSight 在写文章时必须：
1. **规划阶段**：列出配图计划（几张、什么类型、插在哪）
2. **采集阶段**：告知 Mars 需要哪些截图素材
3. **组装阶段**：blog_render.py 支持 `<img>` 标签插入
4. **QC 阶段**：content_qc.py 检查配图数量是否达标

### Mars 协作职责
- InSight 请求截图 → Mars 用 browser/canvas 工具采集
- 对话截图 → 提醒 Eason 截图，或从历史记录中提取
- 所有截图发布前 → 过打码脚本

---

## 禁止事项

❌ 不用库存图片（Unsplash/Pexels 等通用配图）
❌ 不用 AI 生成的"假截图"
❌ 不在截图中暴露：API Key、完整 Token、内部群 ID、他人隐私信息
❌ 不为了配图而配图——没有合适截图时，宁可不放
