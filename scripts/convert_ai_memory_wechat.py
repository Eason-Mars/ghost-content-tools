#!/usr/bin/env python3
"""
专用微信转换器：ai-team-memory-system
使用 wechat_formatter 的标准样式体系（与 ghost_to_wechat.py 一致）
处理自定义组件：step-card / pre.code-block / analogy / alert-grid / faq-item
"""

import sys, re
from pathlib import Path
from bs4 import BeautifulSoup

# 复用官方样式常量
from wechat_formatter import (
    BRAND_RED, BRAND_DARK, BRAND_GOLD, BRAND_BG, FF,
    S_BODY, S_HERO, S_HERO_TITLE, S_META, S_META_LABEL,
    S_PAGE, S_LEAD, S_H2, S_H3, S_P, S_BQ, S_HIGHLIGHT,
    S_IMG_CAPTION, S_IMG_WRAPPER, S_IMG, S_UL, S_LI, S_HR,
    S_STRONG, S_CODE, S_CLOSING, S_CLOSING_NAME, S_CLOSING_CREDS, S_CLOSING_TAG,
    esc
)

FF_MONO = "'SF Mono', 'Fira Code', Consolas, monospace"

# ── 自定义组件样式（对齐标准体系）──────────────────────────────────
def s(d): return "; ".join(f"{k}:{v}" for k, v in d.items())

S_STEP_CARD   = s({"border": f"1px solid #e0dbd8", "border-radius": "8px", "padding": "20px 22px", "margin": "24px 0"})
S_STEP_NUM    = s({"background": BRAND_RED, "color": "#fff", "font-size": "13px", "font-weight": "800",
                   "font-family": "Arial,sans-serif", "width": "34px", "height": "34px",
                   "border-radius": "50%", "display": "inline-block", "text-align": "center",
                   "line-height": "34px", "vertical-align": "middle", "margin-right": "12px", "flex-shrink": "0"})
S_STEP_TITLE  = s({"font-size": "17px", "font-weight": "800", "color": "#1a1a1a", "vertical-align": "middle"})
S_STEP_SUB    = s({"font-size": "12px", "color": "#888", "font-family": "Arial,sans-serif", "margin": "4px 0 14px"})
S_STEP_WHY    = s({"background": "#faf5f3", "border-left": f"3px solid {BRAND_GOLD}",
                   "padding": "10px 14px", "border-radius": "0 5px 5px 0",
                   "margin": "0 0 14px", "font-size": "14px", "color": "#555", "line-height": "1.8"})
S_ANALOGY     = s({"background": BRAND_BG, "border-radius": "8px", "padding": "16px 20px",
                   "margin": "18px 0", "font-size": "14px", "color": "#444", "line-height": "1.85"})
S_ANALOGY_LBL = s({"font-size": "11px", "letter-spacing": "2px", "color": BRAND_RED,
                   "font-family": "Arial,sans-serif", "font-weight": "700", "margin-bottom": "6px"})
S_ALERT_RED   = s({"padding": "10px 14px", "border-radius": "6px", "font-size": "14px",
                   "line-height": "1.75", "background": "#fce8e8", "border": "1px solid #f5a8a8", "margin-bottom": "8px"})
S_ALERT_YLW   = s({"padding": "10px 14px", "border-radius": "6px", "font-size": "14px",
                   "line-height": "1.75", "background": "#fffbe6", "border": "1px solid #ffe58f", "margin-bottom": "8px"})
S_ALERT_GRN   = s({"padding": "10px 14px", "border-radius": "6px", "font-size": "14px",
                   "line-height": "1.75", "background": "#f0faf4", "border": "1px solid #86c57a", "margin-bottom": "8px"})
S_CODE_BLOCK  = s({"background": "#1e1e1e", "color": "#d4d4d4", "border-radius": "8px",
                   "padding": "14px 16px", "margin": "12px 0 4px", "font-family": FF_MONO,
                   "font-size": "12px", "line-height": "1.8", "overflow-x": "auto",
                   "white-space": "pre-wrap", "word-break": "break-word"})
S_CODE_NOTE   = s({"font-size": "13px", "color": "#666", "line-height": "1.7", "margin": "0 0 14px"})
S_RESULT      = s({"background": "#f0faf4", "border": "1px solid #86c57a",
                   "border-radius": "8px", "padding": "14px 18px", "margin": "16px 0"})
S_RESULT_LBL  = s({"font-size": "11px", "letter-spacing": "2px", "color": "#2d7a47",
                   "font-family": "Arial,sans-serif", "font-weight": "700", "margin-bottom": "6px"})
S_RESULT_P    = s({"margin": "0", "font-size": "14px", "line-height": "1.85"})
S_FAQ_ITEM    = s({"border-bottom": "1px solid #e9e9e7", "padding": "16px 0"})
S_FAQ_Q       = s({"font-weight": "800", "font-size": "15px", "color": "#1a1a1a", "margin-bottom": "6px"})
S_FAQ_A       = s({"font-size": "14px", "color": "#555", "line-height": "1.85"})
S_TOC         = s({"background": BRAND_BG, "border-radius": "8px", "padding": "16px 20px", "margin": "0 0 28px"})
S_TOC_TTL     = s({"font-size": "11px", "letter-spacing": "2px", "color": BRAND_RED,
                   "font-family": "Arial,sans-serif", "font-weight": "700", "margin-bottom": "10px"})
