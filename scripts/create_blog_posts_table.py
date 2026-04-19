#!/usr/bin/env python3
"""
create_blog_posts_table.py — 在 Supabase 建立 blog_posts 表

使用 psycopg2 直连 PostgreSQL（Supabase REST API 不支持 DDL）

用法:
  python3 scripts/create_blog_posts_table.py
"""

import psycopg2
import sys
from pathlib import Path

DB_HOST = "db.cyzdudbtqunwzvxjumtr.supabase.co"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "H6z&&K5EJojs"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS blog_posts (
  id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  slug            text        UNIQUE NOT NULL,
  title           text        NOT NULL,
  platform        text        NOT NULL,   -- 'ghost' | 'wechat' | 'xhs' | 'x'
  status          text        NOT NULL,   -- 'published' | 'draft' | 'scheduled'
  published_at    timestamptz,
  ghost_id        text,                   -- Ghost post ID（发布后返回）
  wechat_media_id text,                   -- 微信 media_id
  series          text,                   -- 'great-minds' | null
  series_issue    int,                    -- 001, 002, 003...
  notes           text,
  created_at      timestamptz DEFAULT now(),
  updated_at      timestamptz DEFAULT now()
);
"""

# auto-update updated_at trigger
CREATE_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_blog_posts_updated_at ON blog_posts;
CREATE TRIGGER update_blog_posts_updated_at
  BEFORE UPDATE ON blog_posts
  FOR EACH ROW
  EXECUTE PROCEDURE update_updated_at_column();
"""


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=15,
    )


def main():
    print("▶ 连接 Supabase PostgreSQL...")
    try:
        conn = get_connection()
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        sys.exit(1)

    try:
        cur = conn.cursor()

        print("▶ 建立 blog_posts 表（如已存在则跳过）...")
        cur.execute(CREATE_TABLE_SQL)

        print("▶ 建立 updated_at 自动更新触发器...")
        cur.execute(CREATE_TRIGGER_SQL)

        conn.commit()
        print("✅ blog_posts 表建立完成")

        # 验证
        cur.execute("SELECT COUNT(*) FROM blog_posts")
        count = cur.fetchone()[0]
        print(f"✅ 当前记录数：{count}")

        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"❌ 建表失败：{e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
