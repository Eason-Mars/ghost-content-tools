#!/usr/bin/env python3
"""
WeChat Official Account HTML Formatter v2.0
Convert markdown to WeChat-compatible HTML with inline styles.
对标36氪/智能涌现排版标准，保持 Eason 品牌色体系。

升级内容 (v2.0):
- 正文 15px / line-height 2.0 / letter-spacing 0.544px
- 左右边距统一 16px
- 新增图片说明、元信息区、核心观点卡片样式
- 优化 blockquote 和 strong 样式
"""

import re
import html as html_module
from pathlib import Path

# ── 品牌色 ─────────────────────────────────────────────────────────────
BRAND_RED = '#8B3A2A'       # 棕红主色
BRAND_DARK = '#6B2A1A'      # 深棕
BRAND_GOLD = '#C5963A'      # 金色
BRAND_BG = '#FAF5F3'        # 浅粉背景

# ── 字体 ─────────────────────────────────────────────────────────────
FF = '-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",Georgia,serif'

# ── 基础样式（对标36氪：15px / line-height 2.0 / letter-spacing 0.544px）──
S_BODY = (
    f'font-family:{FF};font-size:15px;line-height:2.0;'
    'color:rgba(0,0,0,0.9);letter-spacing:0.544px;'
)

# ── Hero 头部（棕红标题 + 底部分隔线）──
S_HERO = (
    'text-align:center;padding:32px 16px 24px;'
    f'border-bottom:2px solid {BRAND_RED};margin-bottom:24px;'
)
S_HERO_TITLE = (
    f'font-size:22px;font-weight:800;line-height:1.4;'
    f'color:{BRAND_RED};margin:0 auto;text-align:center;'
)

# ── 元信息区（作者｜来源，13px 右对齐）──
S_META = (
    'font-size:13px;color:#666;text-align:right;'
    'margin:0 16px 24px;line-height:1.8;letter-spacing:0.5px;'
)
S_META_LABEL = 'font-weight:700;color:#666;'

# ── 内容区 ──
S_PAGE = (
    f'font-family:{FF};font-size:15px;line-height:2.0;'
    'color:rgba(0,0,0,0.9);padding:0 16px 48px;letter-spacing:0.544px;'
)

# ── 首段（视觉区分）──
S_LEAD = (
    'font-size:15px;color:rgb(85,85,85);margin:0 0 24px;'
    'padding-bottom:24px;border-bottom:1px solid rgb(233,233,231);'
    'line-height:2.0;letter-spacing:0.544px;text-align:justify;'
)

# ── H2 标题（加粗 + 棕红左边框）──
S_H2 = (
    f'font-size:18px;color:rgba(0,0,0,0.9);margin:36px 0 16px;'
    f'padding-left:14px;border-left:4px solid {BRAND_RED};'
    'font-weight:800;line-height:1.75;'
)

# ── H3 标题 ──
S_H3 = (
    f'font-size:16px;color:{BRAND_DARK};margin:28px 0 10px;'
    'font-weight:700;line-height:1.75;'
)

# ── 正文段落 ──
S_P = (
    'margin:0 0 24px;font-size:15px;line-height:2.0;'
    'letter-spacing:0.544px;text-align:justify;'
)

# ── 引用块（对标36氪：灰色左边框 + 浅色文字）──
S_BQ = (
    f'border-left:3px solid {BRAND_RED};padding:12px 20px;'
    f'margin:24px 0;background:{BRAND_BG};color:rgba(0,0,0,0.55);'
    'font-size:15px;line-height:2.0;letter-spacing:0.544px;'
)

# ── 核心观点高亮卡片（新增）──
S_HIGHLIGHT = (
    f'background:{BRAND_BG};border-left:4px solid {BRAND_RED};'
    'padding:16px 20px;margin:24px 0;font-size:15px;'
    'color:rgba(0,0,0,0.8);line-height:2.0;letter-spacing:0.544px;'
)

# ── 图片说明（新增：13px 灰色居中）──
S_IMG_CAPTION = (
    'font-size:13px;color:#999;text-align:center;'
    'margin:4px 0 24px;line-height:1.6;letter-spacing:0.5px;'
)

# ── 图片容器 ──
S_IMG_WRAPPER = 'text-align:center;margin:24px 0 4px;'
S_IMG = 'max-width:100%;height:auto;'

# ── 列表 ──
S_UL = 'margin:0 0 24px 1.6em;'
S_LI = 'margin-bottom:8px;line-height:2.0;letter-spacing:0.544px;'