S_TOC_LI      = s({"font-size": "14px", "margin-bottom": "4px", "color": "#555"})
S_BADGE       = s({"display": "inline-block", "background": "#e0dbd8", "color": "#666",
                   "font-size": "11px", "padding": "2px 8px", "border-radius": "10px",
                   "font-family": "Arial,sans-serif", "font-weight": "700",
                   "margin-left": "6px", "vertical-align": "middle"})
S_NOTE_BOX    = s({"background": BRAND_BG, "border": f"1px solid #d4b5aa",
                   "border-radius": "6px", "padding": "14px 18px", "margin": "20px 0",
                   "font-size": "14px", "color": "#555", "line-height": "1.85"})


def render_node(node):
    if not hasattr(node, 'name') or node.name is None:
        return str(node)

    cls = node.get("class", [])
    tag = node.name

    # ── code-note（p 标签前判断）─────────────────────────────
    if "code-note" in cls:
        return f'<p style="{S_CODE_NOTE}">{node.get_text(strip=True)}</p>'

    # ── p ────────────────────────────────────────────────────
    if tag == "p":
        inner = node.decode_contents()
        inner = re.sub(r'<strong>(.*?)</strong>', rf'<strong style="{S_STRONG}">\1</strong>', inner)
        inner = re.sub(r'<code>(.*?)</code>', rf'<code style="{S_CODE}">\1</code>', inner)
        return f'<section style="{S_P}">{inner}</section>'

    # ── lead ─────────────────────────────────────────────────
    if "lead" in cls:
        inner = "".join(render_node(c) for c in node.children)
        return f'<section style="{S_LEAD}">{inner}</section>'

    # ── TOC ──────────────────────────────────────────────────
    if "toc" in cls:
        ttl = node.find(class_="toc-title")
        ol = node.find("ol")
        ttl_html = f'<p style="{S_TOC_TTL}">{ttl.get_text(strip=True)}</p>' if ttl else ""
        items_html = ""
        if ol:
            for li in ol.find_all("li", recursive=False):
                items_html += f'<p style="{S_TOC_LI}">• {li.get_text(strip=True)}</p>'
        return f'<section style="{S_TOC}">{ttl_html}{items_html}</section>'

    # ── h2 ───────────────────────────────────────────────────
    if tag == "h2":
        for span in node.find_all("span", class_="label"):
            span.decompose()
        return f'<section style="{S_H2}">{node.get_text(strip=True)}</section>'

    # ── h3 ───────────────────────────────────────────────────
    if tag == "h3":
        return f'<p style="{S_H3}">{node.get_text(strip=True)}</p>'

    # ── ul/ol ─────────────────────────────────────────────────
    if tag in ("ul", "ol"):
        items = "".join(
            f'<li style="{S_LI}">{li.decode_contents()}</li>'
            for li in node.find_all("li", recursive=False)
        )
        return f'<ul style="{S_UL}">{items}</ul>'

    # ── blockquote ───────────────────────────────────────────
    if tag == "blockquote":
        return f'<section style="{S_BQ}">{node.get_text(strip=True)}</section>'

    # ── hr ───────────────────────────────────────────────────
    if tag == "hr":
        return f'<hr style="{S_HR}">'

    # ── note-box ─────────────────────────────────────────────
    if "note-box" in cls:
        inner = node.decode_contents()
        inner = re.sub(r'<strong>(.*?)</strong>', rf'<strong style="color:{BRAND_RED};font-weight:700">\1</strong>', inner)
        return f'<section style="{S_NOTE_BOX}">{inner}</section>'

    # ── analogy ──────────────────────────────────────────────
    if "analogy" in cls:
        lbl = node.find(class_="analogy-label")
        lbl_html = f'<p style="{S_ANALOGY_LBL}">{lbl.get_text(strip=True)}</p>' if lbl else ""
        if lbl: lbl.decompose()
        return f'<section style="{S_ANALOGY}">{lbl_html}<p style="margin:0">{node.get_text(strip=True)}</p></section>'

    # ── alert-grid ───────────────────────────────────────────
    if "alert-grid" in cls:
        items_html = ""
        for item in node.find_all(class_="alert-item"):
            ic = item.get("class", [])
            st = S_ALERT_RED if "alert-red" in ic else (S_ALERT_GRN if "alert-green" in ic else S_ALERT_YLW)
            inner = item.decode_contents()
            inner = re.sub(r'<strong>(.*?)</strong>', rf'<strong style="font-weight:700">\1</strong>', inner)
            items_html += f'<section style="{st}">{inner}</section>'
        return f'<section style="margin:18px 0">{items_html}</section>'

    # ── pre.code-block ───────────────────────────────────────
    if tag == "pre" and "code-block" in cls:
        text = node.get_text()
        from html import escape
        return f'<pre style="{S_CODE_BLOCK}">{escape(text)}</pre>'

    # ── step-card ────────────────────────────────────────────
    if "step-card" in cls:
        inner_parts = []
        header = node.find(class_="step-header")
        if header:
            num_el   = header.find(class_="step-num")
            title_el = header.find(class_="step-title")
            sub_el   = header.find(class_="step-subtitle")
            num_html   = f'<span style="{S_STEP_NUM}">{num_el.get_text(strip=True)}</span>' if num_el else ""
            title_html = f'<span style="{S_STEP_TITLE}">{title_el.get_text(strip=True)}</span>' if title_el else ""
            sub_html   = f'<p style="{S_STEP_SUB}">{sub_el.get_text(strip=True)}</p>' if sub_el else ""
            inner_parts.append(f'<p style="margin:0 0 4px">{num_html}{title_html}</p>{sub_html}')
            header.decompose()
        why = node.find(class_="step-why")
        if why:
            strong = why.find("strong")
            strong_txt = strong.get_text(strip=True) if strong else ""
            if strong: strong.decompose()
            body = why.get_text(strip=True)
            inner_parts.append(f'<section style="{S_STEP_WHY}"><strong style="color:{BRAND_RED};font-weight:700">{strong_txt}</strong> {body}</section>')
            why.decompose()
        for child in node.children:
            rendered = render_node(child)
            if rendered and rendered.strip():
                inner_parts.append(rendered)
        return f'<section style="{S_STEP_CARD}">{"".join(inner_parts)}</section>'

    # ── result-box ───────────────────────────────────────────
    if "result-box" in cls:
        lbl = node.find(class_="result-label")
        lbl_html = f'<p style="{S_RESULT_LBL}">{lbl.get_text(strip=True)}</p>' if lbl else ""
        if lbl: lbl.decompose()
        return f'<section style="{S_RESULT}">{lbl_html}<p style="{S_RESULT_P}">{node.get_text(strip=True)}</p></section>'

    # ── faq-item ─────────────────────────────────────────────
    if "faq-item" in cls:
        q_el = node.find(class_="faq-q")
        a_el = node.find(class_="faq-a")
        q_html = f'<p style="{S_FAQ_Q}">{q_el.get_text(strip=True)}</p>' if q_el else ""
        a_html = f'<p style="{S_FAQ_A}">{a_el.get_text(strip=True)}</p>' if a_el else ""
        return f'<section style="{S_FAQ_ITEM}">{q_html}{a_html}</section>'

    # ── closing ──────────────────────────────────────────────
    if "closing" in cls:
        return (
            f'<section style="{S_CLOSING}">'
            f'<p style="{S_CLOSING_NAME}">我叫 Eason</p>'
            f'<p style="{S_CLOSING_CREDS}">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</p>'
            f'<p style="{S_CLOSING_TAG}">在东京经营几家餐厅，用AI做投资研究和餐饮零售管理——然后把踩过的坑写出来</p>'
            '</section>'
        )

    # ── site-footer → 跳过 ───────────────────────────────────
    if "site-footer" in cls:
        return ""

    # ── x-box → 跳过 ─────────────────────────────────────────
    if "x-box" in cls:
        return ""

    # ── badge ────────────────────────────────────────────────
    if "badge" in cls:
        return f'<span style="{S_BADGE}">{node.get_text(strip=True)}</span>'

    # ── 默认递归 ──────────────────────────────────────────────
    return "".join(render_node(c) for c in node.children)


