#!/usr/bin/env python3
"""
小红书卡片 v2:字更大、无页眉页脚、内容填满版面
1242×1660 竖版
"""

from pathlib import Path

OUT_DIR = Path('/Users/dljapan/.openclaw/workspace/personal-brand/content/drafts/2026-03-19-ai-memory/xhs')
OUT_DIR.mkdir(parents=True, exist_ok=True)

RED    = '#8B3A2A'
RED_LT = '#B85040'
GOLD   = '#C5963A'
CREAM  = '#FAF6F1'
GRAY   = '#6B6560'
TEXT   = '#1A1714'
FF     = '"PingFang SC","Noto Sans SC","Hiragino Sans GB","Microsoft YaHei",sans-serif'

BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1242px; height:1660px; overflow:hidden;
       font-family:{FF}; color:{TEXT}; background:{CREAM}; }}
.card {{ width:1242px; height:1660px; display:flex;
         flex-direction:column; position:relative; overflow:hidden; }}
"""

# ── 封面 ─────────────────────────────────────────────────────────────────
def cover_card():
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{BASE_CSS}
.bg {{ position:absolute;inset:0;
       background:linear-gradient(150deg,{RED} 0%,#5C1F12 60%,#2E0E08 100%); }}
.content {{ position:relative;z-index:1;height:100%;
            display:flex;flex-direction:column;padding:96px 88px; }}
.tag {{ font-size:28px;color:rgba(255,255,255,0.5);
        letter-spacing:4px;font-weight:600;margin-bottom:56px; }}
.title {{ font-size:108px;font-weight:900;color:#fff;
          line-height:1.15;letter-spacing:3px;flex:1; }}
.accent {{ color:{GOLD}; }}
.sub {{ font-size:40px;color:rgba(255,255,255,0.75);
        line-height:1.6;margin-bottom:64px;
        border-left:5px solid {GOLD};padding-left:28px; }}
.author {{ font-size:28px;color:rgba(255,255,255,0.45);letter-spacing:2px; }}
</style></head><body><div class="card">
  <div class="bg"></div>
  <div class="content">
    <div class="tag">AI × 工作方式</div>
    <div class="title">AI说<br><span class="accent">"完成了"</span><br>的那一刻</div>
    <div class="sub">才是真正工作的开始</div>
    <div class="author">Eason · 走南闯北</div>
  </div>
</div></body></html>"""

