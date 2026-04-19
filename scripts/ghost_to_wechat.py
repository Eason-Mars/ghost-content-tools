#!/usr/bin/env python3
"""
Ghost to WeChat Converter v1.0
将 Ghost 格式的 HTML 文章转换为微信公众号兼容的内联样式 HTML。

Usage:
  python3 ghost_to_wechat.py <ghost_html_file> [--title TITLE] [--author AUTHOR] [--output FILE] [--publish]

功能:
- 提取 Ghost HTML 的主要内容
- 剥掉 Ghost CSS class，转为微信兼容的内联样式
- 保留图片、引用、标题等语义结构
- 自动加 Hero 头部和 Closing 尾部
- 可选直接推送到微信草稿箱
"""

import re
import html as html_module
from pathlib import Path
import argparse

# 复用 wechat_formatter 的样式常量
from wechat_formatter import (
    BRAND_RED, BRAND_DARK, BRAND_GOLD, BRAND_BG, FF,
    S_BODY, S_HERO, S_HERO_TITLE, S_META, S_META_LABEL,
    S_PAGE, S_LEAD, S_H2, S_H3, S_P, S_BQ, S_HIGHLIGHT,
    S_IMG_CAPTION, S_IMG_WRAPPER, S_IMG, S_UL, S_LI, S_HR,
    S_STRONG, S_CODE, S_CLOSING, S_CLOSING_NAME, S_CLOSING_CREDS, S_CLOSING_TAG,
    esc
)


