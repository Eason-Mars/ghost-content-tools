#!/usr/bin/env python3
"""
Blog 统一发布脚本 v2.0
用法：
  python3 publish_blog.py <source.html> --slug <slug> [--ghost] [--wechat] [--all]
  python3 publish_blog.py <source.html> --slug <slug> --all \
    --update-ghost <post_id> --update-wechat <media_id>

改进 v2.0：
  - BeautifulSoup DOM 解析，取代脆弱的正则
  - 微信版内联样式转换器：通用组件映射表，不再依赖专用脚本
  - Ghost 浏览器自动启动检测
  - QC 更全面（内容级检查）
"""

import argparse
import re
import subprocess
import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup, Tag

SCRIPTS_DIR = Path(__file__).parent
WORKSPACE   = SCRIPTS_DIR.parent

# ── 品牌色 ─────────────────────────────────────────────────────────────
BRAND_RED  = '#8B3A2A'
BRAND_GOLD = '#C5963A'
FF = '-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",Georgia,serif'
BASE  = f'font-family:{FF};font-size:15px;line-height:2.0;color:rgba(0,0,0,0.9);letter-spacing:0.544px;'
P_    = 'margin:0 0 24px;font-size:15px;line-height:2.0;letter-spacing:0.544px;text-align:justify;'
H2_   = f'font-size:18px;color:rgba(0,0,0,0.9);margin:36px 0 16px;padding-left:14px;border-left:4px solid {BRAND_RED};font-weight:800;line-height:1.75;'
H3_   = f'font-size:16px;font-weight:700;color:{BRAND_RED};margin:28px 0 10px;'
BQ_   = f'margin:0 0 24px;padding:16px 20px;border-left:4px solid {BRAND_GOLD};background:#fff8f0;font-size:15px;line-height:2.0;letter-spacing:0.544px;font-style:italic;color:#444;'
HL_   = f'margin:0 0 24px;padding:16px 20px;background:#F0E4D8;border-radius:4px;font-size:15px;line-height:2.0;letter-spacing:0.544px;color:#5a2a1a;'
LEAD_ = f'font-size:15px;color:rgb(85,85,85);margin:0 0 24px;padding-bottom:24px;border-bottom:1px solid rgb(233,233,231);line-height:2.0;letter-spacing:0.544px;text-align:justify;'
STR_  = 'color:#1a1a1a;font-weight:700;'
# wall-card → 微信卡片样式
WALL_WRAP_  = f'margin:0 0 16px;padding:18px 20px;background:#fff;border-left:4px solid {BRAND_GOLD};border:1px solid #e0dbd8;border-radius:4px;'
WALL_NUM_   = f'font-size:11px;font-weight:700;letter-spacing:1.5px;color:{BRAND_GOLD};margin-bottom:4px;'
WALL_TTL_   = f'font-size:16px;font-weight:700;color:{BRAND_RED};margin-bottom:4px;'
WALL_RULE_  = 'font-size:13px;color:#888;margin-bottom:6px;line-height:1.7;'
WALL_FLAB_  = f'font-size:11px;font-weight:700;color:{BRAND_RED};letter-spacing:1px;display:block;margin-bottom:4px;'
WALL_FEAR_  = 'font-size:14px;color:#333;line-height:1.85;margin:0;'
# method-list → 微信卡片样式
METHOD_ITEM_ = 'margin-bottom:10px;padding:14px 16px;background:#fff;border:1px solid #e0dbd8;border-radius:4px;font-size:15px;line-height:2.0;letter-spacing:0.544px;'
METHOD_TTL_  = f'font-size:15px;font-weight:700;color:{BRAND_RED};display:block;margin-bottom:4px;'
METHOD_DESC_ = 'font-size:14px;color:#555;line-height:1.85;'
# closing / hero
CLOSING_  = f'background:{BRAND_RED};color:#fff;padding:24px;margin-top:40px;border-radius:4px;'
C_NAME_   = 'font-size:19px;font-weight:800;margin-bottom:6px;'
C_CRED_   = 'font-size:12px;opacity:0.70;line-height:1.8;margin-bottom:6px;letter-spacing:0.5px;'
C_TAG_    = 'font-size:13px;opacity:0.85;line-height:1.7;'
HERO_TTL_ = f'font-size:22px;font-weight:800;line-height:1.4;color:{BRAND_RED};margin:0 auto;text-align:center;'
META_     = 'font-size:13px;color:#666;text-align:right;margin:0 16px 24px;line-height:1.8;letter-spacing:0.5px;'
PAGE_     = f'{BASE}padding:0 16px 48px;'


# ══════════════════════════════════════════════════════════════════════
#  Ghost 版生成（DOM 解析）
# ══════════════════════════════════════════════════════════════════════

