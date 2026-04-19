#!/usr/bin/env python3
"""
great_minds_wechat_inline.py — Great Minds 微信推送预处理器

功能：
  1. 读取 fill_great_minds.py 生成的完整 HTML
  2. 展开 CSS 变量（premailer 不支持 var()）
  3. premailer inline CSS
  4. 提取 body 内容
  5. 输出纯正文 HTML（可直接推微信）

用法：
  python3 scripts/great_minds_wechat_inline.py <input.html> <output.html>

示例：
  python3 scripts/great_minds_wechat_inline.py \\
    personal-brand/content/great-minds/great-minds-003-wechat-body.html \\
    personal-brand/content/great-minds/great-minds-003-wechat-final.html
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup


def expand_css_vars(content: str) -> str:
    """展开 :root 里的 CSS 变量，替换所有 var(--xxx)"""
    root_match = re.search(r':root\s*\{([^}]+)\}', content)
    vars_map = {}
    if root_match:
        for line in root_match.group(1).splitlines():
            m = re.match(r'\s*--([\w-]+)\s*:\s*(.+?);', line)
            if m:
                vars_map[m.group(1)] = m.group(2).strip()

    def _replace(m):
        return vars_map.get(m.group(1), m.group(0))

    result = re.sub(r'var\(--([\w-]+)\)', _replace, content)
    remaining = len(re.findall(r'var\(--[\w-]+\)', result))
    print(f'  CSS 变量展开：{len(vars_map)} 个变量，残留 {remaining} 个')
    return result


def inline_and_extract(content: str) -> str:
    """premailer inline CSS，提取 body 内容"""
    try:
        from premailer import transform
        inlined = transform(content, base_url='', remove_classes=False, cssutils_logging_level=50)
        print('  premailer inline：✅')
    except ImportError:
        print('  ⚠️ premailer 未安装，请运行：pip install premailer --break-system-packages')
        sys.exit(1)

    soup = BeautifulSoup(inlined, 'html.parser')
    body = soup.find('body')
    body_html = body.decode_contents() if body else inlined

    # 去掉残留 <style> 块
    body_html = re.sub(r'<style[^>]*>.*?</style>', '', body_html, flags=re.DOTALL)
    return body_html


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f'❌ 输入文件不存在: {input_path}')
        sys.exit(1)

    print(f'📄 读取: {input_path}')
    content = input_path.read_text('utf-8')
    print(f'  原始大小: {len(content):,} 字符')

    print('🔧 展开 CSS 变量...')
    content = expand_css_vars(content)

    print('🎨 inline CSS...')
    body_html = inline_and_extract(content)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body_html, 'utf-8')

    print(f'✅ 输出: {output_path}')
    print(f'  最终大小: {len(body_html):,} 字符')
    print(f'  棕红色(#8B3A2A): {body_html.count("#8B3A2A")} 处')
    print(f'  签名(我叫 Eason): {body_html.count("我叫 Eason")} 处')
    print(f'  var()残留: {body_html.count("var(--")} 处')
    print(f'  style块残留: {body_html.count("<style")} 块')


if __name__ == '__main__':
    main()
