#!/usr/bin/env python3
"""
WeChat Official Account Publisher v2.0
Usage:
  python3 publish_wechat.py <html_or_md_file> --title "标题" [--author "作者"] [--cover cover.jpg] [--digest "摘要"] [--draft] [--publish] [--force-new] [--update MEDIA_ID]

升级内容 (v2.0):
- 图片缓存：.wechat_cache.json 记录已上传图片，避免重复上传
- 草稿幂等更新：首次创建后存 media_id，后续自动更新同一草稿
- --force-new：忽略缓存，强制创建新草稿
- --update：指定 media_id 直接更新
- 内容图片自动上传：扫描 HTML 中的本地图片，上传后替换 src
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
import mimetypes
import uuid
import html as html_module
import hashlib

# ── Config ───────────────────────────────────────────────��──────────────
# ENV_FILE resolution order:
#   1. $GHOST_ENV_FILE (explicit override — set this when running from a
#      different workspace that reuses a shared .env.wechat)
#   2. <repo-root>/.env.wechat (default, local to this repo)
ENV_FILE = Path(os.environ.get("GHOST_ENV_FILE") or (Path(__file__).parent.parent / ".env.wechat"))
CACHE_FILE = ".wechat_cache.json"  # 相对于文章目录

def load_env():
    """Load credentials from .env.wechat"""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env.get("WECHAT_APP_ID"), env.get("WECHAT_APP_SECRET")


# ── Cache Management ────────────────────────────────────────────────────
def get_cache_path(article_dir):
    """获取缓存文件路径"""
    return Path(article_dir) / CACHE_FILE


def load_cache(article_dir):
    """加载缓存"""
    cache_path = get_cache_path(article_dir)
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except:
            pass
    return {"images": {}, "thumb_media_id": None, "draft_media_id": None}


def save_cache(article_dir, cache):
    """保存缓存"""
    cache_path = get_cache_path(article_dir)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def get_file_hash(file_path):
    """计算文件 MD5 哈希"""
    return hashlib.md5(Path(file_path).read_bytes()).hexdigest()


# ── Token Cache ─────────────────────────────────────────────────────────
TOKEN_CACHE = Path("/tmp/wechat_token.json")

def get_access_token(app_id, app_secret, force=False):
    """Get access token with caching (2h TTL)"""
    if not force and TOKEN_CACHE.exists():
        cache = json.loads(TOKEN_CACHE.read_text())
        if cache.get("expires_at", 0) > time.time() + 300:
            return cache["access_token"]
    
    url = (
        f"https://api.weixin.qq.com/cgi-bin/token?"
        f"grant_type=client_credential&appid={app_id}&secret={app_secret}"
    )
    resp = json.loads(urllib.request.urlopen(url, timeout=15).read())
    if "access_token" not in resp:
        print(f"❌ Token error: {resp}", file=sys.stderr)
        sys.exit(1)
    
    cache = {
        "access_token": resp["access_token"],
        "expires_at": time.time() + resp.get("expires_in", 7200),
    }
    TOKEN_CACHE.write_text(json.dumps(cache))
    return cache["access_token"]


# ── Multipart Upload Helper ─────────────────────────────────────────────
def multipart_upload(url, file_path, field_name="media"):
    """Upload file via multipart/form-data"""
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"
    
    file_path = Path(file_path)
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    file_data = file_path.read_bytes()
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
    
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp


# ── Media Upload ────────────────────────────────────────────────────────
def upload_thumb(token, image_path, cache, article_dir):
    """Upload cover image as permanent material → thumb_media_id（带缓存）"""
    file_hash = get_file_hash(image_path)
    
    # 检查缓存
    if cache.get("thumb_hash") == file_hash and cache.get("thumb_media_id"):
        print(f"✅ Cover cached: {cache['thumb_media_id']}")
        return cache["thumb_media_id"]
    
    url = (
        f"https://api.weixin.qq.com/cgi-bin/material/add_material?"
        f"access_token={token}&type=thumb"
    )
    resp = multipart_upload(url, image_path)
    if "media_id" not in resp:
        print(f"❌ Thumb upload error: {resp}", file=sys.stderr)
        sys.exit(1)
    
    # 更新缓存
    cache["thumb_media_id"] = resp["media_id"]
    cache["thumb_hash"] = file_hash
    save_cache(article_dir, cache)
    
    print(f"✅ Cover uploaded: {resp['media_id']}")
    return resp["media_id"]


def upload_content_image(token, image_path, cache, article_dir):
    """Upload inline image for article content → url（带缓存）"""
    file_hash = get_file_hash(image_path)
    cache_key = str(Path(image_path).name)
    
    # 检查缓存
    if cache.get("images", {}).get(cache_key, {}).get("hash") == file_hash:
        cached_url = cache["images"][cache_key]["url"]
        print(f"✅ Image cached: {cached_url[:60]}...")
        return cached_url
    
    url = (
        f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?"
        f"access_token={token}"
    )
    resp = multipart_upload(url, image_path)
    if "url" not in resp:
        print(f"❌ Image upload error: {resp}", file=sys.stderr)
        return None
    
    # 更新缓存
    if "images" not in cache:
        cache["images"] = {}
    cache["images"][cache_key] = {"hash": file_hash, "url": resp["url"]}
    save_cache(article_dir, cache)
    
    print(f"✅ Image uploaded: {resp['url'][:60]}...")
    return resp["url"]


def process_content_images(token, content, article_dir, cache):
    """扫描 HTML 中的本地图片，上传后替换 src"""
    # 匹配 src="..." 中的本地路径
    img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    
    def replace_image(match):
        full_match = match.group(0)
        src = match.group(1)
        
        # 跳过已经是 URL 的图片
        if src.startswith(('http://', 'https://')):
            return full_match
        
        # 处理 base64 图片：提取、存临时文件、上传
        if src.startswith('data:'):
            import base64 as b64mod
            import tempfile
            # 解析 data:image/png;base64,xxxxx
            m = re.match(r'data:image/(\w+);base64,(.+)', src, re.DOTALL)
            if not m:
                print(f"⚠️ Unsupported data URI format, skipping")
                return full_match
            ext = m.group(1).replace('jpeg', 'jpg')
            b64data = m.group(2)
            # 用完整内容 hash 做缓存 key（不能只用前200字符，JPEG文件头相同会碰撞）
            content_hash = hashlib.md5(b64data.encode()).hexdigest()[:16]
            cache_key = f"b64_{content_hash}.{ext}"
            if cache.get("images", {}).get(cache_key, {}).get("hash") == content_hash:
                cached_url = cache["images"][cache_key]["url"]
                print(f"✅ Base64 image cached: {cached_url[:60]}...")
                return full_match.replace(src, cached_url)
            # 写临时文件并上传
            tmp_path = Path(tempfile.mktemp(suffix=f'.{ext}'))
            try:
                tmp_path.write_bytes(b64mod.b64decode(b64data))
                new_url = upload_content_image(token, tmp_path, cache, article_dir)
                if new_url:
                    # 覆盖缓存 key 为 b64 hash
                    if "images" not in cache:
                        cache["images"] = {}
                    cache["images"][cache_key] = {"hash": content_hash, "url": new_url}
                    save_cache(article_dir, cache)
                    return full_match.replace(src, new_url)
            finally:
                tmp_path.unlink(missing_ok=True)
            return full_match
        
        # 解析本地路径
        if src.startswith('/'):
            img_path = Path(src)
        else:
            img_path = Path(article_dir) / src
        
        if not img_path.exists():
            print(f"⚠️ Image not found: {img_path}")
            return full_match
        
        # 上传并替换
        new_url = upload_content_image(token, img_path, cache, article_dir)
        if new_url:
            return full_match.replace(src, new_url)
        return full_match
    
    return img_pattern.sub(replace_image, content)


# ── Content Processing ──────────────────────────────────────────────────
def read_content(file_path, token=None, article_dir=None, cache=None):
    """Read content file (HTML or Markdown)"""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")
    
    if path.suffix in (".html", ".htm"):
        content = text
    else:
        # Markdown → 使用 wechat_formatter 转换
        try:
            from wechat_formatter import md_to_wechat
            content = md_to_wechat(text)
        except ImportError:
            print("❌ wechat_formatter.py not found", file=sys.stderr)
            sys.exit(1)
    
    # 处理内容中的本地图片
    if token and article_dir and cache:
        content = process_content_images(token, content, article_dir, cache)
    
    return content


# ── Generate Default Cover ──────────────────────────────────────────────
def generate_default_cover(title):
    """Generate a simple cover image using PIL"""
    cover_path = Path("/tmp/wechat_cover.jpg")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 2.35:1 ratio (WeChat recommended)
        img = Image.new("RGB", (900, 383), color=(139, 58, 42))  # #8B3A2A
        draw = ImageDraw.Draw(img)
        
        # Try to find a CJK font
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
        ]
        font = None
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, 36)
                    break
                except:
                    pass
        if font is None:
            font = ImageFont.load_default()
        
        # Draw title text centered
        max_chars = 16
        lines = []
        for i in range(0, len(title), max_chars):
            lines.append(title[i:i+max_chars])
        
        y_start = (383 - len(lines) * 50) // 2
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            x = (900 - w) // 2
            draw.text((x, y_start + i * 50), line, fill="white", font=font)
        
        # Add author line
        try:
            small_font = ImageFont.truetype(font_paths[0], 20) if os.path.exists(font_paths[0]) else font
        except:
            small_font = font
        author_text = "Eason Zhang"
        bbox = draw.textbbox((0, 0), author_text, font=small_font)
        aw = bbox[2] - bbox[0]
        draw.text(((900 - aw) // 2, 330), author_text, fill=(197, 150, 58), font=small_font)
        
        img.save(str(cover_path), "JPEG", quality=90)
        print(f"✅ Cover generated: {cover_path}")
        return cover_path
        
    except ImportError:
        print("❌ PIL not available, please provide a cover image with --cover", file=sys.stderr)
        sys.exit(1)


# ── Draft / Publish ─────────────────────────────────────────────────────
def create_draft(token, title, content, thumb_media_id, author="Eason", digest=""):
    """Create article draft"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    
    article = {
        "title": title,
        "author": author,
        "digest": digest[:120] if digest else "",
        "content": content,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    
    data = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    
    if "media_id" not in resp:
        print(f"❌ Draft error: {resp}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Draft created: {resp['media_id']}")
    return resp["media_id"]


def update_draft(token, media_id, title, content, thumb_media_id, author="Eason", digest=""):
    """Update existing draft（幂等更新）"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/update?access_token={token}"
    
    article = {
        "title": title,
        "author": author,
        "digest": digest[:120] if digest else "",
        "content": content,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    
    data = json.dumps({
        "media_id": media_id,
        "index": 0,  # 更新第一篇文章
        "articles": article,
    }, ensure_ascii=False).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    
    if resp.get("errcode", 0) != 0:
        print(f"❌ Draft update error: {resp}", file=sys.stderr)
        # 如果更新失败（比如草稿已删除），返回 None 让调用方创建新草稿
        return None
    
    print(f"✅ Draft updated: {media_id}")
    return media_id


def publish_draft(token, media_id):
    """Publish from draft"""
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"
    data = json.dumps({"media_id": media_id}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    
    if resp.get("errcode", 0) != 0 and "publish_id" not in resp:
        print(f"❌ Publish error: {resp}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Published! publish_id: {resp.get('publish_id', 'N/A')}")
    return resp


# ── Main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="WeChat Official Account Publisher v2.0")
    parser.add_argument("file", help="HTML or Markdown file to publish")
    parser.add_argument("--title", required=True, help="Article title")
    parser.add_argument("--author", default="Eason", help="Author name")
    parser.add_argument("--cover", help="Cover image path (auto-generated if omitted)")
    parser.add_argument("--digest", default="", help="Article summary (≤120 chars)")
    parser.add_argument("--draft", action="store_true", help="Create draft only (default)")
    parser.add_argument("--publish", action="store_true", help="Publish immediately")
    parser.add_argument("--force-new", action="store_true", help="Ignore cache, create new draft")
    parser.add_argument("--update", metavar="MEDIA_ID", help="Update existing draft by media_id")
    parser.add_argument("--token", help="Override access token")
    args = parser.parse_args()
    
    app_id, app_secret = load_env()
    if not app_id or not app_secret:
        print("❌ Missing WECHAT_APP_ID/WECHAT_APP_SECRET in .env.wechat", file=sys.stderr)
        sys.exit(1)
    
    # 确定文章目录
    article_dir = Path(args.file).parent.resolve()
    
    # 加载缓存
    cache = load_cache(article_dir) if not args.force_new else {"images": {}}
    
    # 1. Get token
    token = args.token or get_access_token(app_id, app_secret)
    print(f"🔑 Token OK")
    
    # 2. Read & convert content（同时处理内容图片）
    content = read_content(args.file, token, article_dir, cache)
    print(f"📄 Content loaded ({len(content)} chars)")
    
    # 3. Upload cover
    if args.cover:
        cover_path = Path(args.cover)
    else:
        cover_path = generate_default_cover(args.title)
    thumb_media_id = upload_thumb(token, cover_path, cache, article_dir)
    
    # 4. Create or update draft
    existing_media_id = args.update or (cache.get("draft_media_id") if not args.force_new else None)
    
    if existing_media_id:
        # 尝试更新现有草稿
        media_id = update_draft(
            token, existing_media_id, args.title, content, thumb_media_id,
            author=args.author, digest=args.digest,
        )
        if media_id is None:
            # 更新失败，创建新草稿
            print("⚠️ Update failed, creating new draft...")
            media_id = create_draft(
                token, args.title, content, thumb_media_id,
                author=args.author, digest=args.digest,
            )
    else:
        # 创建新草稿
        media_id = create_draft(
            token, args.title, content, thumb_media_id,
            author=args.author, digest=args.digest,
        )
    
    # 保存 draft_media_id 到缓存
    cache["draft_media_id"] = media_id
    save_cache(article_dir, cache)
    
    # 5. Publish if requested
    if args.publish:
        publish_draft(token, media_id)
    else:
        print(f"📝 Draft ready. Run with --publish to publish, or publish from WeChat admin.")
        print(f"   Draft media_id: {media_id}")
        print(f"   Cache saved to: {get_cache_path(article_dir)}")


if __name__ == "__main__":
    main()