def generate_ghost_html(source_html: str) -> str:
    soup = BeautifulSoup(source_html, 'html.parser')

    # 提取并清理 <style>
    style_tag = soup.find('style')
    style_text = style_tag.string if style_tag else ''
    # 去掉 nav / x-box CSS 规则
    style_text = re.sub(r'\s*nav\s*\{[^}]*\}', '', style_text)
    style_text = re.sub(r'\s*\.x-box[\w\s.>#~:,\[\]="*]*\{[^}]*\}', '', style_text)

    # 移除不需要的顶层元素
    for tag_name in ['nav']:
        for t in soup.find_all(tag_name):
            t.decompose()
    for cls in ['x-box']:
        for t in soup.find_all(class_=cls):
            t.decompose()

    # 提取 hero + page
    hero = soup.find(class_='hero')
    page = soup.find(class_='page')

    if not hero or not page:
        raise ValueError('找不到 .hero 或 .page，请检查源文件结构')

    # page 里再去一次 site-footer（有时在 page 内）
    for t in page.find_all(class_='site-footer'):
        t.decompose()

    ghost_html = (
        f'<style>{style_text}</style>\n'
        f'{hero}\n'
        f'{page}\n'
        f'<div class="site-footer">easonzhang.ai · Eason Zhang</div>'
    )
    return ghost_html


def qc_ghost(html: str) -> bool:
    forbidden = {
        'x-box HTML块': 'class="x-box"',
        'X推文内容': 'X · 发布简介',
        'nav标签': '<nav',
        'DOCTYPE': '<!DOCTYPE',
        'APAG标签': 'class="label"',
        '品牌名杨国福': '杨国福',
    }
    required = {
        'hero存在': 'class="hero"',
        'closing签名': '我叫 Eason',
    }
    ok = True
    for name, kw in forbidden.items():
        count = html.count(kw)
        passed = count == 0
        print(f'  {"✅" if passed else "❌"} {name}: {count} (应为0)')
        if not passed: ok = False
    for name, kw in required.items():
        count = html.count(kw)
        passed = count >= 1
        print(f'  {"✅" if passed else "❌"} {name}: {count} (应≥1)')
        if not passed: ok = False
    return ok


# ══════════════════════════════════════════════════════════════════════
#  微信版生成（组件映射，DOM 解析）
# ══════════════════════════════════════════════════════════════════════

def _wechat_node(tag) -> str:
    """递归将单个 BS4 Tag 转为微信内联样式 HTML"""
    if isinstance(tag, str):
        return tag  # NavigableString

    name = tag.name if tag.name else ''
    cls  = tag.get('class', [])
    cls  = cls if isinstance(cls, list) else [cls]

    # ── 自定义组件 ──────────────────────────────────────────────────
    if 'wall-card' in cls:
        num   = tag.find(class_='wall-num')
        title = tag.find(class_='wall-title')
        rule  = tag.find(class_='rule')
        flab  = tag.find(class_='fear-label')
        fear  = tag.find(class_='fear')
        jp    = title.find(class_='jp') if title else None
        if jp: jp.decompose()
        title_text = title.get_text(strip=True) if title else ''
        return (
            f'<section style="{WALL_WRAP_}">'
            f'<p style="{WALL_NUM_}">{num.get_text(strip=True) if num else ""}</p>'
            f'<p style="{WALL_TTL_}">{title_text}</p>'
            f'<p style="{WALL_RULE_}">{rule.get_text(strip=True) if rule else ""}</p>'
            f'<span style="{WALL_FLAB_}">{flab.get_text(strip=True) if flab else "墙后面真正的顾虑"}</span>'
            f'<p style="{WALL_FEAR_}">{fear.decode_contents() if fear else ""}</p>'
            f'</section>'
        )

    if 'method-list' in cls:
        items = []
        for li in tag.find_all('li'):
            icon    = li.find(class_='icon')
            content = li.find(class_='content')
            strong  = content.find('strong') if content else None
            span    = content.find('span') if content else None
            items.append(
                f'<section style="{METHOD_ITEM_}">'
                f'{icon.get_text(strip=True) + "　" if icon else ""}'
                f'<strong style="{METHOD_TTL_}">{strong.get_text(strip=True) if strong else ""}</strong>'
                f'<span style="{METHOD_DESC_}">{span.get_text(strip=True) if span else ""}</span>'
                f'</section>'
            )
        return ''.join(items)

    if 'highlight-box' in cls:
        inner = tag.decode_contents()
        # 保留内部 strong
        inner = re.sub(r'<strong[^>]*>', f'<strong style="{STR_}">', inner)
        return f'<section style="{HL_}">{inner}</section>'

    if 'quote-block' in cls:
        inner = tag.decode_contents()
        return f'<section style="{BQ_}">{inner}</section>'

    if 'closing' in cls:
        name_ = tag.find(class_='name')
        creds = tag.find(class_='creds')
        tline = tag.find(class_='tagline')
        return (
            f'<section style="{CLOSING_}">'
            f'<p style="{C_NAME_}">{name_.get_text(strip=True) if name_ else "我叫 Eason"}</p>'
            f'<p style="{C_CRED_}">{creds.get_text(strip=True) if creds else ""}</p>'
            f'<p style="{C_TAG_}">{tline.get_text(strip=True) if tline else ""}</p>'
            f'</section>'
        )

    if 'x-box' in cls:
        return ''  # 微信版不要 x-box

    if 'site-footer' in cls:
        return ''  # 不要 footer

    if 'lead' in cls:
        inner = tag.decode_contents()
        inner = re.sub(r'<strong[^>]*>', f'<strong style="{STR_}">', inner)
        return f'<section style="{LEAD_}">{inner}</section>'

    # ── 标准 HTML 元素 ──────────────────────────────────────────────
    if name == 'h2':
        return f'<section style="{H2_}">{tag.get_text(strip=True)}</section>'

    if name == 'h3':
        return f'<section style="{H3_}">{tag.get_text(strip=True)}</section>'

    if name == 'p':
        inner = tag.decode_contents()
        inner = re.sub(r'<strong[^>]*>', f'<strong style="{STR_}">', inner)
        inner = re.sub(r'<em[^>]*>', '<em style="color:rgb(85,85,85);font-style:italic;">', inner)
        return f'<section style="{P_}">{inner}</section>'

    if name == 'blockquote':
        return f'<section style="{BQ_}">{tag.decode_contents()}</section>'

    if name in ('ul', 'ol'):
        items = ''.join(
            f'<section style="margin-bottom:8px;line-height:2.0;letter-spacing:0.544px;">• {li.decode_contents()}</section>'
            for li in tag.find_all('li', recursive=False)
        )
        return f'<section style="margin:0 0 24px;">{items}</section>'

    # 其他 div / section → 递归处理子节点
    if name in ('div', 'section', 'article', 'main'):
        return ''.join(_wechat_node(child) for child in tag.children)

    # 其余标签原样保留
    return str(tag)


