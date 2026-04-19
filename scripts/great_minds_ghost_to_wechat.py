"""
great_minds_ghost_to_wechat.py — Great Minds Ghost→微信转换器（正式版 v2，2026-03-22）

用法：
  python3 scripts/great_minds_ghost_to_wechat.py
  输出：/tmp/great-minds-001-wechat-body.html

每期修改：
  - ISSUE_NUM：期号（如 "002"）
  - ISSUE_DATE：发布日期（如 "2026-04-05"）
  - html = Path(...)：指向当期 Ghost HTML 文件

已修复的历史 BUG（禁止回退）：
1. FONT 变量必须用单引号包裹字体名，否则 style 属性双引号冲突导致 font-size/line-height 全部丢失
2. 图片 hash 必须用完整内容 hash（不能只取前200字符），否则 JPEG 文件头相同导致缓存碰撞图片错乱
3. article-header 三层（art-num/art-title/art-meta）必须各自独立 section，禁止合并
4. 模板外层 section 禁止设置 font-size/line-height（微信会覆盖所有子元素）
5. 字体栈 fallback 必须用 sans-serif，Georgia/serif 在微信渲染为宋体
"""
from bs4 import BeautifulSoup, NavigableString
from pathlib import Path
import re

FONT = "'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Helvetica Neue',Arial,sans-serif"

# ── 正文基础样式 ──
S_P      = f'font-family:{FONT};margin:0 0 24px;font-size:15px;line-height:1.9;letter-spacing:0.5px;text-align:justify;color:rgba(0,0,0,0.88);'
S_BQ     = f'font-family:{FONT};margin:0 0 24px;padding:16px 20px;border-left:4px solid #C5963A;background:#fff8f0;font-size:15px;line-height:1.9;letter-spacing:0.5px;font-style:italic;color:#444;'
S_LI     = f'font-family:{FONT};font-size:15px;line-height:1.9;letter-spacing:0.5px;padding-left:16px;margin-bottom:8px;color:rgba(0,0,0,0.88);'
S_H2     = f'font-family:{FONT};font-size:17px;color:rgba(0,0,0,0.9);margin:32px 0 14px;padding-left:14px;border-left:4px solid #8B3A2A;font-weight:800;line-height:1.6;'
S_H2SUB  = f'font-family:{FONT};font-size:15px;color:rgba(0,0,0,0.85);margin:24px 0 12px;padding-left:12px;border-left:3px solid #C5963A;font-weight:700;line-height:1.6;'

# ── article-header 三层 ──
# art-num: "01 · Ethan Mollick · 2026-03-12" — 金色小字全大写
S_ART_NUM   = f'font-family:{FONT};font-size:11px;font-weight:800;color:#C5963A;letter-spacing:1.5px;text-transform:uppercase;margin:40px 0 8px;'
# art-title: 文章标题 — 大号加粗
S_ART_TITLE = f'font-family:{FONT};font-size:20px;font-weight:900;color:#1a1a1a;line-height:1.35;margin:0 0 8px;'
# art-meta: 来源 newsletter name — 小灰字
S_ART_META  = f'font-family:{FONT};font-size:13px;color:#888;margin:0 0 20px;line-height:1.6;'

# ── 分区标题（大标题栏）──
S_SEC    = f'font-family:{FONT};font-size:11px;font-weight:800;color:#8B3A2A;letter-spacing:2px;text-transform:uppercase;border-bottom:2px solid #8B3A2A;padding-bottom:8px;margin:40px 0 20px;'

# ── meta 信息（日期等）──
S_META   = f'font-family:{FONT};margin:0 0 16px;font-size:12px;color:#999;letter-spacing:0.5px;'

# ── URL 灰框 ──
S_URL    = f'font-family:{FONT};margin:0 0 24px;padding:12px 16px;background:#f5f3f0;border-radius:4px;font-size:13px;color:#666;line-height:1.8;word-break:break-all;'
S_URL_LB = 'font-size:11px;font-weight:700;color:#8B3A2A;letter-spacing:1px;display:block;margin-bottom:4px;'

# ── 卡片（other 区域）──
S_CARD   = 'margin:0 0 20px;padding:18px 20px;background:#faf8f6;border-left:4px solid #C5963A;border:1px solid #e0dbd8;border-radius:4px;'
S_CARD_L = f'font-family:{FONT};font-size:11px;font-weight:700;letter-spacing:1.5px;color:#C5963A;margin:0 0 6px;'
S_CARD_T = f'font-family:{FONT};font-size:16px;font-weight:700;color:#8B3A2A;margin:0 0 10px;line-height:1.4;'
S_CARD_P = f'font-family:{FONT};font-size:14px;color:#333;line-height:1.85;margin:0 0 8px;'

# ── callout ──
S_CALLOUT= f'font-family:{FONT};margin:0 0 24px;padding:16px 20px;background:#1a1a1a;color:#fff;border-radius:6px;font-size:14px;line-height:1.9;font-style:italic;'

