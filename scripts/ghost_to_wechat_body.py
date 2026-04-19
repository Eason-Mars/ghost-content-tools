#!/usr/bin/env python3
"""
ghost_to_wechat_body.py — Ghost HTML → 微信公众号正文提取器（v2）

移植自 tmp/raphael-publish/src/lib/wechatCompat.ts

核心处理流程：
  1. premailer inline CSS
  2. 删除不需要出现在微信正文里的块（x-box / site-footer / closing / nav / hero）
  3. 取 .page 内容（去掉外层容器）
  4. 应用 Raphael 主题样式（默认 claude）
  5. flex 布局 → table（微信不支持 flex）
  6. li 内 <p> → <span>（li 内块元素展平）
  7. 强制字体继承（p/li/h1-h6/blockquote/span 全部补 font-family/color/line-height）
  8. ul/li → section + p（微信不支持列表标签）
  9. pre/code 块 → 灰色 section 纯文字
  10. 行内 code → span（字体改单引号避免微信双引号截断 bug）
  11. 中文标点防断行（<strong> 等行内元素后的标点吸附）
  12. img: src 不处理（微信公众号编辑器会自动处理）

踩坑记录（历史）：
  - 必须先 premailer inline，否则自定义 CSS class 样式在微信全丢
  - 必须用 .decode_contents() 去掉 .page 容器（带 max-width/padding 破坏微信版面）
  - ul/li 不被微信支持，必须转成 p + 圆点
  - pre/code 块不被微信支持，必须转成灰色 section
  - 行内 code 字体名必须用单引号（双引号在微信里触发样式截断 bug）
  - x-box / site-footer / closing / nav / hero 等块必须剥离
  - flex 布局在微信图文内部分失效，图片网格用 table 替代

用法：
  python3 scripts/ghost_to_wechat_body.py <input.html> <output_body.html> [theme_id]

示例：
  python3 scripts/ghost_to_wechat_body.py \\
    workspace-insight/output/2026-03-22-ai-governance-evolution.html \\
    /tmp/ai-governance-body.html claude
"""

import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

# 导入主题库
sys.path.insert(0, str(Path(__file__).parent))
from raphael_themes import get_theme, DEFAULT_THEME  # DEFAULT_THEME = 'eason'

# 微信不支持的块级元素 class，发布前必须删除
STRIP_CLASSES = ['x-box', 'site-footer', 'closing', 'nav', 'hero']

# 中文标点（需要防断行的）
CJK_PUNCTS = '：；，。！？、:'


def inline_css(html: str) -> str:
    """用 premailer 把 <style> 块里的 CSS inline 到每个元素上"""
    try:
        from premailer import transform
        return transform(
            html,
            remove_classes=False,
            strip_important=False,
            allow_network=False,
            disable_link_rewrites=True,
            cssutils_logging_level=40,
        )
    except Exception as e:
        print(f"⚠️ premailer failed ({e})，直接使用原始 HTML", file=sys.stderr)
        return html


def strip_blocks(soup: BeautifulSoup) -> None:
    """删除不需要出现在微信正文里的块"""
    for cls in STRIP_CLASSES:
        for el in soup.find_all(class_=cls):
            el.decompose()


def apply_theme_to_root(soup: BeautifulSoup, theme: dict) -> BeautifulSoup:
    """
    将 Raphael 主题样式应用到各标签。
    对于每个标签，合并主题样式（不覆盖已有的同属性）。
    """
    tag_map = {
        'h1': theme.get('h1', ''),
        'h2': theme.get('h2', ''),
        'h3': theme.get('h3', ''),
        'h4': theme.get('h4', ''),
        'p': theme.get('p', ''),
        'strong': theme.get('strong', ''),
        'em': theme.get('em', ''),
        'a': theme.get('a', ''),
        'ul': theme.get('ul', ''),
        'ol': theme.get('ol', ''),
        'li': theme.get('li', ''),
        'blockquote': theme.get('blockquote', ''),
        'code': theme.get('code', ''),
        'pre': theme.get('pre', ''),
        'hr': theme.get('hr', ''),
        'img': theme.get('img', ''),
        'table': theme.get('table', ''),
        'th': theme.get('th', ''),
        'td': theme.get('td', ''),
        'tr': theme.get('tr', ''),
    }
    for tag_name, theme_style in tag_map.items():
        if not theme_style:
            continue
        for el in soup.find_all(tag_name):
            existing = el.get('style', '')
            if existing:
                # 合并：主题样式作为基础，已有样式优先（不覆盖）
                el['style'] = theme_style.rstrip(';') + '; ' + existing
            else:
                el['style'] = theme_style
    return soup


