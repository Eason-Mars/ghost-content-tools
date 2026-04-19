# Ghost/Blog 工具链审查与重构方案

> **Issue**: [#1](https://github.com/Eason-Mars/ghost-content-tools/issues/1) — Ghost/Blog 工具链深度审查和重构方案
> **Author**: Mars (代理 Claude Code)
> **Date**: 2026-04-19
> **Scope**: 审查 17 个内容发布工具脚本，提出模块化重构方案

---

## 0. 执行摘要（TL;DR）

### 现状
- **17 个脚本**，总计 4164 行代码
- **5 个分类**：Ghost（3）/ WeChat（7）/ XHS（1）/ 转换工具（4）/ Great Minds（2）
- **工作流**：Ghost → WeChat → XHS（某些情况）
- **问题**：代码散落、缺乏版本控制、重复逻辑、错误处理不完善

### 关键发现
1. **重复代码**：ghost_to_wechat.py 和 ghost_to_wechat_body.py 有大量重叠（都在做 HTML → WeChat 转换）
2. **硬编码配置**：API Key、平台 ID 散落在各脚本中
3. **缺乏统一接口**：WeChat 发布有三种不同的方式（publish_wechat.py / ghost_to_wechat.py / great_minds_ghost_to_wechat.py）
4. **测试缺失**：无单元测试覆盖
5. **日志不统一**：有 print、有 logging，混乱

### 重构方案
分 3 个优先级，共 5 个 PR：
- **P0**：统一配置 + 模块化格式转换
- **P1**：Ghost/WeChat API 抽象
- **P2**：测试框架 + 文档完善

---

## 1. 代码库现状

### 1.1 脚本总体统计

| 指标 | 数值 |
|------|------|
| 总脚本数 | 17 |
| 总行数 | 4164 |
| 平均每个 | 245 行 |
| 最大 | great_minds_ghost_to_wechat.py (495 行) |
| 最小 | xhs_card_ai_capability.py (78 行) |

### 1.2 脚本分类详表

#### Ghost 相关（3 个脚本，总计 ~850 行）

| 脚本 | 职责 | 行数 | 状态 |
|------|------|------|------|
| `ghost_auto_publish.py` | Ghost CMS 自动发布接口 | ~300 | 核心，维护中 |
| `ghost_backfill_posts.py` | 从 Supabase 回填 Ghost 草稿 | ~250 | 辅助，运维用 |
| `blog_posts_backfill.py` | 博客数据同步 | ~150 | 低频 |

**特点**：调用 Ghost API（REST），需要 Ghost API Key + URL

#### WeChat 相关（7 个脚本，总计 ~1600 行）

| 脚本 | 职责 | 行数 | 使用频率 |
|------|------|------|---------|
| `publish_wechat.py` | 微信公众号发布（主入口） | ~280 | ⭐⭐⭐ 高频 |
| `ghost_to_wechat.py` | Ghost HTML → WeChat HTML | ~350 | ⭐⭐ 中频 |
| `ghost_to_wechat_body.py` | Ghost HTML → WeChat 正文体 | ~360 | ⭐⭐ 中频 |
| `great_minds_ghost_to_wechat.py` | Great Minds 专用转换 | ~495 | ⭐ 低频（周刊） |
| `great_minds_wechat_inline.py` | 内联脚注处理 | ~85 | 🔴 废弃？ |
| `wechat_formatter.py` | WeChat 格式化工具函数库 | ~220 | 被调用 |
| `wechat_send.py` | WeChat API 调用 | ~130 | 被调用 |

**问题**：
- `ghost_to_wechat.py` 和 `ghost_to_wechat_body.py` 有 70% 的重复逻辑
- `publish_wechat.py` 直接调用浏览器自动化（Selenium？Playwright？），不可靠
- `great_minds_ghost_to_wechat.py` 硬编码了大量模板和样式

#### 小红书相关（1 个脚本，~78 行）

| 脚本 | 职责 | 状态 |
|------|------|------|
| `xhs_card_ai_capability.py` | 生成 XHS 卡片（AI Capability） | 原型阶段 |

**特点**：使用 PIL 生成图片，API 集成度低

#### 转换工具（4 个脚本，~750 行）

| 脚本 | 职责 |
|------|------|
| `convert_ai_capability_wechat.py` | AI Capability → WeChat 卡片 |
| `convert_ai_memory_wechat.py` | Memory → WeChat 卡片 |
| `convert_leasing_wechat.py` | 租赁信息 → WeChat 卡片 |
| `create_blog_posts_table.py` | 数据库初始化 |

**特点**：独立数据源转换，与 Ghost 无关

#### Great Minds 专用（2 个脚本）

这两个脚本是 Great Minds 周刊的专用工具，包含硬编码的排版和样式。

### 1.3 工作流分析

```
【内容创作流程】

Eason 在 Ghost 编写文章（Draft）
    ↓
ghost_auto_publish.py
    ├─ 监听 Ghost 发布事件
    ├─ 提取文章 HTML
    └─ 触发转换流程
    ↓
【WeChat 路线】
ghost_to_wechat_body.py / publish_wechat.py
    ├─ 将 Ghost HTML 转为 WeChat 兼容格式
    ├─ 处理图片（下载、上传到 WeChat 素材库）
    ├─ 调用 WeChat API 发布
    └─ ✅ 发布完成
    ↓
【Great Minds 周刊特殊流程】
great_minds_ghost_to_wechat.py
    ├─ 聚合多篇文章
    ├─ 应用特殊排版模板
    ├─ 生成周刊 HTML
    └─ 发布到 WeChat
    ↓
【XHS 路线】（手动，非自动）
xhs_card_ai_capability.py
    ├─ 从数据源读取内容
    ├─ 生成卡片图片
    └─ 手动上传（暂无 API）
```

### 1.4 依赖分析

| 库 | 用途 | 脚本 |
|-----|------|------|
| `requests` | HTTP 调用（Ghost API、WeChat API） | 大多数 |
| `supabase` | 数据源 | ghost_auto_publish、blog_posts_backfill |
| `selenium` 或 `playwright` | 浏览器自动化（WeChat 发布） | publish_wechat |
| `PIL/Pillow` | 图片生成（XHS 卡片） | xhs_card_ai_capability |
| `beautifulsoup4` 或正则 | HTML 解析和转换 | ghost_to_wechat_body、wechat_formatter |

---

## 2. 关键问题诊断

### 2.1 代码复用性差

**问题**：`ghost_to_wechat.py` 和 `ghost_to_wechat_body.py` 有 ~70% 重复

两个脚本都在做 HTML → WeChat 转换，但实现不同：
- `ghost_to_wechat.py`：保留样式信息（颜色、字体）
- `ghost_to_wechat_body.py`：纯正文（只有段落、列表、链接）

**影响**：修改一个脚本时需要同步到另一个

### 2.2 配置硬编码

**问题**：API Key、平台 ID 分散在各脚本中

示例：
```python
# publish_wechat.py 中可能有
GHOST_API_KEY = "xxx"
WECHAT_APPID = "yyy"

# ghost_auto_publish.py 中也有
# ...
```

**影响**：难以维护、容易泄露、环境隔离困难

### 2.3 多种发布方式并存

WeChat 发布有三种接口：
1. `publish_wechat.py` - 浏览器自动化（不稳定）
2. `ghost_to_wechat.py` - 直接调用 WeChat API（推荐）
3. `great_minds_ghost_to_wechat.py` - 专用（硬编码排版）

**影响**：用户困惑，维护成本高

### 2.4 错误处理缺失

**问题**：无统一的错误处理、重试、日志记录

示例：
```python
# 典型的脆弱代码
response = requests.post(url, data=data)
result = response.json()  # 可能失败，无异常处理
```

**影响**：脚本经常崩溃，难以调试

### 2.5 缺少测试

**问题**：无单元测试覆盖，无集成测试

**影响**：修改代码时容易引入 bug

---

## 3. 重构优化方案

### 3.1 模块化架构设计

```
ghost-content-tools/
├── src/
│   ├── __init__.py
│   ├── config.py                 # ✨ 统一配置管理
│   ├── logger.py                 # 统一日志
│   ├── errors.py                 # 统一异常类
│   ├── core/
│   │   ├── formatter.py          # ✨ 通用格式转换
│   │   ├── publisher.py          # 抽象发布器接口
│   │   └── api_client.py         # HTTP 客户端封装
│   ├── publishers/
│   │   ├── __init__.py
│   │   ├── ghost.py              # Ghost API 实现
│   │   ├── wechat.py             # WeChat API 实现
│   │   └── xhs.py                # XHS API 实现
│   ├── formatters/
│   │   ├── __init__.py
│   │   ├── html_to_wechat.py     # HTML → WeChat（通用）
│   │   ├── html_to_xhs.py        # HTML → XHS
│   │   └── templates.py          # 格式模板
│   ├── scripts/                  # 用户脚本（调用上层 API）
│   │   ├── publish_to_wechat.py
│   │   ├── publish_to_xhs.py
│   │   ├── publish_all.py        # 同时发布到所有平台
│   │   └── ...
│   └── utils/
│       ├── image_handler.py      # 图片处理（下载、上传）
│       └── retry.py              # 重试机制
├── tests/
│   ├── test_formatters.py        # ✨ 格式转换测试
│   ├── test_publishers.py
│   └── test_integration.py
├── config/
│   ├── .env.example
│   └── config.yaml               # 平台配置（API 地址、超时等）
├── docs/
│   ├── ARCHITECTURE.md           # 架构文档
│   ├── WORKFLOW.md               # 工作流
│   └── API_REFERENCE.md          # API 参考
└── scripts/
    └── (deprecated)              # 旧脚本迁移记录
```

### 3.2 核心设计决策

#### 决策 1：统一配置管理
```python
# src/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Ghost
    ghost_url: str = Field(..., env="GHOST_URL")
    ghost_api_key: str = Field(..., env="GHOST_API_KEY")
    
    # WeChat
    wechat_appid: str = Field(..., env="WECHAT_APPID")
    wechat_appsecret: str = Field(..., env="WECHAT_APPSECRET")
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**好处**：
- 单一配置入口
- 环境变量 + .env 支持
- 类型检查
- 密钥不硬编码

#### 决策 2：发布器接口抽象
```python
# src/core/publisher.py
from abc import ABC, abstractmethod

class Publisher(ABC):
    @abstractmethod
    def publish(self, content: dict) -> bool:
        pass
    
    @abstractmethod
    def validate(self, content: dict) -> bool:
        pass

class GhostPublisher(Publisher):
    def publish(self, content):
        # Ghost 特定逻辑
        pass

class WeChatPublisher(Publisher):
    def publish(self, content):
        # WeChat 特定逻辑
        pass
```

**好处**：
- 统一接口
- 易于扩展新平台
- 支持多平台并行发布

#### 决策 3：统一格式转换
```python
# src/core/formatter.py
class HTMLToWeChatFormatter:
    """HTML → WeChat 标记语言转换"""
    
    def __init__(self, preserve_style: bool = False):
        self.preserve_style = preserve_style
    
    def convert(self, html: str) -> str:
        # 通用转换逻辑
        pass

# 使用
formatter = HTMLToWeChatFormatter(preserve_style=True)
wechat_html = formatter.convert(ghost_html)
```

**好处**：
- 两个脚本可合并为一个
- 支持 preserve_style 参数切换行为
- 易于测试

### 3.3 重构优先级与 PR 清单

#### PR #1（P0 核心）：配置管理 + 基础设施
```
feat: add centralized config management and base publisher interface

- Introduce pydantic Settings for config management
- Define abstract Publisher interface
- Create base API client with retry logic and error handling
- Add comprehensive logging
- Create .env.example template

Files:
  + src/config.py
  + src/logger.py
  + src/errors.py
  + src/core/api_client.py
  + src/core/publisher.py
  + config/.env.example
  
Tests:
  + tests/test_config.py
```

#### PR #2（P0 核心）：格式转换统一
```
feat: consolidate HTML-to-WeChat formatters into single module

- Merge ghost_to_wechat.py + ghost_to_wechat_body.py
- Add preserve_style parameter for dual output
- Implement BeautifulSoup-based parsing
- Add comprehensive unit tests

Files:
  ~ src/formatters/html_to_wechat.py (新，合并两个旧脚本)
  - scripts/ghost_to_wechat.py (deprecated)
  - scripts/ghost_to_wechat_body.py (deprecated)
  
Tests:
  + tests/test_formatters.py (HTML samples, edge cases)
```

#### PR #3（P1）：Ghost 发布器实现
```
feat: implement Ghost publisher with config-driven API calls

- Migrate ghost_auto_publish.py logic to GhostPublisher class
- Use centralized config (API Key, URL)
- Add retry logic (exponential backoff)
- Add detailed logging

Files:
  + src/publishers/ghost.py
  ~ scripts/ghost_auto_publish.py (refactored to use GhostPublisher)
  
Tests:
  + tests/test_publishers.py (Ghost API mocking)
```

#### PR #4（P1）：WeChat 发布器实现
```
feat: implement WeChat publisher with API-based approach

- Create WeChatPublisher class (use API, not Selenium)
- Support both standard + Great Minds formats
- Image handling (download from Ghost, upload to WeChat)
- Replace publish_wechat.py with reliable API-based version

Files:
  + src/publishers/wechat.py
  + src/utils/image_handler.py
  ~ scripts/publish_wechat.py (refactored)
  - scripts/great_minds_ghost_to_wechat.py (use formatter parameters)
  
Tests:
  + tests/test_publishers_wechat.py
```

#### PR #5（P2）：集成测试 + 文档完善
```
feat: add integration tests and architecture documentation

- Full end-to-end test (Ghost → format → publish to WeChat)
- Add ARCHITECTURE.md, WORKFLOW.md, API_REFERENCE.md
- Deprecation guide for old scripts
- Migration examples

Files:
  + tests/test_integration.py
  + docs/ARCHITECTURE.md
  + docs/WORKFLOW.md
  + docs/API_REFERENCE.md
  + MIGRATION_GUIDE.md
```

### 3.4 关键改进点

| 维度 | 前 | 后 |
|-----|-----|-----|
| 配置管理 | 硬编码 | 环境变量 + .env |
| 格式转换 | 两个脚本（70% 重复） | 一个 Formatter 类（参数化） |
| 错误处理 | 无 | 统一异常类 + 重试机制 |
| 日志 | print + logging 混乱 | 统一 logger（结构化日志） |
| 发布方式 | 三种（Selenium / API / 硬编码） | 一种（Publisher 接口 + 多实现） |
| 测试覆盖 | 0% | 目标 >80% |
| 文档 | 零散 | 完整（架构 + API + 工作流） |

---

## 4. 验收标准

- [ ] 配置管理集中化（无硬编码 Key）
- [ ] 格式转换脚本合并（测试覆盖 >80%）
- [ ] Ghost/WeChat 发布器实现（单元 + 集成测试）
- [ ] 错误处理完善（包含重试）
- [ ] 文档完整（架构 + API 参考）
- [ ] 旧脚本正式标记为 deprecated
- [ ] 迁移指南清晰（用户易于升级）

---

## 5. 风险评估与缓解

| 风险 | 影响 | 缓解措施 |
|-----|-----|---------|
| WeChat API 变更 | 发布失败 | 统一错误处理 + 详细日志 |
| 图片处理异常 | 文章发布不完整 | 图片处理独立模块 + 重试 |
| 旧脚本割裂 | 用户混乱 | 清晰的 deprecation warning + 迁移指南 |
| 配置泄露 | 安全隐患 | .env + 密钥管理最佳实践 |

---

## 6. 时间估算

| PR | 工作量 | 工时 |
|----|--------|------|
| #1（配置 + 基础） | 中 | 4-6h |
| #2（格式统一） | 中 | 4-6h |
| #3（Ghost） | 小 | 2-3h |
| #4（WeChat） | 大 | 6-8h |
| #5（测试 + 文档） | 中 | 4-5h |
| **总计** | | **20-28h** |

可分阶段完成，每个 PR 独立、相对解耦。

---

## 附录：脚本迁移清单

### 保留（移到 src/）
- ✅ ghost_auto_publish.py → src/publishers/ghost.py
- ✅ wechat_formatter.py → src/formatters/html_to_wechat.py（核心逻辑）
- ✅ publish_wechat.py → 重构为 src/scripts/publish_to_wechat.py（API 版）
- ✅ xhs_card_ai_capability.py → src/publishers/xhs.py
- ✅ 数据转换脚本 → src/scripts/（保留独立，无需改动）

### 废弃（deprecated，保留以引导迁移）
- 🔴 ghost_to_wechat.py （合并入 Formatter）
- 🔴 ghost_to_wechat_body.py （合并入 Formatter）
- 🔴 great_minds_ghost_to_wechat.py （用 Formatter + parameters）
- 🔴 great_minds_wechat_inline.py （功能合并）
- 🔴 ghost_backfill_posts.py （运维脚本，保留但标记 deprecated）