def convert(src: str) -> str:
    soup = BeautifulSoup(src, "html.parser")
    page = soup.find(class_="page")
    if not page:
        return src

    # Hero → 标准格式（棕红标题 + 分隔线 + 作者行）
    hero = soup.find(class_="hero")
    title_txt = ""
    if hero:
        h1 = hero.find("h1")
        title_txt = h1.get_text(strip=True) if h1 else ""

    hero_html = (
        f'<section style="{S_HERO}">'
        f'<p style="{S_HERO_TITLE}">{esc(title_txt)}</p>'
        '</section>'
        f'<section style="{S_META}"><span style="{S_META_LABEL}">文｜</span>Eason</section>'
    ) if title_txt else ""

    content_html = "".join(render_node(child) for child in page.children)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title_txt)}</title>
</head>
<body style="margin:0;padding:20px;background:#fff;">
<section style="{S_BODY}">
{hero_html}
<section style="{S_PAGE}">
{content_html}
</section>
</section>
</body>
</html>'''


if __name__ == "__main__":
    src_file = Path("/Users/dljapan/.openclaw/workspace/personal-brand/content/ai-team-memory-system.html")
    out_file = Path("/tmp/wechat-ai-memory.html")
    src = src_file.read_text(encoding="utf-8")
    result = convert(src)
    out_file.write_text(result, encoding="utf-8")
    print(f"✅ Converted: {out_file} ({len(result)} chars)")