def flex_to_table(soup: BeautifulSoup) -> None:
    """
    flex 布局 → table（微信不支持 flex，图片网格用 table 替代）
    移植自 wechatCompat.ts makeWeChatCompatible step 2
    """
    for node in soup.find_all(['div', 'p']):
        # 跳过 pre/code 内部
        if node.find_parent(['pre', 'code']):
            continue
        style = node.get('style', '')
        is_flex = 'display: flex' in style or 'display:flex' in style
        is_image_grid = 'image-grid' in node.get('class', [])
        if not is_flex and not is_image_grid:
            continue

        children = list(node.children)
        el_children = [c for c in children if hasattr(c, 'name') and c.name]
        # 判断是否全部子元素是图片（或含图片）
        all_img = all(
            c.name == 'img' or c.find('img')
            for c in el_children
        )
        if all_img and el_children:
            table = soup.new_tag('table', style='width: 100%; border-collapse: collapse; margin: 16px 0; border: none !important;')
            tbody = soup.new_tag('tbody')
            tr = soup.new_tag('tr', style='border: none !important; background: transparent !important;')
            for child in el_children:
                td = soup.new_tag('td', style='padding: 0 4px; vertical-align: top; border: none !important; background: transparent !important;')
                td.append(child.__copy__() if hasattr(child, '__copy__') else child)
                tr.append(td)
            tbody.append(tr)
            table.append(tbody)
            node.replace_with(table)
        elif is_flex:
            # 非图片 flex 节点，去掉 flex
            node['style'] = re.sub(r'display:\s*flex;?', 'display: block;', style)


def flatten_li_blocks(soup: BeautifulSoup) -> None:
    """
    li 内的 <p> → <span>（微信 li 内块元素会错位）
    移植自 wechatCompat.ts step 3
    """
    for li in soup.find_all('li'):
        has_block = any(
            hasattr(c, 'name') and c.name in ['p', 'div', 'ul', 'ol', 'blockquote']
            for c in li.children
        )
        if has_block:
            for p in li.find_all('p'):
                span = soup.new_tag('span')
                span.string = p.get_text()
                p_style = p.get('style')
                if p_style:
                    span['style'] = p_style
                p.replace_with(span)


