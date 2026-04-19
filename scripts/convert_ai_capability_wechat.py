#!/usr/bin/env python3
"""
专用转换脚本：2026-03-19-ai-capability-verification.html → 微信公众号格式
处理 qa-block / insight-box / blockquote 等自定义组件
"""

from pathlib import Path

BRAND_RED  = '#8B3A2A'
BRAND_GOLD = '#C5963A'
FF = '-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",Georgia,serif'
BASE = f'font-family:{FF};font-size:15px;line-height:2.0;color:rgba(0,0,0,0.9);letter-spacing:0.544px;'

P            = f'margin:0 0 20px;font-size:15px;line-height:2.0;letter-spacing:0.544px;text-align:justify;'
H2           = f'font-size:18px;color:rgba(0,0,0,0.9);margin:36px 0 16px;padding-left:14px;border-left:4px solid {BRAND_RED};font-weight:800;line-height:1.75;'
STRONG       = f'color:#1a1a1a;font-weight:700;'
LEAD         = f'font-size:15px;color:rgb(85,85,85);margin:0 0 24px;padding-bottom:24px;border-bottom:1px solid rgb(233,233,231);line-height:2.0;letter-spacing:0.544px;text-align:justify;'
BQ           = f'margin:0 0 20px;padding:16px 20px;border-left:4px solid {BRAND_GOLD};background:#fff8f0;font-size:15px;line-height:2.0;letter-spacing:0.544px;font-style:italic;color:#444;'
QA_WRAP      = f'margin:0 0 20px;padding:18px 20px;background:#fff;border:1px solid #e0dbd8;border-radius:6px;border-left:4px solid {BRAND_RED};'
QA_LABEL     = f'font-size:11px;font-weight:700;letter-spacing:1.5px;color:{BRAND_GOLD};margin-bottom:6px;text-transform:uppercase;'
QA_Q         = f'font-size:15px;font-weight:700;color:{BRAND_RED};margin-bottom:8px;line-height:1.75;'
QA_A         = f'font-size:14px;color:#444;line-height:1.9;margin:0;'
INSIGHT_WRAP = f'margin:0 0 20px;padding:18px 22px;background:#F0E4D8;border-radius:4px;font-size:14px;line-height:1.9;letter-spacing:0.544px;color:#5a2a1a;'
CLOSING_WRAP = f'background:{BRAND_RED};color:#fff;padding:24px;margin-top:40px;border-radius:4px;'
CLOSING_NAME = f'font-size:19px;font-weight:800;margin-bottom:6px;'
CLOSING_CRED = f'font-size:12px;opacity:0.70;line-height:1.8;margin-bottom:6px;letter-spacing:0.5px;'
CLOSING_TAG  = f'font-size:13px;opacity:0.85;line-height:1.7;'


