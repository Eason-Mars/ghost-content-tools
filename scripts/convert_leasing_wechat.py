#!/usr/bin/env python3
"""
专用转换脚本：japan-restaurant-leasing-trust.html → 微信公众号格式
处理 wall-card / method-list / quote-block / highlight-box 等自定义组件
"""

from pathlib import Path

BRAND_RED  = '#8B3A2A'
BRAND_GOLD = '#C5963A'
BRAND_BG   = '#FAF5F3'
FF = '-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",Georgia,serif'
BASE = f'font-family:{FF};font-size:15px;line-height:2.0;color:rgba(0,0,0,0.9);letter-spacing:0.544px;'

def S(extra=''):
    return BASE + extra

HERO_TITLE   = f'font-size:22px;font-weight:800;line-height:1.4;color:{BRAND_RED};margin:0 auto;text-align:center;'
META         = f'font-size:13px;color:#666;text-align:right;margin:0 16px 24px;line-height:1.8;letter-spacing:0.5px;'
PAGE         = f'{BASE}padding:0 16px 48px;'
LEAD         = f'font-size:15px;color:rgb(85,85,85);margin:0 0 24px;padding-bottom:24px;border-bottom:1px solid rgb(233,233,231);line-height:2.0;letter-spacing:0.544px;text-align:justify;'
P            = f'margin:0 0 24px;font-size:15px;line-height:2.0;letter-spacing:0.544px;text-align:justify;'
H2           = f'font-size:18px;color:rgba(0,0,0,0.9);margin:36px 0 16px;padding-left:14px;border-left:4px solid {BRAND_RED};font-weight:800;line-height:1.75;'
STRONG       = f'color:#1a1a1a;font-weight:700;'
BQ           = f'margin:0 0 24px;padding:16px 20px;border-left:4px solid {BRAND_GOLD};background:#fff8f0;font-size:15px;line-height:2.0;letter-spacing:0.544px;font-style:italic;color:#444;'
HIGHLIGHT    = f'margin:0 0 24px;padding:16px 20px;background:#F0E4D8;border-radius:4px;font-size:15px;line-height:2.0;letter-spacing:0.544px;color:#5a2a1a;'
WALL_WRAP    = f'margin:0 0 16px;padding:18px 20px;background:#fff;border-left:4px solid {BRAND_GOLD};border:1px solid #e0dbd8;border-radius:4px;'
WALL_NUM     = f'font-size:11px;font-weight:700;letter-spacing:1.5px;color:{BRAND_GOLD};margin-bottom:4px;'
WALL_TITLE   = f'font-size:16px;font-weight:700;color:{BRAND_RED};margin-bottom:4px;'
WALL_RULE    = f'font-size:13px;color:#888;margin-bottom:6px;line-height:1.7;'
WALL_FEAR_LB = f'font-size:11px;font-weight:700;color:{BRAND_RED};letter-spacing:1px;margin-bottom:4px;display:block;'
WALL_FEAR    = f'font-size:14px;color:#333;line-height:1.85;margin:0;'
METHOD_WRAP  = f'margin:0 0 24px;'
METHOD_ITEM  = f'margin-bottom:10px;padding:14px 16px;background:#fff;border:1px solid #e0dbd8;border-radius:4px;font-size:15px;line-height:2.0;letter-spacing:0.544px;'
METHOD_TITLE = f'font-size:15px;font-weight:700;color:{BRAND_RED};display:block;margin-bottom:4px;'
METHOD_DESC  = f'font-size:14px;color:#555;line-height:1.85;'
CLOSING_WRAP = f'background:{BRAND_RED};color:#fff;padding:24px;margin-top:40px;border-radius:4px;'
CLOSING_NAME = f'font-size:19px;font-weight:800;margin-bottom:6px;'
CLOSING_CRED = f'font-size:12px;opacity:0.70;line-height:1.8;margin-bottom:6px;letter-spacing:0.5px;'
CLOSING_TAG  = f'font-size:13px;opacity:0.85;line-height:1.7;'
XBOX_WRAP    = f'background:#f5f3f0;border:1px solid #e0dbd8;border-radius:4px;padding:16px 20px;margin-top:20px;'
XBOX_LB      = f'font-size:11px;letter-spacing:2px;color:{BRAND_RED};font-weight:700;margin-bottom:8px;'
XBOX_P       = f'font-size:15px;color:#1a1a1a;margin:0;line-height:2.0;'