# ── HR ──
S_HR     = 'border:none;border-top:1px solid #e0dbd8;margin:36px 0;'

# ── 图片标注 ──
S_IMGCAP = f'font-family:{FONT};font-size:12px;color:#999;text-align:center;margin-bottom:20px;font-style:italic;'

# ══ 工具函数 ══

def clean_inner(elem):
    """保留 strong/em 语义，去掉所有链接及其他标签"""
    s = elem.decode_contents()
    s = re.sub(r'<strong[^>]*>(.*?)</strong>', r'<strong style="font-weight:700;">\1</strong>', s, flags=re.DOTALL)
    s = re.sub(r'<em[^>]*>(.*?)</em>', r'<em style="font-style:italic;color:#555;">\1</em>', s, flags=re.DOTALL)
    s = re.sub(r'<(?!/?strong|/?em)[^>]+>', '', s)
    return s.strip()

def img_to_wechat(img):
    src = img.get('src','')
    if not src:
        return ''
    return f'<img src="{src}" style="width:100%;display:block;margin:20px 0 6px;border-radius:4px;">\n'

def process_elem(elem):
    """处理正文元素，返回微信 HTML 字符串"""
    if not hasattr(elem, 'name') or not elem.name:
        return ''
    cls = elem.get('class', [])
    tag = elem.name

    # 跳过 article-header / src-btn（在外层单独处理）
    if 'article-header' in cls or 'src-btn' in cls:
        return None

    if tag == 'p':
        text = clean_inner(elem)
        if not text.strip():
            return ''
        return f'<section style="{S_P}">{text}</section>\n'

    if tag == 'h2':
        text = elem.get_text().strip()
        if not text:
            return ''
        if 'sec' in cls:
            return f'<section style="{S_H2SUB}">{text}</section>\n'
        return f'<section style="{S_H2}">{text}</section>\n'

    if tag == 'h3':
        text = elem.get_text().strip()
        return f'<section style="{S_H2SUB}">{text}</section>\n' if text else ''

    if tag == 'blockquote':
        text = elem.get_text().strip()
        return f'<section style="{S_BQ}">{text}</section>\n' if text else ''

    if tag in ('ul', 'ol'):
        items = ''
        for li in elem.find_all('li'):
            items += f'<p style="{S_LI}">• {li.get_text().strip()}</p>\n'
        return f'<section style="margin:0 0 24px;padding-left:0;">{items}</section>\n' if items else ''

    if tag == 'img':
        return img_to_wechat(elem)

    if tag == 'hr':
        return f'<hr style="{S_HR}">\n'

    if tag == 'div':
        # callout
        if 'callout' in cls:
            inner = re.sub(r'<strong[^>]*>(.*?)</strong>', r'<strong style="color:#C5963A;font-weight:700;">\1</strong>',
                           elem.decode_contents(), flags=re.DOTALL)
            inner = re.sub(r'<(?!/?strong)[^>]+>', '', inner)
            return f'<section style="{S_CALLOUT}">{inner.strip()}</section>\n'

        # img-block
        if 'img-block' in cls:
            out = ''
            for img in elem.find_all('img'):
                out += img_to_wechat(img)
            cap = elem.find(class_='img-cap')
            if cap:
                out += f'<p style="{S_IMGCAP}">{cap.get_text()}</p>\n'
            return out

        # 递归
        out = ''
        for child in elem.children:
            r = process_elem(child)
            if r:
                out += r
        return out

    return ''


# ══ 主逻辑 ══

# 直接读 Curiosity 输出（无需 InSight 中转）
# 每期只改这一行的路径
html = Path('/Users/dljapan/.openclaw/workspace/tmp/great-minds-004-ghost.html').read_text('utf-8')
soup = BeautifulSoup(html, 'html.parser')
lines = []

# ── 导言（masthead）──
masthead = soup.find(class_='masthead')
if masthead:
    tagline = masthead.find(class_='tagline')
    meta_d  = masthead.find(class_='meta')
    if tagline:
        lines.append(f'<section style="{S_P}">{tagline.get_text().strip()}</section>\n')
    if meta_d:
        lines.append(f'<section style="{S_META}">{meta_d.get_text().strip()}</section>\n')

# ── 精读文章 ──
lines.append(f'<section style="{S_SEC}">最值得关注的新思考</section>\n')

