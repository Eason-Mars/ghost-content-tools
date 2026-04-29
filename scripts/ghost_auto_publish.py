#!/usr/bin/env python3
"""
ghost_auto_publish.py — Ghost 自动发布（Admin API + JWT，无浏览器依赖）

固化流程：
1. 从 HTML 提取标题/标签/样式+正文（premailer inline CSS）
2. base64 图片 → POST /ghost/api/admin/images/upload/ → 替换为 URL
3. mobiledoc HTML Card 创建；更新时自动检测 lexical/mobiledoc

用法:
  python3 ghost_auto_publish.py <html_file> --slug <short-slug> [--draft] [--update POST_ID]

环境变量:
  GHOST_ADMIN_KEY  Ghost Admin API key（格式 <id>:<secret>，
                   在 Ghost → Settings → Integrations 创建 Custom Integration 后获取）
  GHOST_ADMIN_URL  Ghost 站点根 URL（默认 https://eason.ghost.io）

历史:
  2026-04-29  改用 Ghost Admin API（REST + JWT），移除 Playwright/CDP 依赖
              （Chrome 147 + Playwright connect_over_cdp 在脚本环境完全 hang）
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from pathlib import Path

import jwt as pyjwt
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _logger import get_logger

# Best-effort .env auto-load — keep optional so the script still runs
# in environments where python-dotenv isn't installed.
try:
    from dotenv import load_dotenv
    _repo_root = Path(__file__).resolve().parent.parent
    for _candidate in (_repo_root / ".env", _repo_root / ".env.ghost"):
        if _candidate.exists():
            load_dotenv(_candidate, override=False)
except Exception:
    pass

log = get_logger("ghost.publish")

DEFAULT_ADMIN_URL = "https://eason.ghost.io"
API_VERSION = "v5.0"
JWT_TTL_SECONDS = 5 * 60
HTTP_TIMEOUT = 60
HTTP_TIMEOUT_UPLOAD = 120


def extract_content(html_path: str) -> dict:
    """从博文 HTML 提取标题、样式+正文、标签、图片

    策略：用 premailer 把 CSS inline 到每个 HTML 元素，
    确保 Ghost HTML Card 渲染时不会 strip 掉样式。
    """
    html = Path(html_path).read_text(encoding='utf-8')

    # Title: try hero-title div first, then h1 inside hero/masthead, fallback to any h1, then <title>
    title_match = re.search(r'<div[^>]*class="hero-title"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'class="(?:hero|masthead)"[^>]*>.*?<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if title_match:
        title = re.sub(r'<[^>]+>', '', title_match.group(1).strip())
    else:
        page_title_match = re.search(r'<title>(.*?)</title>', html)
        title = re.sub(r'\s*[|·]\s*20\d\d-\d\d-\d\d.*$', '', page_title_match.group(1)).strip() if page_title_match else "Untitled"

    # Tag from hero-label
    label_match = re.search(r'class="(?:hero-label|series)"[^>]*>(.*?)</div>', html, re.DOTALL)
    tag = re.sub(r'<[^>]+>', '', label_match.group(1).strip()) if label_match else ""
    if not tag or tag.upper() == tag:
        series_match = re.search(r'class="series"[^>]*>(.*?)</div>', html, re.DOTALL)
        if series_match:
            tag = re.sub(r'<[^>]+>', '', series_match.group(1).strip())

    # Inline CSS into elements (Ghost HTML Card strips <style> tags)
    try:
        from premailer import transform
        inlined_html = transform(
            html,
            remove_classes=False,
            strip_important=False,
            allow_network=False,
            disable_link_rewrites=True,
            cssutils_logging_level=40,
        )
    except Exception as e:
        print(f"  ⚠️  premailer failed ({e}), falling back to raw HTML")
        inlined_html = html

    body_match = re.search(r'<body[^>]*>(.*)</body>', inlined_html, re.DOTALL)
    body = body_match.group(1).strip() if body_match else inlined_html

    # Strip residual <style> blocks (already inlined)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)

    # Strip Ghost-only / template-only blocks
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


# ── Ghost Admin API client ────────────────────────────────────────────────

def _admin_credentials() -> tuple[str, str]:
    raw = os.environ.get("GHOST_ADMIN_KEY", "").strip()
    if not raw or ":" not in raw:
        raise RuntimeError(
            "GHOST_ADMIN_KEY missing or malformed. "
            "Format: <id>:<secret>. Create a Custom Integration at "
            "Ghost Admin → Settings → Integrations to obtain one."
        )
    kid, secret = raw.split(":", 1)
    if not kid or not secret:
        raise RuntimeError("GHOST_ADMIN_KEY malformed: id and secret must both be non-empty")
    return kid, secret


def _make_token(kid: str, secret: str) -> str:
    """Generate a short-lived JWT for the Ghost Admin API per docs:
    https://ghost.org/docs/admin-api/#token-authentication
    """
    iat = int(time.time())
    payload = {"iat": iat, "exp": iat + JWT_TTL_SECONDS, "aud": "/admin/"}
    headers = {"alg": "HS256", "kid": kid, "typ": "JWT"}
    return pyjwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=headers)


def _api_url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/ghost/api/admin/{path.lstrip('/')}"


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Ghost {token}", "Accept-Version": API_VERSION}


def _api_call(method: str, url: str, token: str, *, expect_json: bool = True, timeout: int = HTTP_TIMEOUT, **kwargs) -> dict:
    headers = kwargs.pop("headers", {}) or {}
    headers.update(_auth_headers(token))
    resp = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
    if not resp.ok:
        body = (resp.text or "")[:400]
        raise RuntimeError(f"Ghost API {method} {url} → {resp.status_code}: {body}")
    if not expect_json:
        return {}
    try:
        return resp.json()
    except ValueError as e:
        raise RuntimeError(f"Ghost API {method} {url} returned non-JSON: {resp.text[:200]}") from e


def upload_image_bytes(base_url: str, token: str, data: bytes, filename: str, mime: str) -> str:
    url = _api_url(base_url, "images/upload/")
    files = {"file": (filename, data, mime)}
    fields = {"ref": filename}
    headers = _auth_headers(token)
    resp = requests.post(url, files=files, data=fields, headers=headers, timeout=HTTP_TIMEOUT_UPLOAD)
    if not resp.ok:
        raise RuntimeError(f"Ghost image upload {filename} → {resp.status_code}: {resp.text[:300]}")
    payload = resp.json()
    if not payload.get("images") or not payload["images"][0].get("url"):
        raise RuntimeError(f"Ghost image upload {filename} returned no URL: {json.dumps(payload)[:200]}")
    return payload["images"][0]["url"]


def upload_image_b64(base_url: str, token: str, data_uri: str, index: int) -> str:
    if "," not in data_uri:
        raise RuntimeError(f"Image #{index}: data URI missing comma separator")
    mime = "image/jpeg" if "image/jpeg" in data_uri else "image/png"
    ext = "jpg" if mime == "image/jpeg" else "png"
    img_bytes = base64.b64decode(data_uri.split(",", 1)[1])
    return upload_image_bytes(base_url, token, img_bytes, f"upload_{index}.{ext}", mime)


def upload_local_image(base_url: str, token: str, file_path: str) -> str:
    p = Path(file_path)
    ext = p.suffix.lstrip(".").lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    return upload_image_bytes(base_url, token, p.read_bytes(), p.name, mime)


def get_post(base_url: str, token: str, post_id: str, *, formats: str = "mobiledoc,lexical") -> dict:
    url = _api_url(base_url, f"posts/{post_id}/?formats={formats}")
    payload = _api_call("GET", url, token)
    if not payload.get("posts"):
        raise RuntimeError(f"Post {post_id} not found")
    return payload["posts"][0]


def create_post(base_url: str, token: str, post: dict) -> dict:
    url = _api_url(base_url, "posts/")
    payload = _api_call(
        "POST", url, token,
        json={"posts": [post]},
        headers={"Content-Type": "application/json"},
    )
    return payload["posts"][0]


def update_post(base_url: str, token: str, post_id: str, post: dict) -> dict:
    url = _api_url(base_url, f"posts/{post_id}/")
    payload = _api_call(
        "PUT", url, token,
        json={"posts": [post]},
        headers={"Content-Type": "application/json"},
    )
    return payload["posts"][0]


# ── Orchestration ─────────────────────────────────────────────────────────

def publish(html_path: str, slug: str = None, do_publish: bool = True, update_id: str = None) -> dict:
    base_url = os.environ.get("GHOST_ADMIN_URL", DEFAULT_ADMIN_URL).strip() or DEFAULT_ADMIN_URL
    kid, secret = _admin_credentials()
    token = _make_token(kid, secret)

    content = extract_content(html_path)
    print(f"📝 Title: {content['title']}")
    print(f"🏷️  Tag: {content['tag']}")
    print(f"🖼️  Images: {len(content['img_data_list'])}")

    uploaded_urls = []
    for i, data_uri in enumerate(content["img_data_list"]):
        url = upload_image_b64(base_url, token, data_uri, i + 1)
        uploaded_urls.append(url)
        print(f"  ✅ Image {i+1}: {url}")

    html_content = content["html"]
    for url in uploaded_urls:
        if url and "<!-- IMG_PLACEHOLDER -->" in html_content:
            img_tag = (
                f'<img src="{url}" alt="" '
                f'style="max-width:100%;border-radius:6px;'
                f'box-shadow:0 2px 12px rgba(0,0,0,0.12);" />'
            )
            html_content = html_content.replace("<!-- IMG_PLACEHOLDER -->", img_tag, 1)

    mobiledoc = json.dumps({
        "version": "0.3.1",
        "atoms": [],
        "cards": [["html", {"html": html_content, "cardWidth": "wide"}]],
        "markups": [],
        "sections": [[10, 0]],
    })
    status = "published" if do_publish else "draft"

    if update_id:
        existing = get_post(base_url, token, update_id)
        post_format = "lexical" if existing.get("lexical") else "mobiledoc"
        print(f"📦 Post format: {post_format}")
        payload = {
            "title": content["title"],
            "status": status,
            "tags": [{"name": content["tag"]}] if content["tag"] else [],
            "updated_at": existing["updated_at"],
        }
        if slug:
            payload["slug"] = slug
        if post_format == "lexical":
            payload["lexical"] = json.dumps({
                "root": {
                    "children": [{
                        "type": "html", "version": 1,
                        "html": html_content, "cardWidth": "wide",
                    }],
                    "direction": None, "format": "", "indent": 0,
                    "type": "root", "version": 1,
                }
            })
            payload["mobiledoc"] = None
        else:
            payload["mobiledoc"] = mobiledoc
        result = update_post(base_url, token, update_id, payload)
    else:
        payload = {
            "title": content["title"],
            "mobiledoc": mobiledoc,
            "status": status,
            "tags": [{"name": content["tag"]}] if content["tag"] else [],
        }
        if slug:
            payload["slug"] = slug
        result = create_post(base_url, token, payload)

    out = {
        "ok": True,
        "id": result.get("id"),
        "slug": result.get("slug"),
        "url": result.get("url"),
        "status": result.get("status", status),
    }

    print(f"\n{'🟢' if do_publish else '📋'} {'Published' if do_publish else 'Draft created'}")
    print(f"   ID:     {out['id']}")
    print(f"   URL:    {out['url']}")
    print(f"   Slug:   {out['slug']}")
    print(f"   Status: {out['status']}")

    # Supabase content_posts write — failure must surface (RECENT OUTPUT 数据源不能静默)
    from supabase_writer import write_content_post
    _html_text = Path(html_path).read_text(encoding="utf-8")
    _word_count = len(re.sub(r"<[^>]+>", "", _html_text).split())
    write_content_post({
        "ghost_id": out["id"],
        "ghost_slug": out["slug"],
        "ghost_url": out["url"],
        "title": content.get("title", ""),
        "status": out["status"],
        "platform": "ghost",
        "html_file": str(html_path),
        "word_count": _word_count,
        "agent": "insight",
    })

    if do_publish and out.get("id"):
        try:
            verify_post = get_post(base_url, token, out["id"], formats="html")
            verify_html = verify_post.get("html") or ""
            verify = {
                "htmlLength": len(verify_html),
                "hasCustomStyle": ("8B3A2A" in verify_html) or ("hero" in verify_html),
                "hasImages": len(re.findall(r"<img", verify_html)),
            }
            print("\n🔍 Verification:")
            print(f"   HTML length: {verify['htmlLength']} chars")
            print(f"   Custom style: {'✅' if verify['hasCustomStyle'] else '⚠️ NOT FOUND'}")
            print(f"   Images: {verify['hasImages']}")
            if verify["htmlLength"] < 100:
                print("   ⚠️ WARNING: Content appears empty! Check post format (mobiledoc vs lexical).")
        except Exception as e:
            log.warning("Post-publish verification skipped: %s", e)

    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ghost Auto Publish (Admin API + JWT)")
    parser.add_argument("html_file", help="Blog HTML file path")
    parser.add_argument("--slug", help="Custom short slug")
    parser.add_argument("--draft", action="store_true", help="Create as draft (default: publish)")
    parser.add_argument("--update", metavar="POST_ID", help="Update existing post by ID")
    args = parser.parse_args()

    if not Path(args.html_file).exists():
        print(f"❌ File not found: {args.html_file}")
        sys.exit(1)

    try:
        publish(args.html_file, slug=args.slug, do_publish=not args.draft, update_id=args.update)
    except Exception as e:
        print(f"\n❌ {e}")
        log.error("publish failed: %s", e, exc_info=True)
        sys.exit(1)
