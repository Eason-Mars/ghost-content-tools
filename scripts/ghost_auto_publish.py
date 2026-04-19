#!/usr/bin/env python3
"""
ghost_auto_publish.py — Ghost 自动发布（CDP + mobiledoc HTML Card + 图片上传）

固化流程：
1. 连接 OpenClaw 已登录浏览器（CDP port 18800）
2. 从 HTML 提取标题/标签/样式/正文
3. base64 图片 → 上传 Ghost → 替换为 URL
4. mobiledoc HTML Card 格式发布（保留完整自定义 CSS）

用法:
  python3 ghost_auto_publish.py <html_file> --slug <short-slug> [--draft] [--update POST_ID]

示例:
  python3 scripts/ghost_auto_publish.py personal-brand/content/drafts/blog.html --slug my-blog
  python3 scripts/ghost_auto_publish.py blog.html --slug my-blog --update 69afe7b6b3627a0001c730aa
"""

import json, re, base64, sys, argparse
from pathlib import Path


def extract_content(html_path: str) -> dict:
    """从博文 HTML 提取标题、样式+正文、标签、图片
    
    策略：用 premailer 把 CSS inline 到每个 HTML 元素，
    确保 Ghost HTML Card 渲染时不会 strip 掉样式。
    """
    html = Path(html_path).read_text(encoding='utf-8')

    # Title: try hero-title div first, then h1 inside hero/masthead, fallback to any h1, then <title> tag
    title_match = re.search(r'<div[^>]*class="hero-title"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'class="(?:hero|masthead)"[^>]*>.*?<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if title_match:
        title = re.sub(r'<[^>]+>', '', title_match.group(1).strip())
    else:
        # fallback: read from <title> tag, strip the date suffix
        page_title_match = re.search(r'<title>(.*?)</title>', html)
        title = re.sub(r'\s*[|·]\s*20\d\d-\d\d-\d\d.*$', '', page_title_match.group(1)).strip() if page_title_match else "Untitled"

    # Tag from hero-label (includes hidden hero-label for newsletter templates)
    label_match = re.search(r'class="(?:hero-label|series)"[^>]*>(.*?)</div>', html, re.DOTALL)
    tag = re.sub(r'<[^>]+>', '', label_match.group(1).strip()) if label_match else ""
    # For newsletter templates, use series title as tag
    if not tag or tag.upper() == tag:  # all-caps = likely CSS class content, not real tag
        series_match = re.search(r'class="series"[^>]*>(.*?)</div>', html, re.DOTALL)
        if series_match:
            tag = re.sub(r'<[^>]+>', '', series_match.group(1).strip())

    # Inline CSS into elements using premailer (Ghost strips <style> tags from HTML Cards)
    try:
        from premailer import transform
        inlined_html = transform(
            html,
            remove_classes=False,
            strip_important=False,
            allow_network=False,
            disable_link_rewrites=True,
            cssutils_logging_level=40,  # errors only
        )
    except Exception as e:
        print(f"  ⚠️  premailer failed ({e}), falling back to raw HTML")
        inlined_html = html

    # Extract body content from inlined HTML
    body_match = re.search(r'<body[^>]*>(.*)</body>', inlined_html, re.DOTALL)
    body = body_match.group(1).strip() if body_match else inlined_html

    # Remove any residual <style> blocks (already inlined)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)

    # Strip Ghost-only / template-only blocks (should never appear in published content)
    #   .x-box      — X 发布简介框（给作者参考用，不发布）
    #   .site-footer — 页脚（Ghost 自带页脚，不需要）
    from bs4 import BeautifulSoup as _BS
    _soup = _BS(body, 'html.parser')
    for cls in ['x-box', 'site-footer']:
        for el in _soup.find_all(class_=cls):
            el.decompose()
    body = str(_soup)

    # Extract base64 images and replace with placeholders
    img_data_list = []
    def replace_b64_img(match):
        full_tag = match.group(0)
        src_match = re.search(r'src="(data:image/[^"]+)"', full_tag)
        if src_match and len(src_match.group(1)) > 50000:
            img_data_list.append(src_match.group(1))
            return '<!-- IMG_PLACEHOLDER -->'
        return full_tag

    body = re.sub(r'<img[^>]*src="data:image/[^"]*"[^>]*/?\s*>', replace_b64_img, body)

    return {
        "title": title,
        "tag": tag,
        "html": body,
        "img_data_list": img_data_list,
    }


def find_ghost_page(playwright_browser):
    """在已连接的浏览器中找到 Ghost admin 页面"""
    for context in playwright_browser.contexts:
        for page in context.pages:
            if "eason.ghost.io" in page.url:
                return page
    return None


def upload_image_to_ghost(ghost_page, data_uri: str, index: int) -> str:
    """上传单张图片到 Ghost，返回 URL。用 arg 传递避免 evaluate 字符串溢出"""
    import tempfile, os
    b64_data = data_uri.split(',', 1)[1] if ',' in data_uri else data_uri
    mime = 'image/jpeg' if 'image/jpeg' in data_uri else 'image/png'
    ext = 'jpg' if mime == 'image/jpeg' else 'png'

    # Write to temp file, then use upload_file_to_ghost
    img_bytes = base64.b64decode(b64_data)
    tmp_path = f"/tmp/ghost_upload_{index}.{ext}"
    Path(tmp_path).write_bytes(img_bytes)
    url = upload_file_to_ghost(ghost_page, tmp_path)
    os.unlink(tmp_path)
    return url


def upload_file_to_ghost(ghost_page, file_path: str) -> str:
    """上传本地图片文件到 Ghost，返回 URL。分块传入避免 evaluate 溢出"""
    data = Path(file_path).read_bytes()
    b64_data = base64.b64encode(data).decode()
    ext = Path(file_path).suffix.lstrip('.')
    mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else 'image/png'
    name = Path(file_path).name

    # Split base64 into chunks and concatenate in browser
    chunk_size = 50000  # ~50KB per chunk, safe for evaluate
    chunks = [b64_data[i:i+chunk_size] for i in range(0, len(b64_data), chunk_size)]

    ghost_page.evaluate("window.__img_b64 = '';")
    for chunk in chunks:
        # Use JSON.stringify to safely pass the chunk
        ghost_page.evaluate(f"window.__img_b64 += {json.dumps(chunk)};")

    ghost_page.evaluate(f"window.__img_name = {json.dumps(name)};")
    ghost_page.evaluate(f"window.__img_mime = {json.dumps(mime)};")

    result = ghost_page.evaluate("""
        async () => {
            const b64 = window.__img_b64;
            const binary = atob(b64);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
            const blob = new Blob([bytes], { type: window.__img_mime });
            const fd = new FormData();
            fd.append("file", blob, window.__img_name);
            const resp = await fetch("/ghost/api/admin/images/upload/", { method: "POST", body: fd });
            const data = await resp.json();
            if (data.images && data.images[0]) return { ok: true, url: data.images[0].url };
            return { ok: false, error: JSON.stringify(data).substring(0, 200) };
        }
    """)

    if result.get("ok"):
        return result["url"]
    print(f"  ❌ Upload {name}: {result}")
    return None


def publish(html_path: str, slug: str = None, do_publish: bool = True, update_id: str = None):
    from playwright.sync_api import sync_playwright

    content = extract_content(html_path)
    print(f"📝 Title: {content['title']}")
    print(f"🏷️  Tag: {content['tag']}")
    print(f"🖼️  Images: {len(content['img_data_list'])}")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        ghost_page = find_ghost_page(browser)

        if not ghost_page:
            print("❌ Ghost admin page not found. Open https://eason.ghost.io/ghost/ in browser first.")
            sys.exit(1)

        print(f"✅ Connected: {ghost_page.url}")

        # --- Upload images ---
        uploaded_urls = []
        for i, data_uri in enumerate(content['img_data_list']):
            url = upload_image_to_ghost(ghost_page, data_uri, i + 1)
            uploaded_urls.append(url)
            if url:
                print(f"  ✅ Image {i+1}: {url}")

        # --- Replace placeholders ---
        html_content = content['html']
        for url in uploaded_urls:
            if url and '<!-- IMG_PLACEHOLDER -->' in html_content:
                img_tag = f'<img src="{url}" alt="" style="max-width:100%;border-radius:6px;box-shadow:0 2px 12px rgba(0,0,0,0.12);" />'
                html_content = html_content.replace('<!-- IMG_PLACEHOLDER -->', img_tag, 1)

        # --- Build mobiledoc ---
        mobiledoc = json.dumps({
            'version': '0.3.1',
            'atoms': [],
            'cards': [['html', {'html': html_content, 'cardWidth': 'wide'}]],
            'markups': [],
            'sections': [[10, 0]]
        })

        status = "published" if do_publish else "draft"

        ghost_page.evaluate(f"window.__mobiledoc = {json.dumps(mobiledoc)};")
        ghost_page.evaluate(f"window.__title = {json.dumps(content['title'])};")
        ghost_page.evaluate(f"window.__tag = {json.dumps(content['tag'])};")
        ghost_page.evaluate(f"window.__slug = {json.dumps(slug or '')};")
        ghost_page.evaluate(f"window.__status = '{status}';")

        if update_id:
            # Detect existing post format (mobiledoc vs lexical)
            post_data = ghost_page.evaluate(f"""
                async () => {{
                    const resp = await fetch("/ghost/api/admin/posts/{update_id}/?formats=mobiledoc,lexical");
                    const data = await resp.json();
                    const p = data.posts[0];
                    return {{
                        updated_at: p.updated_at,
                        format: p.lexical ? 'lexical' : 'mobiledoc'
                    }};
                }}
            """)
            post_format = post_data.get('format', 'mobiledoc')
            print(f"📦 Post format: {post_format}")

            ghost_page.evaluate(f"window.__updated_at = \"{post_data['updated_at']}\";")

            # Build lexical JSON if needed
            if post_format == 'lexical':
                lexical = json.dumps({
                    "root": {
                        "children": [{"type": "html", "version": 1, "html": html_content, "cardWidth": "wide"}],
                        "direction": None, "format": "", "indent": 0, "type": "root", "version": 1
                    }
                })
                ghost_page.evaluate(f"window.__lexical = {json.dumps(lexical)};")

            result = ghost_page.evaluate(f"""
                async () => {{
                    const p = {{
                        title: window.__title,
                        status: window.__status,
                        tags: window.__tag ? [{{ name: window.__tag }}] : [],
                        updated_at: window.__updated_at
                    }};
                    if ('{post_format}' === 'lexical') {{
                        p.lexical = window.__lexical;
                        p.mobiledoc = null;
                    }} else {{
                        p.mobiledoc = window.__mobiledoc;
                    }}
                    if (window.__slug) p.slug = window.__slug;
                    const resp = await fetch("/ghost/api/admin/posts/{update_id}/", {{
                        method: "PUT",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ posts: [p] }})
                    }});
                    const data = await resp.json();
                    if (data.posts?.[0]) return {{ ok: true, id: data.posts[0].id, slug: data.posts[0].slug, url: data.posts[0].url, status: data.posts[0].status }};
                    return {{ ok: false, error: JSON.stringify(data).substring(0, 300) }};
                }}
            """)
        else:
            result = ghost_page.evaluate("""
                async () => {
                    const p = {
                        title: window.__title,
                        mobiledoc: window.__mobiledoc,
                        status: window.__status,
                        tags: window.__tag ? [{ name: window.__tag }] : []
                    };
                    if (window.__slug) p.slug = window.__slug;
                    const resp = await fetch("/ghost/api/admin/posts/", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ posts: [p] })
                    });
                    const data = await resp.json();
                    if (data.posts?.[0]) return { ok: true, id: data.posts[0].id, slug: data.posts[0].slug, url: data.posts[0].url, status: data.posts[0].status };
                    return { ok: false, error: JSON.stringify(data).substring(0, 300) };
                }
            """)

        if result.get("ok"):
            print(f"\n{'🟢' if do_publish else '📋'} {'Published' if do_publish else 'Draft created'}")
            print(f"   ID:     {result['id']}")
            print(f"   URL:    {result['url']}")
            print(f"   Slug:   {result['slug']}")
            print(f"   Status: {result['status']}")

            # ── Supabase content_posts 写入（非阻塞） ──
            try:
                import sys as _sys
                _sys.path.insert(0, str(Path(__file__).parent))
                from supabase_writer import write_content_post
                import re as _re
                _html_text = Path(html_path).read_text(encoding="utf-8")
                _word_count = len(_re.sub(r'<[^>]+>', '', _html_text).split())
                write_content_post({
                    "ghost_id": result.get("id"),
                    "ghost_slug": result.get("slug"),
                    "ghost_url": result.get("url"),
                    "title": content.get("title", ""),
                    "status": result.get("status", "published"),
                    "platform": "ghost",
                    "html_file": str(html_path),
                    "word_count": _word_count,
                    "agent": "insight",
                })
            except Exception as _e:
                print(f"[WARN] content_post DB 写入跳过：{_e}", file=__import__('sys').stderr)

            # ── Supabase blog_posts 写入（非阻塞，已合并至 content_posts） ──
            # upsert_blog_post 已废弃，写入逻辑在上方 write_content_post 中处理

            # Post-publish verification
            if do_publish and result.get('id'):
                verify = ghost_page.evaluate(f"""
                    async () => {{
                        const resp = await fetch("/ghost/api/admin/posts/{result['id']}/?formats=html");
                        const data = await resp.json();
                        const html = data.posts[0].html || '';
                        return {{
                            htmlLength: html.length,
                            hasCustomStyle: html.includes('8B3A2A') || html.includes('hero'),
                            hasImages: (html.match(/<img/g) || []).length
                        }};
                    }}
                """)
                print(f"\n🔍 Verification:")
                print(f"   HTML length: {verify['htmlLength']} chars")
                print(f"   Custom style: {'✅' if verify['hasCustomStyle'] else '⚠️ NOT FOUND'}")
                print(f"   Images: {verify['hasImages']}")
                if verify['htmlLength'] < 100:
                    print(f"   ⚠️ WARNING: Content appears empty! Check post format (mobiledoc vs lexical).")
        else:
            print(f"\n❌ Failed: {result}")
            sys.exit(1)

        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ghost Auto Publish (CDP + mobiledoc HTML Card)")
    parser.add_argument("html_file", help="Blog HTML file path")
    parser.add_argument("--slug", help="Custom short slug")
    parser.add_argument("--draft", action="store_true", help="Create as draft (default: publish)")
    parser.add_argument("--update", metavar="POST_ID", help="Update existing post by ID")
    args = parser.parse_args()

    if not Path(args.html_file).exists():
        print(f"❌ File not found: {args.html_file}")
        sys.exit(1)

    publish(args.html_file, slug=args.slug, do_publish=not args.draft, update_id=args.update)