# ── 分隔线 ──
S_HR = 'border:none;border-top:1px solid rgb(224,219,216);margin:32px 0;'

# ── 加粗（正文中保持黑色，不用品牌色��──
S_STRONG = 'color:#1a1a1a;font-weight:700;'

# ── 行内代码 ──
S_CODE = (
    f'background:rgb(245,243,240);padding:2px 5px;font-size:14px;'
    f'color:{BRAND_RED};font-family:Menlo,Consolas,monospace;'
)

# ── Closing 尾部签名 ──
S_CLOSING = (
    f'border-top:2px solid {BRAND_RED};'
    f'border-bottom:2px solid {BRAND_RED};'
    'padding:20px 16px;margin-top:36px;'
)
S_CLOSING_NAME = f'font-size:18px;font-weight:800;margin-bottom:6px;color:{BRAND_RED};'
S_CLOSING_CREDS = (
    'font-size:12px;color:#999;line-height:1.75;'
    'margin-bottom:6px;font-family:Arial,sans-serif;letter-spacing:0.5px;'
)
S_CLOSING_TAG = 'font-size:13px;color:#666;line-height:1.75;'


def esc(text):
    """HTML 转义"""
    return html_module.escape(text)


def process_inline(text):
    """处理行内格式：加粗、斜体、行内代码"""
    text = esc(text)
    # 加粗
    text = re.sub(r'\*\*(.+?)\*\*', rf'<strong style="{S_STRONG}">\1</strong>', text)
    # 斜体
    text = re.sub(r'\*(.+?)\*', r'<em style="color:rgb(85,85,85);font-style:italic;">\1</em>', text)
    # 行内代码
    text = re.sub(r'`(.+?)`', rf'<code style="{S_CODE}">\1</code>', text)
    return text


def md_to_wechat(md_text, title="", author="Eason", source="", date=""):
    """
    将 Markdown 转换为微信公众号兼容的内联样式 HTML
    
    参数:
        md_text: Markdown 文本
        title: 文章标题
        author: 作者名
        source: 来源（可选）
        date: 日期（可选）
    """
    lines = md_text.strip().split("\n")
    parts = []
    in_ul = False
    is_first_paragraph = True
    pending_image = None  # 用于处理图片说明

    # ── Hero 头部 ──
    if title:
        parts.append(
            f'<section style="{S_HERO}">'
            f'<p style="{S_HERO_TITLE}">{esc(title)}</p>'
            '</section>'
        )

    # ── 元信息区（作者｜来源）──
    meta_parts = []
    if author:
        meta_parts.append(f'<span style="{S_META_LABEL}">文｜</span>{esc(author)}')
    if source:
        meta_parts.append(f'<span style="{S_META_LABEL}">来源｜</span>{esc(source)}')
    if date:
        meta_parts.append(f'{esc(date)}')
    if meta_parts:
        parts.append(f'<section style="{S_META}">{" · ".join(meta_parts)}</section>')

    # ── 内容区 ──
    parts.append(f'<section style="{S_PAGE}">')

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        i += 1

        # 空行
        if not s:
            if in_ul:
                parts.append('</section>')
                in_ul = False
            continue

        # 图片：![alt](url)
        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', s)
        if img_match:
            alt_text = img_match.group(1)
            img_url = img_match.group(2)
            parts.append(
                f'<section style="{S_IMG_WRAPPER}">'
                f'<img src="{esc(img_url)}" alt="{esc(alt_text)}" style="{S_IMG}">'
                '</section>'
            )
            # 检查下一行是否是图片说明（斜体行）
            if i < len(lines):
                next_line = lines[i].strip()
                caption_match = re.match(r'^\*([^*]+)\*$', next_line)
                if caption_match:
                    caption = caption_match.group(1)
                    parts.append(f'<section style="{S_IMG_CAPTION}">{esc(caption)}</section>')
                    i += 1
            continue

        # H2
        if s.startswith("## "):
            parts.append(f'<section style="{S_H2}">{process_inline(s[3:])}</section>')
            continue

        # H3
        if s.startswith("### "):
            parts.append(f'<section style="{S_H3}">{process_inline(s[4:])}</section>')
            continue

        # H1（如果已有 Hero 标题则跳过，避免重复）
        if s.startswith("# "):
            if not title:
                parts.append(f'<section style="{S_H2}">{process_inline(s[2:])}</section>')
            continue

        # 分隔线
        if s in ("---", "***", "___"):
            parts.append(f'<section style="{S_HR}"></section>')
            continue

        # 核心观点高亮卡片：> ! 开头
        if s.startswith("> !"):
            hl_lines = [s[3:].strip()]
            while i < len(lines) and lines[i].strip().startswith("> "):
                line = lines[i].strip()
                if line.startswith("> !"):
                    hl_lines.append(line[3:].strip())
                else:
                    hl_lines.append(line[2:].strip())
                i += 1
            content = "<br>".join(process_inline(l) for l in hl_lines)
            parts.append(f'<section style="{S_HIGHLIGHT}">{content}</section>')
            continue

        # 引用块
        if s.startswith("> "):
            bq_lines = [s[2:]]
            while i < len(lines) and lines[i].strip().startswith("> "):
                bq_lines.append(lines[i].strip()[2:])
                i += 1
            content = "<br>".join(process_inline(l) for l in bq_lines)
            parts.append(f'<section style="{S_BQ}">{content}</section>')
            continue

        # 无序列表
        if s.startswith("- ") or s.startswith("• "):
            if not in_ul:
                parts.append(f'<section style="{S_UL}">')
                in_ul = True
            parts.append(f'<section style="{S_LI}">• {process_inline(s[2:])}</section>')
            continue

        # 有序列表
        ol_match = re.match(r'^(\d+)\.\s+(.+)$', s)
        if ol_match:
            num = ol_match.group(1)
            text = ol_match.group(2)
            parts.append(f'<section style="{S_P}">{num}. {process_inline(text)}</section>')
            continue

        # 普通段落
        if is_first_paragraph:
            parts.append(f'<section style="{S_LEAD}">{process_inline(s)}</section>')
            is_first_paragraph = False
        else:
            parts.append(f'<section style="{S_P}">{process_inline(s)}</section>')

    if in_ul:
        parts.append('</section>')

    parts.append('</section>')  # 关闭内容区

    # ── Closing 尾部签名 ──
    parts.append(
        f'<section style="{S_CLOSING}">'
        f'<p style="{S_CLOSING_NAME}">我叫 Eason</p>'
        f'<p style="{S_CLOSING_CREDS}">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</p>'
        f'<p style="{S_CLOSING_TAG}">在东京经营几家餐厅，用AI做投资研究和餐饮零售管理——然后把踩过的坑写出来</p>'
        '</section>'
    )

    inner = f'<section style="{S_BODY}">\n' + "\n".join(parts) + '\n</section>'
    return inner