for art in soup.find_all(class_='article'):
    header  = art.find(class_='article-header')
    src_btn = art.find(class_='src-btn')
    orig_url = src_btn.get('href', '') if src_btn else ''

    if header:
        num_e   = header.find(class_='art-num')
        title_e = header.find(class_='art-title')
        meta_e  = header.find(class_='art-meta')

        # art-num：金色小字 "01 · Ethan Mollick · 2026-03-12"
        if num_e:
            lines.append(f'<section style="{S_ART_NUM}">{num_e.get_text().strip()}</section>\n')

        # art-title：大标题，链接改纯文本
        if title_e:
            title_text = title_e.get_text().strip()
            lines.append(f'<section style="{S_ART_TITLE}">{title_text}</section>\n')

        # art-meta：来源名（去掉"阅读原文"链接）
        if meta_e:
            parts = []
            for item in meta_e.children:
                if hasattr(item, 'name') and item.name == 'a':
                    continue  # 跳过"阅读原文"链接
                if isinstance(item, NavigableString):
                    t = str(item).strip().strip('·').strip()
                    if t:
                        parts.append(t)
            meta_text = ' · '.join(p for p in parts if p)
            if meta_text:
                lines.append(f'<section style="{S_ART_META}">{meta_text}</section>\n')

    # 正文子元素
    for child in art.children:
        if not hasattr(child, 'name') or not child.name:
            continue
        if child == header:
            continue
        if src_btn and child == src_btn:
            # URL 灰框
            if orig_url:
                lines.append(f'<section style="{S_URL}"><span style="{S_URL_LB}">📎 原文链接</span>{orig_url}</section>\n')
            continue
        r = process_elem(child)
        if r:
            lines.append(r)

    lines.append(f'<hr style="{S_HR}">\n')

# ── 其他值得关注 ──
lines.append(f'<section style="{S_SEC}">其他值得关注的思考</section>\n')

for o in soup.find_all(class_='other'):
    title_e = o.find(class_='other-title')
    meta_e  = o.find(class_='other-meta')

    title_text = title_e.get_text().strip() if title_e else ''
    title_link = title_e.find('a') if title_e else None
    orig_url   = title_link.get('href', '') if title_link else ''

    # meta：来源+作者+日期（去掉"原文"链接）
    parts = []
    if meta_e:
        for item in meta_e.children:
            if hasattr(item, 'name') and item.name == 'a':
                continue
            if isinstance(item, NavigableString):
                t = str(item).strip().strip('·').strip()
                if t:
                    parts.append(t)
    meta_text = ' · '.join(p for p in parts if p)

    card_inner  = f'<p style="{S_CARD_L}">{meta_text}</p>\n' if meta_text else ''
    card_inner += f'<p style="{S_CARD_T}">{title_text}</p>\n'

    for child in o.children:
        if not hasattr(child, 'name') or not child.name:
            continue
        child_cls = child.get('class', [])
        if any(c in child_cls for c in ['other-title', 'other-meta']):
            continue
        if child.name == 'p':
            card_inner += f'<p style="{S_CARD_P}">{child.get_text().strip()}</p>\n'
        elif child.name in ('ul', 'ol'):
            for li in child.find_all('li'):
                card_inner += f'<p style="{S_CARD_P}">• {li.get_text().strip()}</p>\n'

    if orig_url:
        card_inner += f'<p style="{S_URL_LB}">📎 原文</p>\n<p style="font-family:{FONT};font-size:13px;color:#666;word-break:break-all;margin:0;">{orig_url}</p>\n'

    lines.append(f'<section style="{S_CARD}">{card_inner}</section>\n')

# ── Great Minds 系列固定结尾块 ──
ISSUE_NUM = "004"
ISSUE_DATE = "2026-04-04"
FOOTER_BLOCK = (
    f'<section style="text-align:center;padding:32px 0 24px;margin-top:40px;border-top:1px solid #E0DBD8;">'
    f'<p style="font-family:{FONT};font-size:15px;font-weight:800;color:#8B3A2A;margin:0 0 8px;letter-spacing:0.5px;">'
    f'Great Minds Think Alike · Issue {ISSUE_NUM}</p>'
    f'<p style="font-family:{FONT};font-size:13px;color:#666;margin:0 0 8px;line-height:1.8;">'
    f'精选 AI 领域独立思考者的一手内容，不加滤镜</p>'
    f'<p style="font-family:{FONT};font-size:12px;color:#999;margin:0;line-height:1.8;">'
    f'策划 Mars 🔴 · 内容整理 Curiosity 🔍 · {ISSUE_DATE}</p>'
    f'</section>\n'
)
lines.append(FOOTER_BLOCK)

body = ''.join(lines)
out_path = Path(f'/tmp/great-minds-{ISSUE_NUM}-wechat-body.html')
out_path.write_text(body, 'utf-8')

print(f'生成完成: {len(body)} 字符')
print(f'class= 残留: {body.count("class=")}')
print(f'<a href 残留: {body.count("<a href")}')
print(f'URL框数量: {body.count("📎")}')
print(f'图片数量: {body.count("<img ")}')
print(f'"阅读原文"残留: {body.count("阅读原文")}')
print(f'art-num 数量: {body.count(S_ART_NUM[:30])}')
print(f'art-title 数量: {body.count(S_ART_TITLE[:30])}')
print(f'art-meta 数量: {body.count(S_ART_META[:30])}')
