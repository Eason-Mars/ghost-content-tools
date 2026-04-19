#!/usr/bin/env python3
"""
supabase_writer.py — Mars 专属 Supabase 写入工具
核心原则：写入失败只 warn，不影响主流程
"""
import sys
import json
from datetime import datetime
from pathlib import Path


def _get_client():
    """获取 Supabase client，失败返回 None"""
    try:
        import os
        import sys as _sys
        from supabase import create_client

        # [vault_migrated 2026-04-13] 优先通过 VaultClient 读取凭证
        try:
            _sys.path.insert(0, '/Users/dljapan/.openclaw/workspace')
            from scripts.vault_api import vault as _vault
            url = _vault.get('supabase_url')
            key = _vault.get('supabase_key')
        except ImportError:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')

        if not url or not key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY not set")

        return create_client(url, key)
    except Exception as e:
        print(f"[WARN] Supabase 连接失败：{e}", file=sys.stderr)
        return None


def write_eval_score(score_json_path: str) -> bool:
    """
    将 eval_scores JSON 文件写入数据库
    score_json_path: intel/eval_scores/xxx.json 的路径
    返回 True=成功，False=失败（不 raise）
    """
    try:
        client = _get_client()
        if not client:
            return False

        with open(score_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        dims = data.get("dimensions", {})

        row = {
            "report_file": data.get("report_file", ""),
            "report_type": data.get("report_type", ""),
            "report_timestamp": data.get("timestamp"),
            "scored_at": data.get("scored_at", datetime.now().isoformat()),
            "total_score": data.get("total_score"),
            "dim_direction": dims.get("方向明确性", {}).get("score"),
            "dim_verifiable": dims.get("假设可验证性", {}).get("score"),
            "dim_data_support": dims.get("数据支撑完整性", {}).get("score"),
            "dim_consistency": dims.get("内部一致性", {}).get("score"),
            "dim_stop_loss": dims.get("止损条件", {}).get("score"),
            "flags": data.get("flags", []),
            "short_term_direction": data.get("short_term_direction", ""),
            "short_term_assumption": data.get("short_term_assumption", ""),
            "watchlist_symbols": data.get("watchlist_symbols", []),
            "rubric_version": data.get("rubric_version", "v0.2"),
            "raw_json": data,
            "agent": data.get("agent", "pathfinder"),
            "output_type": data.get("report_type", ""),
        }

        result = client.table("eval_scores").insert(row).execute()
        print(f"[DB] eval_score 写入成功：{data.get('report_file')}")
        return True

    except Exception as e:
        print(f"[WARN] eval_score DB 写入失败（本地文件不受影响）：{e}", file=sys.stderr)
        return False


def write_hypothesis_verification(verification: dict) -> bool:
    """
    写入假设核验结果到 hypothesis_tracking
    verification: {report_file, timeframe, direction, assumption, actual_result, actual_change_pct, hit, verified_at, days_window}
    """
    try:
        client = _get_client()
        if not client:
            return False
        row = {
            "report_file": verification.get("report_file", ""),
            "timeframe": "短期",
            "direction": verification.get("assumed_direction", ""),
            "assumption": verification.get("assumed_assumption", ""),
            "actual_result": verification.get("actual_result", ""),
            "verified_at": verification.get("verified_at"),
            "hit": verification.get("hit"),
            "verify_at": f"T+{verification.get('days_window', 5)}",
        }
        client.table("hypothesis_tracking").insert(row).execute()
        print(f"[DB] hypothesis_verification 写入成功：{row['report_file'][:30]}")
        return True
    except Exception as e:
        print(f"[WARN] hypothesis_tracking DB 写入失败：{e}", file=sys.stderr)
        return False


def write_picks_tracking(pick: dict) -> bool:
    """
    写入选股追踪记录
    pick: {ticker, name, direction, entry_price, target_price, stop_loss, analyst, strategy, rationale, pick_date}
    """
    try:
        client = _get_client()
        if not client:
            return False
        result = client.table("picks_tracking").insert(pick).execute()
        print(f"[DB] pick 写入成功：{pick.get('ticker')}")
        return True
    except Exception as e:
        print(f"[WARN] picks_tracking DB 写入失败：{e}", file=sys.stderr)
        return False


def update_picks_tracking(ticker: str, updates: dict) -> bool:
    """
    更新 picks_tracking 的平仓字段
    ticker: 股票代码
    updates: {close_price, close_date, hit, status} 中的任意字段
    只更新最新一条 active 记录
    """
    try:
        client = _get_client()
        if not client:
            return False
        # 找最新的 active 记录
        existing = client.table("picks_tracking")\
            .select("id")\
            .eq("ticker", ticker)\
            .eq("status", "active")\
            .order("pick_date", desc=True)\
            .limit(1)\
            .execute()
        if not existing.data:
            print(f"[WARN] picks_tracking 未找到 {ticker} 的 active 记录", file=sys.stderr)
            return False
        record_id = existing.data[0]["id"]
        client.table("picks_tracking").update(updates).eq("id", record_id).execute()
        print(f"[DB] picks_tracking 平仓更新成功：{ticker}")
        return True
    except Exception as e:
        print(f"[WARN] picks_tracking 平仓更新失败：{e}", file=sys.stderr)
        return False


def write_mistake_log(scene: str, rule_violated: str, root_cause: str, fix: str, category: str = "process"):
    """
    写入错误日志。
    返回 True=成功写入，"skipped"=已存在跳过，False=失败。
    """
    try:
        client = _get_client()
        if not client:
            return False
        # 防重复：检查是否已有相同 scene
        existing = client.table("mistake_log").select("id").eq("scene", scene[:100]).execute()
        if existing.data:
            print(f"[DB] mistake_log 已存在，跳过：{scene[:40]}")
            return "skipped"
        row = {
            "scene": scene,
            "rule_violated": rule_violated,
            "root_cause": root_cause,
            "fix": fix,
            "category": category,
        }
        client.table("mistake_log").insert(row).execute()
        print(f"[DB] mistake_log 写入成功：{scene[:40]}")
        return True
    except Exception as e:
        print(f"[WARN] mistake_log DB 写入失败：{e}", file=sys.stderr)
        return False


def write_skill_usage(skill_name: str, mode: str = None, workspace: str = None,
                       task: str = "", improvement: str = "", category: str = "",
                       # legacy compat params (kept for existing callers)
                       agent: str = None, trigger_context: str = None,
                       task_id: str = None, success: bool = True) -> bool:
    """
    记录 lesson-keeper Skill 使用情况到 skill_usage 表。

    lesson-keeper 调用时：
      skill_name: 'lesson-keeper' / 'lesson-keeper-zh' / 'lesson-keeper-internal'
      mode:       'correction' / 'feature-request' / 'error' / 'knowledge' / 'task-review'
      workspace:  agent workspace 路径
      task:       任务标题（task-review 模式）
      improvement: 改进点（task-review 模式）
      category:   BAD-X 分类（correction 模式）

    字段映射（skill_usage 表只有 skill_name / agent / trigger_context / task_id / success）：
      mode       → agent
      category/task/improvement → trigger_context（JSON 编码）
    """
    try:
        client = _get_client()
        if not client:
            return False

        # Build trigger_context from lesson-keeper params if present
        if mode is not None:
            ctx_data = {}
            if workspace:
                ctx_data["workspace"] = workspace
            if task:
                ctx_data["task"] = task
            if improvement:
                ctx_data["improvement"] = improvement
            if category:
                ctx_data["category"] = category
            _trigger_context = json.dumps(ctx_data, ensure_ascii=False) if ctx_data else None
            _agent = mode
        else:
            # legacy call path
            _trigger_context = trigger_context
            _agent = agent

        row = {
            "skill_name": skill_name,
            "agent": _agent,
            "trigger_context": _trigger_context,
            "task_id": task_id,
            "success": success,
        }
        client.table("skill_usage").insert(row).execute()
        print(f"[DB] skill_usage 写入成功：{skill_name} / {_agent}")
        return True
    except Exception as e:
        print(f"[WARN] skill_usage 写入失败：{e}", file=sys.stderr)
        return False


def write_improvement_log(agent: str, from_version: str, to_version: str,
                           low_score_dims: list, proposal_json: dict,
                           changes_summary: str) -> bool:
    """写入 rubric 升级记录"""
    try:
        client = _get_client()
        if not client:
            return False
        row = {
            "agent": agent,
            "rubric_version_from": from_version,
            "rubric_version_to": to_version,
            "low_score_dims": low_score_dims,
            "proposal_json": proposal_json,
            "changes_summary": changes_summary,
        }
        client.table("agent_improvement_log").insert(row).execute()
        print(f"[DB] improvement_log 写入成功：{agent} {from_version}→{to_version}")
        return True
    except Exception as e:
        print(f"[WARN] improvement_log DB 写入失败：{e}", file=sys.stderr)
        return False


def write_content_post(post: dict) -> bool:
    """
    写入/更新内容发布记录（upsert 语义）
    post: {ghost_id, ghost_slug, ghost_url, title, status, platform, topic_tags, series, word_count, html_file, agent}
    - 已存在（按 ghost_id 匹配）→ UPDATE status / ghost_url / ghost_slug 等字段（确保 draft→published 状态同步）
    - 不存在 → INSERT
    """
    try:
        client = _get_client()
        if not client:
            return False
        # 按 ghost_id upsert：已存在时更新状态及关键字段，确保 draft→published 能同步
        if post.get("ghost_id"):
            existing = client.table("content_posts").select("id").eq("ghost_id", post["ghost_id"]).execute()
            if existing.data:
                # 只更新可能变化的字段，不覆盖 created_at 等固定字段
                update_fields = {k: v for k, v in post.items() if k in (
                    "status", "ghost_url", "ghost_slug", "title", "word_count", "html_file"
                )}
                client.table("content_posts").update(update_fields).eq("ghost_id", post["ghost_id"]).execute()
                print(f"[DB] content_post 已更新（status={post.get('status')}）：{post.get('title', '')[:30]}")
                return True
        result = client.table("content_posts").insert(post).execute()
        print(f"[DB] content_post 写入成功（status={post.get('status')}）：{post.get('title', '')[:30]}")
        return True
    except Exception as e:
        print(f"[WARN] content_post DB 写入失败：{e}", file=sys.stderr)
        return False


def write_arti_requirement(req: dict) -> bool:
    """
    写入/更新 ARTI 需求记录
    req: {req_id, title, description, source, priority, assignee, status, blocked_reason, category, due_date}
    """
    try:
        client = _get_client()
        if not client:
            return False
        # upsert by req_id
        if req.get("req_id"):
            result = client.table("arti_requirements").upsert(req, on_conflict="req_id").execute()
        else:
            result = client.table("arti_requirements").insert(req).execute()
        print(f"[DB] arti_requirement 写入成功：{req.get('req_id', '')} {req.get('title', '')[:30]}")
        return True
    except Exception as e:
        print(f"[WARN] arti_requirement DB 写入失败：{e}", file=sys.stderr)
        return False


def write_arti_delivery(delivery: dict) -> bool:
    """
    写入 ARTI 交付记录
    delivery: {req_id, title, assignee, promised_at, delivered_at, quality_score, notes, status}
    """
    try:
        client = _get_client()
        if not client:
            return False
        result = client.table("arti_deliveries").insert(delivery).execute()
        print(f"[DB] arti_delivery 写入成功：{delivery.get('title', '')[:30]}")
        return True
    except Exception as e:
        print(f"[WARN] arti_delivery DB 写入失败：{e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "skill_usage":
        # CLI: supabase_writer.py skill_usage <skill_name> <mode> <workspace> [task] [improvement] [category]
        args = sys.argv[2:]
        if len(args) < 3:
            print("Usage: supabase_writer.py skill_usage <skill_name> <mode> <workspace> [task] [improvement] [category]",
                  file=sys.stderr)
            sys.exit(1)
        _skill_name  = args[0]
        _mode        = args[1]
        _workspace   = args[2]
        _task        = args[3] if len(args) > 3 else ""
        _improvement = args[4] if len(args) > 4 else ""
        _category    = args[5] if len(args) > 5 else ""
        ok = write_skill_usage(
            skill_name=_skill_name,
            mode=_mode,
            workspace=_workspace,
            task=_task,
            improvement=_improvement,
            category=_category,
        )
        sys.exit(0 if ok else 1)
    else:
        # 连接测试
        client = _get_client()
        if client:
            print("✅ supabase_writer 连接测试通过")
        else:
            print("❌ 连接失败")