def extract_body_content(html_text):
    """提取 HTML 的主要内容区域"""
    # 尝试提取 Ghost 的 post-content 区域
    patterns = [
        r'<div[^>]*class="[^"]*post-content[^"]*"[^>]*>(.*?)</div>',
        r'<article[^>]*>(.*?)</article>',
        r'<main[^>]*>(.*?)</main>',
        r'<body[^>]*>(.*?)</body>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
    
    # 如果都没匹配到，返回整个内容
    return html_text


def strip_tags_keep_content(html_text, tag):
    """移除指定标签但保留内容"""
    pattern = rf'<{tag}[^>]*>(.*?)</{tag}>'
    return re.sub(pattern, r'\1', html_text, flags=re.DOTALL | re.IGNORECASE)


def convert_ghost_to_wechat(html_text, title="", author="Eason", source=""):
    """将 Ghost HTML 转换为微信内联样式 HTML"""
    
    # 提取主要内容
    content = extract_body_content(html_text)
    
    # 移除 script 和 style 标签
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除所有 class 和 id 属性
    content = re.sub(r'\s+class="[^"]*"', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\s+id="[^"]*"', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\s+data-[a-z-]+="[^"]*"', '', content, flags=re.IGNORECASE)
    
    parts = []
    
    # ── Hero 头部 ──
    if title:
        parts.append(
            f'<section style="{S_HERO}">'
            f'<p style="{S_HERO_TITLE}">{esc(title)}</p>'
            '</section>'
        )
    
    # ── 元信息区 ──
    meta_parts = []
    if author:
        meta_parts.append(f'<span style="{S_META_LABEL}">文｜</span>{esc(author)}')
    if source:
        meta_parts.append(f'<span style="{S_META_LABEL}">来源｜</span>{esc(source)}')
    if meta_parts:
        parts.append(f'<section style="{S_META}">{" · ".join(meta_parts)}</section>')
    
    # ── 内容区 ──
    parts.append(f'<section style="{S_PAGE}">')
    
    # 转换各种元素
    
    # H1 → H2 样式
    content = re.sub(
        r'<h1[^>]*>(.*?)</h1>',
        rf'<section style="{S_H2}">\1</section>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # H2
    content = re.sub(
        r'<h2[^>]*>(.*?)</h2>',
        rf'<section style="{S_H2}">\1</section>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # H3
    content = re.sub(
        r'<h3[^>]*>(.*?)</h3>',
        rf'<section style="{S_H3}">\1</section>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # H4-H6 → H3 样式
    content = re.sub(
        r'<h[456][^>]*>(.*?)</h[456]>',
        rf'<section style="{S_H3}">\1</section>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Blockquote
    content = re.sub(
        r'<blockquote[^>]*>(.*?)</blockquote>',
        rf'<section style="{S_BQ}">\1</section>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # 段落
    content = re.sub(
        r'<p[^>]*>(.*?)</p>',
        rf'<section style="{S_P}">\1</section>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # 图片
    def convert_img(match):
        img_tag = match.group(0)
        # 提取 src
        src_match = re.search(r'src="([^"]+)"', img_tag)
        alt_match = re.search(r'alt="([^"]*)"', img_tag)
        src = src_match.group(1) if src_match else ""
        alt = alt_match.group(1) if alt_match else ""
        
        result = f'<section style="{S_IMG_WRAPPER}">'
        result += f'<img src="{src}" alt="{esc(alt)}" style="{S_IMG}">'
        result += '</section>'
        
        # 如果有 alt 文字，作为图片说明
        if alt:
            result += f'<section style="{S_IMG_CAPTION}">{esc(alt)}</section>'
        
        return result
    
    content = re.sub(r'<img[^>]+>', convert_img, content, flags=re.IGNORECASE)
    
    # 列表
    content = re.sub(
        r'<ul[^>]*>',
        f'<section style="{S_UL}">',
        content, flags=re.IGNORECASE
    )
    content = re.sub(r'</ul>', '</section>', content, flags=re.IGNORECASE)
    
    content = re.sub(
        r'<li[^>]*>(.*?)</li>',
        rf'<section style="{S_LI}">• \1</section>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # 有序列表转无序（微信对 ol 支持不好）
    content = re.sub(
        r'<ol[^>]*>',
        f'<section style="{S_UL}">',
        content, flags=re.IGNORECASE
    )
    content = re.sub(r'</ol>', '</section>', content, flags=re.IGNORECASE)
    
    # 分隔线
    content = re.sub(
        r'<hr[^>]*>',
        f'<section style="{S_HR}"></section>',
        content, flags=re.IGNORECASE
    )
    
    # Strong
    content = re.sub(
        r'<strong[^>]*>(.*?)</strong>',
        rf'<strong style="{S_STRONG}">\1</strong>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    content = re.sub(
        r'<b[^>]*>(.*?)</b>',
        rf'<strong style="{S_STRONG}">\1</strong>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Em/Italic
    content = re.sub(
        r'<em[^>]*>(.*?)</em>',
        r'<em style="color:rgb(85,85,85);font-style:italic;">\1</em>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    content = re.sub(
        r'<i[^>]*>(.*?)</i>',
        r'<em style="color:rgb(85,85,85);font-style:italic;">\1</em>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Code
    content = re.sub(
        r'<code[^>]*>(.*?)</code>',
        rf'<code style="{S_CODE}">\1</code>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # 移除 figure/figcaption 标签但保留内容
    content = strip_tags_keep_content(content, 'figure')
    content = re.sub(
        r'<figcaption[^>]*>(.*?)</figcaption>',
        rf'<section style="{S_IMG_CAPTION}">\1</section>',
        content, flags=re.DOTALL | re.IGNORECASE
    )
    
    # 移除其他常见包装标签
    for tag in ['div', 'span', 'article', 'main', 'header', 'footer', 'nav', 'aside']:
        content = strip_tags_keep_content(content, tag)
    
    # 移除空白标签
    content = re.sub(r'<section[^>]*>\s*</section>', '', content)
    
    # 清理多余空白
    content = re.sub(r'\n\s*\n', '\n', content)
    content = content.strip()
    
    parts.append(content)
    parts.append('</section>')  # 关闭内容区
    
    # ── Closing 尾部签名 ──
    parts.append(
        f'<section style="{S_CLOSING}">'
        f'<p style="{S_CLOSING_NAME}">我叫 Eason</p>'
        f'<p style="{S_CLOSING_CREDS}">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</p>'
        f'<p style="{S_CLOSING_TAG}">在东京经营几家餐厅，用AI做投资研究和餐饮零售管理——然后把踩过的坑写出来</p>'
        '</section>'
    )
    
    return f'<section style="{S_BODY}">\n' + "\n".join(parts) + '\n</section>'


def convert_file(input_path, output_path=None, title="", author="Eason", source=""):
    """转换 Ghost HTML 文件为微信 HTML"""
    html_text = Path(input_path).read_text(encoding="utf-8")
    
    # 如果没有指定标题，尝试从 HTML 中提取
    if not title:
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
    
    wechat_html = convert_ghost_to_wechat(html_text, title=title, author=author, source=source)
    
    if output_path is None:
        output_path = Path(input_path).with_suffix(".wechat.html")
    
    Path(output_path).write_text(wechat_html, encoding="utf-8")
    print(f"✅ Converted: {output_path} ({len(wechat_html)} chars)")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ghost → WeChat HTML 转换器 v1.0")
    parser.add_argument("file", help="Ghost HTML 文件")
    parser.add_argument("--title", default="", help="文章标题（不指定则从 HTML 提取）")
    parser.add_argument("--author", default="Eason", help="作者名")
    parser.add_argument("--source", default="", help="来源")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    parser.add_argument("--publish", action="store_true", help="转换后直接推送到微信草稿箱")
    args = parser.parse_args()
    
    # 转换
    output_path = convert_file(
        args.file, 
        args.output, 
        title=args.title, 
        author=args.author, 
        source=args.source
    )
    
    # 如果需要发布
    if args.publish:
        import subprocess
        title = args.title or Path(args.file).stem
        cmd = [
            "python3", str(Path(__file__).parent / "publish_wechat.py"),
            str(output_path),
            "--title", title,
            "--author", args.author,
        ]
        print(f"\n📤 Publishing to WeChat...")
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