def generate_wechat_html(source_html: str, title: str = '') -> str:
    soup = BeautifulSoup(source_html, 'html.parser')

    # 提取标题
    if not title:
        h1 = soup.find('h1')
        title = h1.get_text(strip=True) if h1 else ''

    # 提取 page 内容
    page = soup.find(class_='page')
    if not page:
        raise ValueError('找不到 .page，请检查源文件结构')

    # 转换内容
    content_parts = []
    for child in page.children:
        if not hasattr(child, 'name') or not child.name:
            continue
        content_parts.append(_wechat_node(child))

    content = '\n'.join(p for p in content_parts if p.strip())

    wechat_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:20px;background:#fff;">
<section style="{BASE}">
<section style="text-align:center;padding:32px 16px 24px;border-bottom:2px solid {BRAND_RED};margin-bottom:24px;">
<p style="{HERO_TTL_}">{title}</p>
</section>
<section style="{META_}"><span style="font-weight:700;color:#666;">文｜</span>Eason</section>
<section style="{PAGE_}">
{content}
</section>
</section>
</body>
</html>'''
    return wechat_html


def qc_wechat(html: str) -> bool:
    forbidden = {
        'x-box': 'x-box',
        'X推文简介': 'X · 发布简介',
        'APAG标签': 'class="label"',
        '品牌名': '杨国福',
    }
    required = {
        'DOCTYPE': '<!DOCTYPE',
        '签名': '我叫 Eason',
        '内联样式存在': 'style=',
    }
    ok = True
    for name, kw in forbidden.items():
        count = html.count(kw)
        passed = count == 0
        print(f'  {"✅" if passed else "❌"} {name}: {count} (应为0)')
        if not passed: ok = False
    for name, kw in required.items():
        count = html.count(kw)
        passed = count >= 1
        print(f'  {"✅" if passed else "❌"} {name}: {count} (应≥1)')
        if not passed: ok = False
    return ok


# ══════════════════════════════════════════════════════════════════════
#  发布调用
# ══════════════════════════════════════════════════════════════════════

def ensure_ghost_browser():
    """确保 Ghost admin 浏览器已启动"""
    result = subprocess.run(
        [sys.executable, '-c',
         'import urllib.request; urllib.request.urlopen("http://127.0.0.1:18800/json", timeout=2)'],
        capture_output=True
    )
    if result.returncode != 0:
        print('  🌐 启动 openclaw 浏览器...')
        subprocess.Popen(
            ['openclaw', 'browser', 'start', '--profile', 'openclaw'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        import time; time.sleep(4)

        # 打开 Ghost admin
        subprocess.run(
            ['openclaw', 'browser', 'open', '--profile', 'openclaw',
             '--url', 'https://eason.ghost.io/ghost/'],
            capture_output=True
        )
        time.sleep(3)


def publish_ghost(ghost_html_path: Path, slug: str, post_id: str = None) -> dict:
    ensure_ghost_browser()
    cmd = [sys.executable, str(SCRIPTS_DIR / 'ghost_auto_publish.py'),
           str(ghost_html_path), '--slug', slug, '--draft']
    if post_id:
        cmd += ['--update', post_id]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return {}
    id_m  = re.search(r'ID:\s+(\S+)', result.stdout)
    url_m = re.search(r'URL:\s+(\S+)', result.stdout)
    return {'id': id_m.group(1) if id_m else '', 'url': url_m.group(1) if url_m else ''}


def publish_wechat(wechat_html_path: Path, title: str, media_id: str = None) -> dict:
    cmd = [sys.executable, str(SCRIPTS_DIR / 'publish_wechat.py'),
           str(wechat_html_path), '--title', title, '--author', 'Eason']
    if media_id:
        cmd += ['--update', media_id]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return {}
    mid_m = re.search(r'Draft (?:created|updated): (\S+)', result.stdout)
    return {'media_id': mid_m.group(1) if mid_m else ''}


# ══════════════════════════════════════════════════════════════════════
#  主入口
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Blog 统一发布脚本 v2.0')
    parser.add_argument('source', help='源 HTML 文件')
    parser.add_argument('--slug', required=True)
    parser.add_argument('--title', default='')
    parser.add_argument('--ghost',  action='store_true')
    parser.add_argument('--wechat', action='store_true')
    parser.add_argument('--all',    action='store_true')
    parser.add_argument('--update-ghost',  default='', metavar='POST_ID')
    parser.add_argument('--update-wechat', default='', metavar='MEDIA_ID')
    parser.add_argument('--dry-run', action='store_true', help='只生成文件，不推送')
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    if not source_path.exists():
        sys.exit(f'❌ 文件不存在: {source_path}')

    source_html = source_path.read_text(encoding='utf-8')

    # 提取标题
    title = args.title
    if not title:
        soup = BeautifulSoup(source_html, 'html.parser')
        h1 = soup.find('h1')
        title = h1.get_text(strip=True) if h1 else args.slug

    do_ghost  = args.ghost or args.all
    do_wechat = args.wechat or args.all
    if not do_ghost and not do_wechat:
        sys.exit('❌ 请指定 --ghost / --wechat / --all')

    results = {}

    # ── Ghost ─────────────────────────────────────────────────────────
    if do_ghost:
        print('\n' + '─'*50)
        print('📦 Ghost 版生成...')
        try:
            ghost_html = generate_ghost_html(source_html)
        except Exception as e:
            sys.exit(f'❌ Ghost版生成失败: {e}')

        ghost_path = source_path.parent / (source_path.stem + '-ghost.html')
        ghost_path.write_text(ghost_html, encoding='utf-8')
        print(f'   → {ghost_path.name} ({len(ghost_html):,} chars)')

        print('\n🔍 Ghost QC:')
        if not qc_ghost(ghost_html):
            sys.exit('❌ Ghost QC 未通过，中止')
        print('✅ Ghost QC 通过')

        if not args.dry_run:
            print('\n🚀 推送 Ghost 草稿...')
            r = publish_ghost(ghost_path, args.slug, args.update_ghost or None)
            if r.get('url'):
                results['ghost'] = r
                print(f'✅ Ghost 完成 → 预览: {r["url"]}')

    # ── 微信 ──────────────────────────────────────────────────────────
    if do_wechat:
        print('\n' + '─'*50)
        print('📱 微信版生成...')
        try:
            wechat_html = generate_wechat_html(source_html, title)
        except Exception as e:
            sys.exit(f'❌ 微信版生成失败: {e}')

        wechat_path = source_path.with_suffix('.wechat.html')
        wechat_path.write_text(wechat_html, encoding='utf-8')
        print(f'   → {wechat_path.name} ({len(wechat_html):,} chars)')

        print('\n🔍 微信 QC:')
        if not qc_wechat(wechat_html):
            sys.exit('❌ 微信 QC 未通过，中止')
        print('✅ 微信 QC 通过')

        if not args.dry_run:
            print('\n🚀 推送微信草稿...')
            r = publish_wechat(wechat_path, title, args.update_wechat or None)
            if r.get('media_id'):
                results['wechat'] = r
                print(f'✅ 微信完成 → media_id: {r["media_id"]}')

    print('\n🎉 完成')
    if results:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