def wrap_standalone(html_content):
    """包装为完整 HTML 文件（带 charset 声明，防乱码）"""
    return (
        '<!DOCTYPE html>\n'
        '<html>\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '</head>\n<body style="margin:0;padding:20px;background:#fff;">\n'
        f'{html_content}\n'
        '</body>\n</html>'
    )


def embed_local_images(html_content, base_dir):
    """将本地图片嵌入为 base64 data URI（防止打开时图片丢失）"""
    import base64
    
    mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp'}
    
    def replace_src(match):
        full = match.group(0)
        src = match.group(1)
        if src.startswith(('http://', 'https://', 'data:')):
            return full
        img_path = Path(base_dir) / src
        if not img_path.exists():
            return full
        mime = mime_map.get(img_path.suffix.lower(), 'image/png')
        b64 = base64.b64encode(img_path.read_bytes()).decode()
        return full.replace(src, f'data:{mime};base64,{b64}')
    
    return re.sub(r'<img[^>]+src="([^"]+)"', replace_src, html_content)


def convert_file(input_path, output_path=None, title="", author="Eason", source="", date=""):
    """转换 Markdown 文件为微信 HTML"""
    md = Path(input_path).read_text(encoding="utf-8")
    html_out = md_to_wechat(md, title=title, author=author, source=source, date=date)
    # 嵌入本地图片为 base64
    html_out = embed_local_images(html_out, Path(input_path).parent)
    # 文件输出时包装完整 HTML（防乱码）
    html_out = wrap_standalone(html_out)
    if output_path is None:
        output_path = Path(input_path).with_suffix(".wechat.html")
    Path(output_path).write_text(html_out, encoding="utf-8")
    print(f"✅ Converted: {output_path} ({len(html_out)} chars)")
    return output_path


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Markdown → WeChat HTML 转换器 v2.0")
    p.add_argument("file", help="输入的 Markdown 文件")
    p.add_argument("--title", default="", help="文章标题")
    p.add_argument("--author", default="Eason", help="作者名")
    p.add_argument("--source", default="", help="来源")
    p.add_argument("--date", default="", help="日期")
    p.add_argument("--output", "-o", default=None, help="输出文件路径")
    a = p.parse_args()
    convert_file(a.file, a.output, title=a.title, author=a.author, source=a.source, date=a.date)