# ── 第1张:开篇 ─────────────────────────────────────────────────────────
def card_opening():
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{BASE_CSS}
.card {{ background:#fff; }}
.top {{ height:12px;background:linear-gradient(90deg,{RED},{GOLD},{RED_LT}); }}
.body {{ flex:1;padding:72px 88px;display:flex;flex-direction:column;justify-content:center; }}
.chapter {{ font-size:26px;color:{GOLD};font-weight:700;letter-spacing:3px;margin-bottom:24px; }}
.h2 {{ font-size:60px;font-weight:900;color:{RED};line-height:1.3;margin-bottom:36px; }}
.bar {{ width:64px;height:6px;background:linear-gradient(90deg,{RED},{GOLD});
        border-radius:3px;margin-bottom:48px; }}
.p {{ font-size:38px;line-height:1.85;color:{TEXT};margin-bottom:28px; }}
.em {{ color:{RED};font-weight:700; }}
.quote {{ margin:8px 0 28px;padding:28px 36px;
          border-left:6px solid {GOLD};background:{CREAM};border-radius:0 16px 16px 0; }}
.quote p {{ font-size:40px;line-height:1.8;color:#5a3020;font-style:italic;margin:0; }}
.num {{ position:absolute;bottom:48px;right:72px;
        font-size:26px;color:#D0C8C2;font-weight:600; }}
</style></head><body><div class="card">
  <div class="top"></div>
  <div class="body">
    <div class="chapter">— 01 —</div>
    <div class="h2">"完成了"<br>是最危险的三个字</div>
    <div class="bar"></div>
    <p class="p">AI最危险的时刻，不是它说<span class="em">"我不会"</span>，<br>而是它说<span class="em">"完成了"</span>。</p>
    <p class="p">说"我不会"，你会去找别的办法。<br>说"完成了"，你就真的以为完成了。</p>
    <div class="quote"><p>今天文件一个个建好，汇报一条条来了，听起来很顺利。<br>但我没有停在"顺利"这里。</p></div>
  </div>
  <div class="num">1 / 6</div>
</div></body></html>"""

# ── 第2张:追问01-03 ────────────────────────────────────────────────────
def card_qa_1():
    qas = [
        ("追问 01", ""调用规则写清楚了吗?"", f"SKILL.md 没区分 Level 1/2/3<br>系统<span style='color:{RED};font-weight:700;'>不知道什么时候读深度档案</span>"),
        ("追问 02", ""触发场景定义了吗?"", f"触发条件模糊——什么叫"展开某位大师"?<br><span style='color:{RED};font-weight:700;'>没有边界 = AI随机应变 = 不可控</span>"),
        ("追问 03", ""场景设计和系统打通了吗?"", f"用户叙事写得好，但和调用逻辑<span style='color:{RED};font-weight:700;'>是两张皮</span>"),
    ]
    blocks = ''
    for label, q, a in qas:
        blocks += f"""<div style="margin-bottom:36px;padding:32px 36px;background:{CREAM};
border-radius:20px;border-left:6px solid {GOLD};">
  <div style="font-size:24px;font-weight:700;color:{GOLD};letter-spacing:3px;margin-bottom:14px;">{label}</div>
  <div style="font-size:34px;font-weight:800;color:{RED};line-height:1.5;margin-bottom:14px;">{q}</div>
  <div style="font-size:30px;color:{GRAY};line-height:1.65;">{a}</div>
</div>"""

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{BASE_CSS}
.card {{ background:#fff; }}
.top {{ height:12px;background:linear-gradient(90deg,{RED},{GOLD},{RED_LT}); }}
.body {{ flex:1;padding:60px 80px;display:flex;flex-direction:column;justify-content:center; }}
.chapter {{ font-size:26px;color:{GOLD};font-weight:700;letter-spacing:3px;margin-bottom:20px; }}
.h2 {{ font-size:54px;font-weight:900;color:{RED};line-height:1.3;margin-bottom:28px; }}
.bar {{ width:64px;height:6px;background:linear-gradient(90deg,{RED},{GOLD});border-radius:3px;margin-bottom:40px; }}
.num {{ position:absolute;bottom:48px;right:72px;font-size:26px;color:#D0C8C2;font-weight:600; }}
</style></head><body><div class="card">
  <div class="top"></div>
  <div class="body">
    <div class="chapter">— 02 —</div>
    <div class="h2">七轮追问 · 前三轮</div>
    <div class="bar"></div>
    {blocks}
  </div>
  <div class="num">2 / 6</div>
</div></body></html>"""

# ── 第3张:追问04-07 ────────────────────────────────────────────────────
def card_qa_2():
    qas = [
        ("追问 04", ""文档路径最优化了吗?"", f"Buffett.md 14k tokens，<br><span style='color:{RED};font-weight:700;'>一半是重复内容</span>，重构后压到 6k"),
        ("追问 05", ""简版人设更新了吗?"", f"深度档案建完没有反哺简版<br><span style='color:{RED};font-weight:700;'>输出质量零提升</span>"),
        ("追问 06", ""七位大师结构统一吗?"", f"有人缺章节，有人格式乱<br><span style='color:{RED};font-weight:700;'>批量任务越到后面越走形</span>"),
        ("追问 07", ""这种问题日后如何避免?"", f"这才是最严重的——<br><span style='color:{RED};font-weight:700;'>buffett.md 被截断，带着损坏文件跑了整个下午</span>"),
    ]
    blocks = ''
    for label, q, a in qas:
        blocks += f"""<div style="margin-bottom:28px;padding:26px 32px;background:{CREAM};
border-radius:18px;border-left:6px solid {GOLD};">
  <div style="font-size:22px;font-weight:700;color:{GOLD};letter-spacing:3px;margin-bottom:10px;">{label}</div>
  <div style="font-size:30px;font-weight:800;color:{RED};line-height:1.45;margin-bottom:10px;">{q}</div>
  <div style="font-size:27px;color:{GRAY};line-height:1.6;">{a}</div>
</div>"""

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{BASE_CSS}
.card {{ background:#fff; }}
.top {{ height:12px;background:linear-gradient(90deg,{RED},{GOLD},{RED_LT}); }}
.body {{ flex:1;padding:60px 80px;display:flex;flex-direction:column;justify-content:center; }}
.chapter {{ font-size:26px;color:{GOLD};font-weight:700;letter-spacing:3px;margin-bottom:20px; }}
.h2 {{ font-size:54px;font-weight:900;color:{RED};line-height:1.3;margin-bottom:28px; }}
.bar {{ width:64px;height:6px;background:linear-gradient(90deg,{RED},{GOLD});border-radius:3px;margin-bottom:36px; }}
.num {{ position:absolute;bottom:48px;right:72px;font-size:26px;color:#D0C8C2;font-weight:600; }}
</style></head><body><div class="card">
  <div class="top"></div>
  <div class="body">
    <div class="chapter">— 03 —</div>
    <div class="h2">七轮追问 · 后四轮</div>
    <div class="bar"></div>
    {blocks}
  </div>
  <div class="num">3 / 6</div>
</div></body></html>"""

# ── 第4张:护城河 ────────────────────────────────────────────────────────
def card_moat():
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{BASE_CSS}
.card {{ background:#fff; }}
.top {{ height:12px;background:linear-gradient(90deg,{RED},{GOLD},{RED_LT}); }}
.body {{ flex:1;padding:72px 88px;display:flex;flex-direction:column;justify-content:center; }}
.chapter {{ font-size:26px;color:{GOLD};font-weight:700;letter-spacing:3px;margin-bottom:24px; }}
.h2 {{ font-size:56px;font-weight:900;color:{RED};line-height:1.3;margin-bottom:32px; }}
.bar {{ width:64px;height:6px;background:linear-gradient(90deg,{RED},{GOLD});border-radius:3px;margin-bottom:44px; }}
.quote {{ padding:36px 40px;border-left:6px solid {GOLD};background:{CREAM};
          border-radius:0 20px 20px 0;margin-bottom:40px; }}
.q-text {{ font-size:38px;line-height:1.75;color:#5a3020;font-style:italic;margin:0; }}
.em {{ color:{RED};font-weight:800;font-style:normal; }}
.p {{ font-size:36px;line-height:1.85;margin-bottom:36px; }}
.highlight {{ padding:36px 40px;background:linear-gradient(135deg,#FDF0E8,#F5E0CC);
              border-radius:20px; }}
.hl-title {{ font-size:30px;font-weight:800;color:{RED};margin-bottom:20px; }}
.hl-item {{ font-size:30px;line-height:1.85;color:{TEXT};margin-bottom:8px; }}
.num {{ position:absolute;bottom:48px;right:72px;font-size:26px;color:#D0C8C2;font-weight:600; }}
</style></head><body><div class="card">
  <div class="top"></div>
  <div class="body">
    <div class="chapter">— 04 —</div>
    <div class="h2">追问，是用户<br>自己的护城河</div>
    <div class="bar"></div>
    <div class="quote">
      <p class="q-text">"声称完成"和"真正可用"之间，有一道沟。<br>这道沟<span class="em">只能被人主动发现和填上</span>。</p>
    </div>
    <div class="highlight">
      <div class="hl-title">真正的升级，需要同时满足:</div>
      <div class="hl-item">① 文件存在 &nbsp;② 内容完整</div>
      <div class="hl-item">③ 规则更新 &nbsp;④ 系统能调到</div>
      <div class="hl-item">⑤ 实际输出质量提升</div>
    </div>
  </div>
  <div class="num">4 / 6</div>
</div></body></html>"""

# ── 第5张:结论 ──────────────────────────────────────────────────────────
def card_conclusion():
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{BASE_CSS}
.card {{ background:#fff; }}
.top {{ height:12px;background:linear-gradient(90deg,{RED},{GOLD},{RED_LT}); }}
.body {{ flex:1;padding:72px 88px;display:flex;flex-direction:column;justify-content:center; }}
.chapter {{ font-size:26px;color:{GOLD};font-weight:700;letter-spacing:3px;margin-bottom:24px; }}
.h2 {{ font-size:56px;font-weight:900;color:{RED};line-height:1.3;margin-bottom:32px; }}
.bar {{ width:64px;height:6px;background:linear-gradient(90deg,{RED},{GOLD});border-radius:3px;margin-bottom:44px; }}
.p {{ font-size:38px;line-height:1.9;margin-bottom:32px;color:{TEXT}; }}
.em {{ color:{RED};font-weight:800; }}
.meta-q {{ padding:32px 40px;border-left:6px solid {GOLD};background:{CREAM};
           border-radius:0 16px 16px 0;margin-bottom:36px; }}
.meta-q p {{ font-size:40px;font-style:italic;color:#5a3020;margin:0;line-height:1.7; }}
.final {{ padding:36px 40px;background:{RED};border-radius:20px; }}
.final p {{ font-size:36px;font-weight:700;color:#fff;line-height:1.7;margin:0; }}
.num {{ position:absolute;bottom:48px;right:72px;font-size:26px;color:#D0C8C2;font-weight:600; }}
</style></head><body><div class="card">
  <div class="top"></div>
  <div class="body">
    <div class="chapter">— 05 —</div>
    <div class="h2">最后那个问题<br>才是真正的问题</div>
    <div class="bar"></div>
    <div class="meta-q"><p>"这种问题，我们日后如何避免?"</p></div>
    <p class="p">单次出漏洞可以接受。<br>但不复盘、不建立机制，<br>下次还会出——只是<span class="em">换个地方出现</span>。</p>
    <div class="final">
      <p>AI不会主动告诉你它做错了。<br>它只会告诉你它<span style="color:{GOLD};">完成了</span>。</p>
    </div>
  </div>
  <div class="num">5 / 6</div>
</div></body></html>"""

# ── 结尾卡片 ─────────────────────────────────────────────────────────────
def card_ending():
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{BASE_CSS}
.bg {{ position:absolute;inset:0;
       background:linear-gradient(160deg,#2E0E08 0%,{RED} 50%,#7A2E1C 100%); }}
.content {{ position:relative;z-index:1;height:100%;
            display:flex;flex-direction:column;align-items:center;
            justify-content:center;padding:80px 88px;text-align:center; }}
.icon {{ font-size:120px;margin-bottom:48px; }}
.title {{ font-size:64px;font-weight:900;color:#fff;line-height:1.35;margin-bottom:40px; }}
.accent {{ color:{GOLD}; }}
.divider {{ width:80px;height:5px;background:{GOLD};border-radius:3px;margin:0 auto 48px; }}
.desc {{ font-size:36px;color:rgba(255,255,255,0.75);line-height:1.85;margin-bottom:64px; }}
.cta {{ padding:36px 64px;background:rgba(255,255,255,0.12);
        border-radius:24px;border:2px solid rgba(197,150,58,0.5); }}
.cta-main {{ font-size:34px;font-weight:800;color:{GOLD};margin-bottom:12px; }}
.cta-sub {{ font-size:28px;color:rgba(255,255,255,0.6); }}
</style></head><body><div class="card">
  <div class="bg"></div>
  <div class="content">
    <div class="icon">🤔</div>
    <div class="title">下次AI说<span class="accent">"完成了"</span><br>先别急着相信</div>
    <div class="divider"></div>
    <div class="desc">追问是用户自己的护城河<br>找到沟，才能填上沟</div>
    <div class="cta">
      <div class="cta-main">觉得有用?点赞 + 收藏 🌟</div>
      <div class="cta-sub">更多AI踩坑记录 → 关注我</div>
    </div>
  </div>
</div></body></html>"""

# ── 生成 ─────────────────────────────────────────────────────────────────
cards = [
    ('00-cover',    cover_card()),
    ('01-opening',  card_opening()),
    ('02-qa-1-3',   card_qa_1()),
    ('03-qa-4-7',   card_qa_2()),
    ('04-moat',     card_moat()),
    ('05-conclusion', card_conclusion()),
    ('06-ending',   card_ending()),
]

for fname, html in cards:
    p = OUT_DIR / f'{fname}.html'
    p.write_text(html, encoding='utf-8')
    print(f'✅ {p.name}')

print(f'\n共 {len(cards)} 张，输出到:{OUT_DIR}')