def force_font_inheritance(soup: BeautifulSoup, theme: dict) -> None:
    """
    强制字体/颜色/行高继承（微信会覆盖 p/li 等元素的字体）
    移植自 wechatCompat.ts step 4
    """
    container_style = theme.get('container', '')

    font_match = re.search(r'font-family:\s*([^;]+);', container_style)
    size_match = re.search(r'font-size:\s*([^;]+);', container_style)
    # 匹配 color: 但不匹配 background-color: （Python 3.9 不支持变长 lookbehind）
    color_match = re.search(r'(?:^|[\s;])color:\s*([^;]+);', container_style)
    lh_match = re.search(r'line-height:\s*([^;]+);', container_style)

    font_family = font_match.group(1).strip() if font_match else None
    font_size = size_match.group(1).strip() if size_match else None
    color = color_match.group(1).strip() if color_match else None
    line_height = lh_match.group(1).strip() if lh_match else None

    text_tags = ['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'span']
    for tag in soup.find_all(text_tags):
        # 跳过 code/pre 内部 span（保留代码高亮）
        if tag.name == 'span' and tag.find_parent(['pre', 'code']):
            continue
        current = tag.get('style', '')
        additions = ''
        if font_family and 'font-family:' not in current:
            additions += f' font-family: {font_family};'
        if line_height and 'line-height:' not in current:
            additions += f' line-height: {line_height};'
        if font_size and 'font-size:' not in current and tag.name in ['p', 'li', 'blockquote', 'span']:
            additions += f' font-size: {font_size};'
        if color and 'color:' not in current:
            additions += f' color: {color};'
        if additions:
            tag['style'] = (current + additions).strip()


def convert_lists(soup: BeautifulSoup, theme: dict) -> None:
    """ul/ol + li → section + p（微信不支持列表标签）"""
    li_style = theme.get('li', 'font-size:15px;line-height:1.9;color:rgba(0,0,0,0.88);padding-left:16px;margin-bottom:8px;')
    for ul in soup.find_all(['ul', 'ol']):
        wrap = soup.new_tag('section', style='margin:0 0 20px;')
        for li in ul.find_all('li', recursive=False):
            inner = li.decode_contents().strip()
            p = BeautifulSoup(f'<p style="{li_style}">• {inner}</p>', 'html.parser').p
            wrap.append(p)
        ul.replace_with(wrap)


def convert_code_blocks(soup: BeautifulSoup, theme: dict) -> None:
    """pre/code 块 → 灰色 section 纯文字（微信不支持代码块）"""
    pre_style = theme.get('pre', 'font-size:13px;line-height:1.8;color:#555;background:#f5f3f0;padding:14px 18px;margin:16px 0 24px;border-radius:4px;white-space:pre-wrap;word-break:break-all;')
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        text = code.get_text() if code else pre.get_text()
        section = soup.new_tag('section', style=pre_style)
        section.string = text.strip()
        pre.replace_with(section)


def convert_inline_code(soup: BeautifulSoup, theme: dict) -> None:
    """行内 code → span，字体改单引号（双引号触发微信样式截断 bug）"""
    raw_style = theme.get('code', "font-family:'SF Mono',Consolas,monospace;padding:3px 6px;background:#f5f3f0;border-radius:3px;font-size:13px;")
    # 确保字体名使用单引号
    safe_style = raw_style.replace('"SF Mono"', "'SF Mono'").replace('"Fira Code"', "'Fira Code'")
    for code in soup.find_all('code'):
        span = soup.new_tag('span', style=safe_style)
        span.string = code.get_text()
        code.replace_with(span)


def fix_cjk_punctuation(html: str) -> str:
    """
    中文标点防断行：</strong>：→ </strong>\u2060：
    移植自 wechatCompat.ts step end
    """
    pattern = r'(</(?:strong|b|em|span|a|code)>)\s*([：；，。！？、:])'
    return re.sub(pattern, lambda m: m.group(1) + '\u2060' + m.group(2), html)


def wrap_with_container(body_html: str, theme: dict) -> str:
    """用主题 container 样式包裹正文"""
    container_style = theme.get('container', '')
    return f'<section style="{container_style}">{body_html}</section>'


def extract_body(html_path: str, theme_id: str = DEFAULT_THEME) -> str:
    html = Path(html_path).read_text('utf-8')
    theme = get_theme(theme_id)

    # Step 1: premailer inline
    inlined = inline_css(html)

    # Step 2: parse
    soup = BeautifulSoup(inlined, 'html.parser')

    # Step 3: 删除模板专用块
    strip_blocks(soup)

    # Step 4: 取 .page 内容
    page = soup.find(class_='page')
    if not page:
        print("⚠️ 未找到 .page 容器，使用 <body> 内容", file=sys.stderr)
        body_soup = BeautifulSoup(soup.find('body').decode_contents(), 'html.parser')
    else:
        body_soup = BeautifulSoup(page.decode_contents(), 'html.parser')

    # Step 4.5: 清除 .lead / .content-body 的左右 padding（微信里会产生双重留白）
    import re as _re
    for el in body_soup.find_all(True):
        style = el.get('style', '')
        if style:
            # 去掉所有左右 padding（Ghost 模板特有，微信不需要，任何 px 值都清）
            style = _re.sub(r'padding-left\s*:\s*\d+px\s*;?\s*', '', style)
            style = _re.sub(r'padding-right\s*:\s*\d+px\s*;?\s*', '', style)
            # padding: 0 Xpx 形式也去掉（page-inner / content 常见写法）
            style = _re.sub(r'padding\s*:\s*0\s+\d+px\s*;?\s*', 'padding:0;', style)
            # padding: Xpx Ypx（上下 + 左右）→ 只保留上下，清掉左右
            style = _re.sub(r'padding\s*:\s*(\d+px)\s+\d+px\s*;?\s*', r'padding:\1 0;', style)
            # max-width:720px 在微信里无意义，一并去掉
            style = _re.sub(r'max-width\s*:\s*720px\s*;?\s*', '', style)
            el['style'] = style.strip().strip(';')

    # Step 5: 应用主题样式
    apply_theme_to_root(body_soup, theme)

    # Step 6: flex → table（图片网格）
    flex_to_table(body_soup)

    # Step 7: li 内块元素展平
    flatten_li_blocks(body_soup)

    # Step 8: 强制字体继承
    force_font_inheritance(body_soup, theme)

    # Step 9: ul/li → section + p
    convert_lists(body_soup, theme)

    # Step 10: pre/code 块 → 灰色 section
    convert_code_blocks(body_soup, theme)

    # Step 11: 行内 code → span（单引号字体）
    convert_inline_code(body_soup, theme)

    # Step 12: container 包裹
    body_html = str(body_soup)
    wrapped = wrap_with_container(body_html, theme)

    # Step 13: 中文标点防断行
    result = fix_cjk_punctuation(wrapped)

    return result


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    theme_id = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_THEME

    if not Path(input_path).exists():
        print(f"❌ 输入文件不存在: {input_path}")
        sys.exit(1)

    print(f"📄 提取正文: {input_path}")
    print(f"🎨 主题: {theme_id}")
    body = extract_body(input_path, theme_id)
    Path(output_path).write_text(body, 'utf-8')

    # QC
    ul_left = body.count('<ul')
    pre_left = body.count('<pre')
    code_left = body.count('<code')
    dq_font = '"SF Mono"' in body
    page_container = 'class="page"' in body

    print(f"✅ 正文提取完成: {output_path} ({len(body):,} 字符)")
    print(f"   ul/ol 残留: {ul_left}  pre 残留: {pre_left}  code 残留: {code_left}")
    print(f"   双引号字体: {dq_font}  .page 容器: {page_container}")
    if any([ul_left, pre_left, code_left, dq_font, page_container]):
        print("⚠️ QC 警告：有残留需要检查")
    else:
        print("   QC: 全部通过 ✅")


if __name__ == '__main__':
    main()
