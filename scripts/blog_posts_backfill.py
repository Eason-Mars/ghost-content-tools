#!/usr/bin/env python3
"""
blog_posts_backfill.py -- 历史博文数据补录到 Supabase blog_posts 表
幂等可重跑（on_conflict slug DO NOTHING）
"""

import psycopg2
import sys

DB_HOST = "db.cyzdudbtqunwzvxjumtr.supabase.co"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "H6z&&K5EJojs"

ALL_POSTS = [
    # --- 已发布 ---
    {"slug": "about-me",                 "title": "在东京，我投资了6家麻辣烫店",                                        "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "ai-investment-lab",        "title": "我用AI帮自己建了一个私人投资研究院",                                "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "ai-killed-khamenei",       "title": "AI真的杀死了哈梅内伊吗？",                                          "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "chessboard-40",            "title": "棋盘第40格，个人创业者该怎么站位",                                  "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "org-memory",               "title": "为什么你的AI系统会开始记错",                                        "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "saas-to-ai",               "title": "我做了8年SaaS，然后转向了AI",                                       "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "ai-vs-enterprise-software","title": "AI不会消灭企业软件，但会让它们面目全非",                            "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "multi-agent-chaos",        "title": "我们想把AI Agent分工协作，结果把整个系统搞崩了",                    "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "dual-agent-setup",         "title": "今天用了不到一小时，搭好了AI双Agent协作系统",                       "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "content-agent",            "title": "我给自己的AI系统，加了一个内容团队",                                "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "ai-team-upgrade",          "title": "我的AI投研团队，今天升级了",                                        "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "ai-team-evolution",        "title": "我的AI团队，是怎么进化的",                                          "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "venture-studio-upgrade",   "title": "一个周末，我把AI投研系统从能跑升级到能用",                          "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "ai-team-management",       "title": "从1到6：一个人怎么管一支AI团队",                                    "status": "published", "published_at": "2026-03-01T00:00:00+00:00"},
    {"slug": "not-for-quant",            "title": "龙虾不能炒股——用了一个多月大模型投研后不得不说的实话",              "status": "published", "published_at": "2026-03-16T00:00:00+00:00"},
    {"slug": "tokyo-leasing-trust",      "title": "在东京租到一家店，需要的不是钱，是信任",                            "status": "published", "published_at": "2026-03-18T00:00:00+00:00"},
    {"slug": "ai-memory",                "title": "你以为 AI 学会了，下次它还是那样",                                  "status": "published", "published_at": "2026-03-19T00:00:00+00:00"},
    {"slug": "ai-native-app-development","title": "大模型时代，最贵的错误是把 AI 当主角",                              "status": "published", "published_at": "2026-03-24T00:00:00+00:00"},
    {"slug": "great-minds-003",          "title": "这周，聪明人在想什么 | Issue 003",                                  "status": "published", "published_at": "2026-03-28T00:00:00+00:00", "series": "great-minds", "series_issue": 3},
    # --- 草稿 ---
    {"slug": "harness-engineering",      "title": "Harness Engineering：让错误变得不可能发生",                         "status": "draft",     "published_at": None},
]


def get_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD, connect_timeout=15,
    )


def main():
    print("Connecting to Supabase PostgreSQL...")
    try:
        conn = get_connection()
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    inserted = 0
    skipped = 0

    try:
        cur = conn.cursor()

        for post in ALL_POSTS:
            cur.execute("""
                INSERT INTO blog_posts (slug, title, platform, status, published_at, series, series_issue)
                VALUES (%s, %s, 'ghost', %s, %s, %s, %s)
                ON CONFLICT (slug) DO NOTHING
            """, (
                post["slug"],
                post["title"],
                post["status"],
                post.get("published_at"),
                post.get("series"),
                post.get("series_issue"),
            ))
            if cur.rowcount > 0:
                print(f"  OK inserted: {post['slug']}")
                inserted += 1
            else:
                print(f"  SKIP (exists): {post['slug']}")
                skipped += 1

        conn.commit()

        cur.execute("SELECT COUNT(*) FROM blog_posts")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM blog_posts WHERE status='published'")
        pub = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM blog_posts WHERE status='draft'")
        draft = cur.fetchone()[0]

        print(f"\nDone: inserted={inserted}, skipped={skipped}")
        print(f"blog_posts total={total} (published={pub}, draft={draft})")

        if total >= 19:
            print(f"PASS: {total} records >= 19 expected")
        else:
            print(f"WARN: only {total} records, expected >= 19")

        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
