# ROUTING.md — ghost-content-tools 脚本归属表

> 权威仓库：`Eason-Mars/ghost-content-tools`
> 本地工作目录：`/Users/dljapan/.openclaw/workspace-ghost/`
>
> **铁律**：所有脚本改动必须在本仓库开 PR，禁止直接修改本地文件后跳过 PR。
> `workspace/scripts/` 下的同名文件是只读副本（从本仓库同步），不是权威来源。

---

## 受保护脚本（ghost-content-tools 仓库权威）

| 脚本文件 | 权威路径 | 说明 |
|---------|---------|------|
| `ghost_to_wechat_body.py` | `workspace-ghost/scripts/ghost_to_wechat_body.py` | Ghost HTML → 微信正文提取器（premailer inline + 微信兼容性转换）|
| `ghost_auto_publish.py` | `workspace-ghost/scripts/ghost_auto_publish.py` | Ghost 文章发布（CDP 方式）|
| `publish_wechat.py` | `workspace-ghost/scripts/publish_wechat.py` | 微信公众号草稿推送 |
| `publish_blog.py` | `workspace-ghost/scripts/publish_blog.py` | 博客发布流程脚本 |

---

## 副本位置（只读，不得直接修改）

```
/Users/dljapan/.openclaw/workspace/scripts/ghost_to_wechat_body.py  ← 副本
/Users/dljapan/.openclaw/workspace/scripts/ghost_auto_publish.py     ← 副本
/Users/dljapan/.openclaw/workspace/scripts/publish_wechat.py         ← 副本
```

**正确流程**：需要改 → 在本仓库（ghost-content-tools）开 PR → Merge → 同步副本

---

## 违规记录

| 日期 | 事件 | 状态 |
|------|------|------|
| 2026-05-25 | `workspace/scripts/ghost_to_wechat_body.py` 被直接修改（+1840字节），未开 PR | 补 PR 已提交（见 sync/ghost-to-wechat-body-2026-05-25）|
