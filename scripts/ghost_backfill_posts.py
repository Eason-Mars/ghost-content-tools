#!/usr/bin/env python3
"""
ghost_backfill_posts.py — 从 Ghost Admin（CDP）抓取历史文章并写入 Supabase content_posts
用法：python3 ghost_backfill_posts.py [--dry-run]
前置条件：浏览器已打开 eason.ghost.io/ghost/
"""

import sys
import argparse
from pathlib import Path

# 确保 scripts 目录在 path 里
sys.path.insert(0, str(Path(__file__).parent))


def find_ghost_page(browser):
    """在所有 contexts/pages 里找 eason.ghost.io 的页面"""
    for context in browser.contexts:
        for page in context.pages:
            if "eason.ghost.io" in page.url:
                return page
    return None


# 已知系列标签
SERIES_TAGS = ["Great Minds", "APAG", "Great Mind"]


def extract_series(tags: list) -> str:
    """从 tags 列表里提取系列标签"""
    if not tags:
        return ""
    for tag in tags:
        name = tag.get("name", "") if isinstance(tag, dict) else str(tag)
        for s in SERIES_TAGS:
            if s.lower() in name.lower():
                return s
    return ""


def fetch_posts_via_cdp(ghost_page) -> list:
    """通过浏览器 CDP 调用 Ghost Admin API 拉取已发布文章
    注意：tags 字段需要用 include=tags 参数，不是 fields"""
    posts = ghost_page.evaluate("""
        async () => {
            const resp = await fetch(
                '/ghost/api/admin/posts/?limit=all&fields=id,slug,title,status,published_at,url,custom_excerpt&filter=status%3Apublished&include=tags',
                { credentials: 'include' }
            );
            if (!resp.ok) {
                throw new Error('Ghost API 返回错误：' + resp.status);
            }
            const data = await resp.json();
            return data.posts || [];
        }
    """)
    return posts


def build_content_post(post: dict) -> dict:
    """把 Ghost API 的 post 对象转换成 content_posts 表的记录"""
    tags = post.get("tags") or []
    topic_tags = [t.get("name", "") for t in tags if isinstance(t, dict)]
    series = extract_series(tags)

    return {
        "ghost_id": post.get("id"),
        "ghost_slug": post.get("slug"),
        "ghost_url": post.get("url"),
        "title": post.get("title"),
        "status": post.get("status", "published"),
        "platform": "ghost",
        "published_at": post.get("published_at"),
        "topic_tags": topic_tags,
        "series": series,
        "agent": "insight",
    }


def main():
    parser = argparse.ArgumentParser(description="Ghost 历史文章补录到 Supabase content_posts")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写入 DB")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright
    from supabase_writer import write_content_post

    print("🔌 连接 Chrome CDP（端口18800）...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        except Exception as e:
            print(f"❌ 无法连接 CDP：{e}")
            print("  请确保 OpenClaw 浏览器已启动（CDP port 18800）")
            sys.exit(1)

        ghost_page = find_ghost_page(browser)
        if not ghost_page:
            print("❌ 未找到 Ghost Admin 页面，请先在浏览器打开 eason.ghost.io/ghost/")
            sys.exit(1)

        print(f"✅ 找到 Ghost 页面：{ghost_page.url}")
        print("📡 调用 Ghost Admin API 拉取文章...")

        try:
            posts = fetch_posts_via_cdp(ghost_page)
        except Exception as e:
            print(f"❌ 调用 Ghost API 失败：{e}")
            sys.exit(1)

        print(f"📋 共找到 {len(posts)} 篇已发布文章")

        written = 0
        skipped = 0
        failed = 0

        for i, post in enumerate(posts, 1):
            record = build_content_post(post)
            title_short = (record.get("title") or "")[:40]
            pub_date = (record.get("published_at") or "")[:10]
            tags_str = ", ".join(record.get("topic_tags") or []) or "(无标签)"
            series_str = record.get("series") or ""

            print(f"  [{i:03d}] {pub_date} | {title_short} | tags={tags_str}"
                  + (f" | series={series_str}" if series_str else ""))

            if args.dry_run:
                print("        [dry-run] 跳过写入")
                continue

            result = write_content_post(record)
            if result is True:
                # 判断是写入成功还是跳过（write_content_post 对已存在的也返回 True）
                # 通过标准输出区分（write_content_post 内部已打印）
                written += 1
            else:
                failed += 1

        if not args.dry_run:
            print(f"\n✅ 完成：写入/跳过={written}，失败={failed}")
        else:
            print(f"\n[dry-run] 共 {len(posts)} 篇，未写入")


if __name__ == "__main__":
    main()