def wechat_html():
    parts = []

    parts.append(f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:20px;background:#fff;">
<section style="{BASE}">''')

    # Hero
    parts.append(f'''<section style="text-align:center;padding:32px 16px 24px;border-bottom:2px solid {BRAND_RED};margin-bottom:24px;">
<p style="font-size:21px;font-weight:800;line-height:1.5;color:{BRAND_RED};margin:0 auto;">AI说"完成了"的那一刻，才是真正的工作开始</p>
</section>''')

    parts.append(f'<section style="font-size:13px;color:#666;text-align:right;margin:0 0 24px;"><span style="font-weight:700;">文｜</span>Eason</section>')

    parts.append(f'<section style="padding:0 0 40px;">')

    # Lead
    parts.append(f'<section style="{LEAD}">今天我们做了一次大升级，把七位投资大师的知识库从浅版 bullet 升级成真正的深度档案。表面上很顺利。但我问了七轮，每一轮都发现一个新漏洞。最后发现的那个，是让整个系统带着一个损坏文件运行了整个下午。</section>')

    # H2-1
    parts.append(f'<section style="{H2}">"完成了"是最危险的三个字</section>')
    parts.append(f'<section style="{P}">我用AI已经有一段时间了，有一个规律我越来越确定：<strong style="{STRONG}">AI最危险的时刻，不是它说"我不会"，而是它说"完成了"。</strong></section>')
    parts.append(f'<section style="{P}">说"我不会"，你会去找别的办法。说"完成了"，你就真的以为完成了。</section>')
    parts.append(f'<section style="{P}">今天就是一个完整的案例。</section>')
    parts.append(f'<section style="{P}">背景是这样的：我在做一个AI投资研究系统，里面有个"七位大师圆桌"功能——Buffett、Lynch、Marks、Soros、Dalio、Druckenmiller、段永平，让他们用各自的投资哲学来分析A股。一直以来这七位大师的"人设"是浅版的，每人5-6条bullet，能用但不深。今天，我让团队把它升级成真正的深度知识库：每位大师2000到15000字的深度档案，有真实案例、原话引用、量化框架、A股适配。</section>')
    parts.append(f'<section style="{P}">文件一个个建好了，汇报一条条来了。<strong style="{STRONG}">听起来很顺利。但我没有停在"顺利"这里。</strong></section>')

    # H2-2
    parts.append(f'<section style="{H2}">七轮追问，七个漏洞</section>')
    parts.append(f'<section style="{P}">我的第一个问题不是"做得怎么样"，是：</section>')

    # QA blocks
    qas = [
        ("追问 01", '"你再检查一下，确保所有的调用都是完整的、合适的，路径是清晰的，不会错过。"',
         '发现：SKILL.md 里的调用规则没有区分 Level 1 / Level 2 / Level 3——"什么情况下读深度档案"根本没有定义。文件建好了，但系统不知道什么时候该去读它。'),
        ("追问 02", '"那我们轻度圆桌和深度讨论这些场景都定义清楚了吗？是用什么场景来触发？"',
         '发现：触发条件模糊。"用户展开某位大师的看法"——这算 Level 2 还是 Level 1？没有规则。'),
        ("追问 03", '"你之前做了那个\'投资人的一天\'这样的故事，那些场景设计和现在的系统规则打通了吗？"',
         '发现：场景叙事和系统规则是两张皮。用户叙事写得很好，但和实际的调用逻辑没有对齐。'),
        ("追问 04", '"这么大的文档，调用的时候是不是方便读取的？需要分拆吗？路径是不是最优化的？"',
         '发现：Buffett.md 有严重重复——5处相同内容被写了两遍，文件 14k tokens，重构后压缩到 6k tokens。'),
        ("追问 05", '"master-roundtable.md 里的简版人设，是不是需要根据现在的详细版重新写一下？"',
         '发现：简版人设还是建档前的浅版。深度档案建完了，但没有反哺回简版。Level 1 圆桌的输出质量其实还是低的。'),
        ("追问 06", '"你再统一检查一下，我需要确保这七位大师所有的规则都是明确的。"',
         '发现：soros.md 没有圆桌风格章节，duanyongping.md 的来源标注格式不一致。'),
        ("追问 07", '"这种问题，我们日后如何避免？如果我不多问一句，这个问题就还是会存在。"',
         '发现：这才是最严重的——buffett.md 实际上被截断了。328行，Apple 章节中途就断掉了。Mars 没有验证文件写入就报告完成，系统带着这个损坏的文件运行了整个下午。'),
    ]

    followups = [
        '这个问题挺典型的。AI做了"文件创建"这件事，但没有往后想一步：创建完之后，这个文件怎么被调用？调用规则在哪里写？答案是：没写。',
        '你以为规则写了，其实只是写了一个方向，没有写边界。什么叫"展开"？什么叫"深入讨论"？这些都是模糊地带，AI在模糊地带的表现就是随机应变——也就是不可控。',
        '这个问题让我有点无语。之前花时间做的场景设计，相当于做了一个产品 Demo，但 Demo 和实际产品之间的那道桥没有搭。等于是给用户看了一个美好的图纸，但工地上按另一套规则在盖楼。',
        '好家伙。做了一个14000 token 的大文件，里面有一半是重复的。每次调用这个文件，系统都在读一堆冗余内容。这不只是效率问题，这是质量问题——重复内容意味着整理时出了纰漏，数据本身就不干净。',
        '这个漏洞最让我深刻。升级做了一半——底层数据丰富了，但入口层没有更新。等于在图书馆里放了一批好书，但书目系统还是十年前的旧版，读者根本不知道新书在哪里。用户问的那个轻度圆桌，用的还是浅版人设，输出质量没有任何提升。',
        '七个人，以为每个人的文件结构是统一的。结果不是。有人缺章节，有人格式乱。这是最常见的"批量任务"陷阱：AI做多个类似任务时，前几个认真，后面就开始走形。',
        '这个最后才发现的漏洞，是整件事里最严重的。\n\n文件名在，显示正常，汇报说完成。但打开一看，Buffett 关于 Apple 的分析在最关键的地方就断掉了。所有用到 Buffett 分析的场景，拿到的都是残缺的数据。用户不知道，系统也不知道。就这么跑了一整个下午。',
    ]

    for i, (label, q, a) in enumerate(qas):
        parts.append(f'''<section style="{QA_WRAP}">
<p style="{QA_LABEL}">{label}</p>
<p style="{QA_Q}">{q}</p>
<p style="{QA_A}">⬇ {a}</p>
</section>''')
        parts.append(f'<section style="{P}">{followups[i]}</section>')

    # H2-3
    parts.append(f'<section style="{H2}">追问，是对AI最负责任的使用方式</section>')
    parts.append(f'<section style="{P}">七轮问下来，我想清楚了一件事：</section>')
    parts.append(f'<section style="{BQ}">AI很擅长把事情做到"声称完成"的状态，但"声称完成"和"真正可用"之间，有一道沟。</section>')
    parts.append(f'<section style="{P}">这道沟不会自动消失。它只能被人主动发现和填上。</section>')
    parts.append(f'<section style="{P}">很多人用AI的方式是：布置任务，等汇报，接受完成。这没问题——前提是任务简单、验收标准明确。但稍微复杂一点的任务，比如升级一个系统、建一套知识库、改一个流程，"汇报说完成"和"系统真的好用"之间，差的是大量你看不见的细节。</section>')
    parts.append(f'<section style="{P}">我今天的七次追问，不是因为我不信任团队，也不是因为我喜欢挑剔。是因为我知道这些漏洞大概率会在哪里出现，而且我知道如果我不问，没有人会主动来告诉我。</section>')
    parts.append(f'<section style="{P}"><strong style="{STRONG}">追问是用户自己的护城河。</strong>不会追问的用户，永远在用一个"声称完成"但实际上漏洞四伏的系统，还以为自己用的很好。</section>')

    # Insight box
    parts.append(f'''<section style="{INSIGHT_WRAP}">
<strong style="display:block;margin-bottom:8px;">真正的沉淀需要五个条件同时满足：</strong>
1. 文件存在（最基础的）<br>
2. 内容完整（没有截断、没有重复、格式统一）<br>
3. 规则更新（系统知道什么时候调用它）<br>
4. 系统能调到（路径清晰、调用链打通）<br>
5. 实际输出质量提升（最终验收标准）<br><br>
缺任何一个，这个"升级"就只是账面上的升级。
</section>''')

    # H2-4
    parts.append(f'<section style="{H2}">最后那个问题，才是真正的问题</section>')
    parts.append(f'<section style="{P}">七轮问完，我问了一个元问题："这种问题，我们日后如何避免？"</section>')
    parts.append(f'<section style="{P}">这才是整件事里最关键的问题。</section>')
    parts.append(f'<section style="{P}">单次升级出漏洞，这可以接受。每个复杂任务都会有意料之外的地方。但如果不复盘、不建立验证机制、不把这次的教训写进流程，下次还会出同样的漏洞——只是换了一个地方出现。</section>')
    parts.append(f'<section style="{P}">这次建立的规则是：<strong style="{STRONG}">任何文件写入任务，完成后必须验证文件大小和末尾内容，不能只看文件名存在。</strong></section>')
    parts.append(f'<section style="{P}">听起来是很小的一条规则。但如果今天没有问那句"日后如何避免"，这条规则不会存在，Buffett.md 的截断问题会在下一次重演，只是用不同的文件名。</section>')
    parts.append(f'<section style="{P}">用AI做事，你需要的不只是一个"会干活"的系统，更是一个"会被检验"的系统。而让系统可以被检验的责任，在用户这里，不在AI那里。</section>')
    parts.append(f'<section style="{P}">AI不会主动告诉你它做错了。它只会告诉你它完成了。</section>')
    parts.append(f'<section style="{P}"><strong style="{STRONG}">所以，下次你的AI助理说"完成了"，那才是真正工作的开始。</strong></section>')

    # Closing
    parts.append(f'''<section style="{CLOSING_WRAP}">
<p style="{CLOSING_NAME}">我叫 Eason</p>
<p style="{CLOSING_CRED}">CFA持证人 · 前战略咨询合伙人 · 创业者 · 投资人</p>
<p style="{CLOSING_TAG}">在日本经营 6 家餐厅，同时用 AI 做投资研究——然后把踩过的坑写出来。</p>
</section>''')

    parts.append('</section></section></body></html>')
    return '\n'.join(parts)


if __name__ == '__main__':
    out = Path('/Users/dljapan/.openclaw/workspace/personal-brand/content/drafts/2026-03-19-ai-memory/article.wechat2.html')
    out.write_text(wechat_html(), encoding='utf-8')
    print(f'✅ 微信版已生成：{out}')