def wechat_html():
    parts = []

    # ── 外层包裹 ──────────────────────────────────────────────────────
    parts.append(f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:20px;background:#fff;">
<section style="{BASE}">''')

    # ── Hero ──────────────────────────────────────────────────────────
    parts.append(f'''<section style="text-align:center;padding:32px 16px 24px;border-bottom:2px solid {BRAND_RED};margin-bottom:24px;">
<p style="{HERO_TITLE}">在东京租到一家店，需要的不是钱，是信任</p>
</section>''')

    # ── Meta ─────────────────────────────────────────────────────────
    parts.append(f'<section style="{META}"><span style="font-weight:700;color:#666;">文｜</span>Eason</section>')

    # ── 正文区 ────────────────────────────────────────────────────────
    parts.append(f'<section style="{PAGE}">')

    # Lead
    parts.append(f'''<section style="{LEAD}">这段时间我接触了不少中国出海品牌，很多都在认真考虑进东京市场。他们准备得很充分——产品、团队、资金，想得都很清楚。但几乎所有人都没想到，第一个真正的障碍，是<strong style="{STRONG}">租不到店</strong>。<br><br>不是找不到合适的位置，是根本过不了房东那一关。<br><br>我在东京有过同样的经历，也见过身边很多人走同样的弯路。所以想把这件事整理清楚：在东京，为什么租店铺这么难？难在哪里？以及，怎么真正解决它。<br><br>说明一下：这篇聊的是东京。东京在这件事上比较特殊——其他城市相对好一些，但东京的竞争密度和房东筛选标准，是另一个量级。</section>''')

    # H2-1
    parts.append(f'<section style="{H2}">你面对的不是一堵墙，是五堵</section>')
    parts.append(f'<section style="{P}">任何想在东京租商业店铺的新品牌或新公司，无论你来自哪里，都会碰到同样的五道门槛。这不是针对外国人，也不是针对某类行业。这是东京商业租赁市场的底层逻辑。</section>')
    parts.append(f'<section style="{P}">我把它们整理成五道墙。每道墙背后，都有一个更真实的问题。</section>')

    # Five Walls
    walls = [
        ("Wall 01", "信用审查", "与信審査",
         "表面规则：提交过去三年的决算书，证明公司财务稳健。",
         "房东怕你撑不下去然后突然消失。留下的烂摊子——空铺找下一个租客要几个月的空窗期，还要应付原状回復（退租时恢复原貌的义务）纠纷。三年决算书，是他们在问：你有没有足够长的存续证明？"),
        ("Wall 02", "连带保证人", "連帯保証人",
         "表面规则：需要一位日本居民作为连带担保人。",
         "出了问题要追责。外国人可以直接离境，追不回来。担保人是一个「逃不掉」的本地锚点——有人在日本土地上承担后果，房东才有安全感。这不是对人的不信任，是对退出路径的防御。"),
        ("Wall 03", "业种限制", "業種差別",
         "表面规则：某些物业明确拒绝特定餐饮类型，例如中华料理。",
         "不是歧视菜系。是怕排烟投诉、邻居关系破裂、物业声誉受损。更深一层是：他们不确定你是否懂日本的商业规矩，是否愿意遵守。你的经营类型，只是他们用来评估「风险程度」的一个信号。"),
        ("Wall 04", "繁琐流程", "手続き",
         "表面规则：审批流程复杂，文件要求多，时间跨度长。",
         "这不只是官僚主义。东京的房东在用「你愿不愿意配合流程」来测试你：一个认真的长期经营者，会尊重这套体系；一个想走捷径的人，迟早会在其他地方也走捷径。流程，是他们筛人的方式。"),
        ("Wall 05", "人脉网络", "コネクション",
         "表面规则：好位置的铺子从不公开，靠圈子内部流通。",
         "不是故意排外。是房东只愿意把铺子租给「有人能担保其人品」的租客。人脉圈就是信任圈。没有人介绍你，等于没有人愿意为你背书——在日本，这是一个很重的信号。"),
    ]
    for num, zh, jp, rule, fear in walls:
        parts.append(f'''<section style="{WALL_WRAP}">
<p style="{WALL_NUM}">{num}</p>
<p style="{WALL_TITLE}">{zh}　<span style="font-size:12px;color:#aaa;font-weight:400;">{jp}</span></p>
<p style="{WALL_RULE}">{rule}</p>
<span style="{WALL_FEAR_LB}">墙后面真正的顾虑</span>
<p style="{WALL_FEAR}">{fear}</p>
</section>''')

    # Highlight
    parts.append(f'<section style="{HIGHLIGHT}">这五道墙，不是为了刁难你。它们是东京房东用来回答同一个问题的不同方式：<strong style="{STRONG}">这个人，值得我把铺子托付给他吗？</strong></section>')

    # H2-2
    parts.append(f'<section style="{H2}">问题的本质，不是规则，是不确定性</section>')
    parts.append(f'<section style="{P}">我花了很长时间才想明白这件事。</section>')
    parts.append(f'<section style="{P}">最初我们试图"满足要求"——没有三年决算书，就想办法提供其他材料；没有连带保证人，就问有没有替代方案。但这个思路是错的。</section>')
    parts.append(f'<section style="{P}">房东提出这些要求，背后驱动的是一种情绪：<strong style="{STRONG}">不确定性带来的恐惧</strong>。他们不知道你是谁，不知道你能不能做下去，不知道出了问题找谁。这种恐惧，用文件是解决不了的，用钱更是解决不了的。</section>')
    # Quote
    parts.append(f'<section style="{BQ}">在东京，你用更高的租金换不来信任。他们拒绝你不是因为钱不够，而是因为这段关系在他们眼里还不够安全。</section>')
    parts.append(f'<section style="{P}">真正的问题是：他们的恐惧，来自信息不对称。他们对你的了解太少，无法判断风险。所以解法不是给钱，是给信息——给确定性的证明。</section>')

    # H2-3
    parts.append(f'<section style="{H2}">不是绕开规则，是正面回应顾虑</section>')
    parts.append(f'<section style="{P}">我们最终成功签下铺子，不是因为找到了什么捷径，而是因为我们搞清楚了每道墙背后真正的顾虑，然后针对那个顾虑，给出正面的回应。</section>')
    parts.append(f'<section style="{P}">好的中介是必要条件——没有熟悉这个圈子的中介，你连跟房东接触的机会都没有。但中介只是传话筒，真正起作用的是你传达的内容。</section>')
    parts.append(f'<section style="{P}">我们做的事情，可以归纳成一个逻辑：<strong style="{STRONG}">每一个行动，都是在回答同一个问题——"你会不会突然跑路？"</strong></section>')

    # Method list
    methods = [
        ("📄", "提交超出要求的材料", "决算书不够？提交母公司背景、业务计划书、团队构成，甚至已有选址的市场调研。让他们看到的，不是一个想租铺子的人，而是一个认真做了准备的长期经营者。"),
        ("🏗️", "展示长期意图的具体信号", "装修投入计划、本地团队构成、与供应商的合作协议、社区活动的参与计划——这些都是在说：我不是来试试的，我打算在这里长期扎根。"),
        ("🤝", "主动接受不对等条款", "愿意支付更高的押金，愿意接受更严格的原状回復条款，愿意签更长的租期——这些对我们「不利」的条款，恰恰是在向房东证明：你不怕被约束，因为你压根没打算逃。"),
        ("🔗", "用中介传达真诚，而不是谈判", "好的中介不是帮你「说服」房东，而是帮你把你的真实意图准确地传递过去。前提是你的意图本身是真的——经不起推敲的材料，通过中介也只会更快露馅。"),
    ]
    parts.append(f'<section style="{METHOD_WRAP}">')
    for icon, title, desc in methods:
        parts.append(f'''<section style="{METHOD_ITEM}">{icon}　<strong style="{METHOD_TITLE}">{title}</strong><span style="{METHOD_DESC}">{desc}</span></section>''')
    parts.append('</section>')

    parts.append(f'<section style="{P}">没有一条捷径，也没有一个时间节点——比如"拿到第一年决算书就好了"。我们当时根本没有那张决算书。真正的转折点，是我们搞明白房东真正在怕什么，然后开始用行动系统性地消除那个恐惧。</section>')

    # H2-4
    parts.append(f'<section style="{H2}">信任是复利，日本租赁是选合伙人</section>')
    parts.append(f'<section style="{P}">第一家店是最难的。不仅是流程上的陌生，更是因为你在这个圈子里毫无信用记录。每一个环节都要从零证明自己。</section>')
    parts.append(f'<section style="{P}">第二家、第三家，会开始感到不一样。之前的房东愿意为你背书了，中介开始主动给你推荐机会，有些铺子不需要重新走完整个审核流程。</section>')
    parts.append(f'<section style="{P}">到第六家的时候，整个体验是完全不同的。不是因为你变富了，而是因为你在这个市场里积累了信用。每一次按时履约，每一次续约，每一次妥善处理和房东之间的小摩擦，都是在往账户里存款。</section>')
    parts.append(f'<section style="{P}">最终，你不只是在这个市场里生存，你成为了这个圈子的一部分。房东开始主动介绍你给他们认识的业主。好位置的铺子，会在公开之前先问你有没有兴趣。</section>')
    parts.append(f'<section style="{HIGHLIGHT}">东京的商业租赁，本质上不是在做一笔交易，而是在选一个合伙人。交易结束就结束了。合伙关系需要时间建立，也需要持续维护——但一旦建立，它会产生复利。</section>')
    parts.append(f'<section style="{P}">如果你正在考虑进东京，我的建议只有一条：</section>')
    parts.append(f'<section style="{P}">花时间理解那堵墙后面的逻辑，比花时间研究报价策略值得得多。</section>')
    parts.append(f'<section style="{P}">钱可以溢价，但信任没有快捷键。</section>')

    # ── Closing 签名 ─────────────────────────────────────────────────
    parts.append(f'''<section style="{CLOSING_WRAP}">
<p style="{CLOSING_NAME}">我叫 Eason</p>
<p style="{CLOSING_CRED}">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</p>
<p style="{CLOSING_TAG}">在东京，投了几家麻辣烫，现在在探索用AI做投资研究和餐饮运营赋能——然后把这些都写出来。</p>
</section>''')

    # X-box 只用于 Ghost/博客版，微信版不包含

    # 关闭
    parts.append('</section>')  # 正文区
    parts.append('</section>')  # 外层 BASE
    parts.append('</body>\n</html>')

    return '\n'.join(parts)


if __name__ == '__main__':
    output = Path('/Users/dljapan/.openclaw/workspace/personal-brand/content/japan-restaurant-leasing-trust.wechat.html')
    html = wechat_html()
    output.write_text(html, encoding='utf-8')
    print(f'✅ Done: {output} ({len(html)} chars)')
