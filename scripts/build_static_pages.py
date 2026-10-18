#!/usr/bin/env python3
"""Build the About / Privacy / Contact pages for ezaiops.com (zh + en) and add
footer links to every existing page.

The blog has no shared stylesheet — each page carries its own <style> block — so
these pages reuse the post template's CSS verbatim to stay visually identical.

Run from the repo root:  python scripts/build_static_pages.py
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BASE = "https://ezaiops.com"
POST = os.path.join(DOCS, "posts", "understanding-agent-traces", "index.html")

STYLE = re.search(r"<style>.*?</style>", io.open(POST, encoding="utf-8").read(), re.S).group(0)
FAVICON = ('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' '
           'viewBox=\'0 0 32 32\'%3E%3Crect width=\'32\' height=\'32\' rx=\'6\' fill=\'%232c3e50\'/%3E'
           '%3Ctext x=\'50%25\' y=\'55%25\' fill=\'white\' font-size=\'14\' font-family=\'Arial,sans-serif\' '
           'text-anchor=\'middle\' dominant-baseline=\'middle\' font-weight=\'700\'%3EEZ%3C/text%3E%3C/svg%3E">')


def header(lang, page):
    """page: about | privacy | contact"""
    if lang == "zh":
        return """  <header class="site-header">
    <div class="site-header-inner">
      <div class="brand">
        <a href="/" class="brand-link">
          <h1>轻松自动化笔记</h1>
          <span class="brand-en">EZ AI Ops Tips</span>
        </a>
      </div>
      <nav class="top-nav">
        <a href="/">首页</a>
        <a href="/#featured">专题</a>
        <a href="/about/">关于</a>
        <a href="https://tools.ezaiops.com/?lang=zh">工具</a>
        <div class="lang-switch">
          <a href="/{p}/" class="active" aria-current="page">中文</a>
          <a href="/en/{p}/" hreflang="en">EN</a>
        </div>
      </nav>
    </div>
  </header>""".format(p=page)
    return """  <header class="site-header">
    <div class="site-header-inner">
      <div class="brand">
        <a href="/en/" class="brand-link">
          <h1>EZ AI Ops Tips</h1>
          <span class="brand-cn">轻松自动化笔记</span>
        </a>
      </div>
      <nav class="top-nav">
        <a href="/en/">Home</a>
        <a href="/en/#featured">Focus</a>
        <a href="/en/about/">About</a>
        <a href="https://tools.ezaiops.com/?lang=en">Tools</a>
        <div class="lang-switch">
          <a href="/{p}/" hreflang="zh-CN">中文</a>
          <a href="/en/{p}/" class="active" aria-current="page">EN</a>
        </div>
      </nav>
    </div>
  </header>""".format(p=page)


def footer(lang):
    if lang == "zh":
        return """  <footer>
    <div class="footer-inner">
      <span>© 2026 EZ AI Ops Tips · 轻松自动化笔记</span>
      <span>DevSecOps · AIOps · LLMOps · IT Automation</span>
      <span><a href="/about/">关于</a> · <a href="/contact/">联系</a> · <a href="/privacy/">隐私</a></span>
      <span><a href="https://tools.ezaiops.com/?lang=zh">免费工具站 →</a></span>
    </div>
  </footer>"""
    return """  <footer>
    <div class="footer-inner">
      <span>© 2026 EZ AI Ops Tips · 轻松自动化笔记</span>
      <span>DevSecOps · AIOps · LLMOps · IT Automation</span>
      <span><a href="/en/about/">About</a> · <a href="/en/contact/">Contact</a> · <a href="/en/privacy/">Privacy</a></span>
      <span><a href="https://tools.ezaiops.com/?lang=en">Free tools →</a></span>
    </div>
  </footer>"""


def build(lang, page, title, desc, kicker, h1, body):
    prefix = "" if lang == "zh" else "/en"
    url = "%s%s/%s/" % (BASE, prefix, page)
    alt_zh = "%s/%s/" % (BASE, page)
    alt_en = "%s/en/%s/" % (BASE, page)
    lang_attr = "zh-CN" if lang == "zh" else "en"
    ld = ('{\n'
          '    "@context": "https://schema.org",\n'
          '    "@type": "WebPage",\n'
          '    "name": %s,\n'
          '    "description": %s,\n'
          '    "inLanguage": "%s",\n'
          '    "dateModified": "2026-10-18",\n'
          '    "isPartOf": { "@type": "WebSite", "name": "EZ AI Ops Tips", "url": "https://ezaiops.com/" }\n'
          '  }') % (json_str(title), json_str(desc), lang_attr)
    return """<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{h1}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="zh-CN" href="{alt_zh}">
  <link rel="alternate" hreflang="en" href="{alt_en}">
  <link rel="alternate" hreflang="x-default" href="{alt_zh}">
  {favicon}
  <script type="application/ld+json">
  {ld}
  </script>
  {style}
</head>
<body>

{header}

  <main class="article-main">
    <article>
      <header class="article-header">
        <span class="series-tag">{kicker}</span>
        <h1>{h1}</h1>
        <div class="article-meta">
          <time datetime="2026-10-18">{date}</time>
        </div>
      </header>

      <div class="article-body">
{body}
      </div>
    </article>
  </main>

{footer}

</body>
</html>
""".format(lang_attr=lang_attr, title=title, desc=desc, h1=h1, url=url,
           alt_zh=alt_zh, alt_en=alt_en, favicon=FAVICON, ld=ld, style=STYLE,
           header=header(lang, page), kicker=kicker,
           date="2026 年 10 月 18 日" if lang == "zh" else "October 18, 2026",
           body=body, footer=footer(lang))


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

PRIVACY_ZH = """
        <p>本站是 ezaiops.com 上的一个静态博客，托管在 GitHub Pages。它没有账号系统、没有评论、没有订阅表单，也没有任何会把你输入的内容发出去的交互。这份政策说明的，主要是托管方日志和广告 Cookie 这两件我们无法完全避免的事。</p>

        <h2>本站会接触到的数据</h2>
        <p>页面由 GitHub Pages 提供。和任何网站托管商一样，GitHub 会记录请求（IP 地址、User-Agent、请求的 URL、时间戳），用于提供服务并防止滥用。我们不会把这些日志作为数据集接收，不会与其他信息合并，也不会用它们识别访客。具体处理方式见 GitHub 的隐私声明。</p>
        <p>除此之外，本站不设置任何用于识别你的 Cookie，也不收集邮箱、姓名或任何表单数据。</p>

        <h2>Cookie 与广告</h2>
        <p>本站目前没有启用广告。未来可能接入 Google AdSense：启用后，Google 及其合作伙伴会使用 Cookie 或网络信标，基于你此前访问本站及其他网站的情况投放广告。</p>
        <p>你可以随时在 Google 广告设置中退出个性化广告，或在 aboutads.info 退出第三方供应商的 Cookie。对欧洲经济区、英国和瑞士的访客，法律要求先取得同意：启用广告后，会在设置任何广告 Cookie 之前显示同意提示，你也可以随时通过提示中的链接更改选择。</p>

        <h2>统计分析</h2>
        <p>目前没有部署任何统计工具。如果未来启用，只会使用聚合的、非识别性指标（页面浏览量、来源、国家/地区级别的位置），并在生效前更新本页。</p>

        <h2>你的权利</h2>
        <p>由于本站不收集你的内容、也没有账号，通常并不存在可供提供或删除的个人数据。如果你认为我们持有关于你的信息——例如你发来的一封邮件或一条 issue——可以要求查看、索取副本或要求删除，通过联系页提出即可。请求会尽力处理，不需要注册。</p>

        <h2>外部链接</h2>
        <p>文章会链接到 GitHub、各家模型厂商文档以及姊妹站 tools.ezaiops.com。离开本站后，你的数据适用目标网站的政策，本页不覆盖它们。</p>

        <h2>儿童隐私</h2>
        <p>本站面向从事 AI 工程与运维的从业者，不面向 13 岁以下儿童，也不会主动收集儿童信息。</p>

        <h2>政策变更</h2>
        <p>实质性变更——启用广告、增加统计、加入任何会把数据传出你设备的特性——都会反映在本页，并更新页面顶部的日期。本站没有邮件列表可通知，因此本页即为记录。</p>

        <h2>联系我们</h2>
        <p>对本政策有疑问，请通过<a href="/contact/">联系页</a>提出。</p>
"""

PRIVACY_EN = """
        <p>This is a static blog hosted on GitHub Pages. There are no accounts, no comments, no newsletter form, and no interaction that sends what you type anywhere. This policy is mostly about the two things we cannot fully avoid: hosting logs and advertising cookies.</p>

        <h2>What the site touches</h2>
        <p>Pages are served by GitHub Pages. Like any web host, GitHub records requests (IP address, user agent, requested URL, timestamp) to deliver the site and protect it from abuse. We do not receive those logs as a dataset, do not combine them with anything else, and do not use them to identify visitors. GitHub's handling is described in the GitHub privacy statement.</p>
        <p>Beyond that, the site sets no cookies to identify you and collects no email addresses, names or form data.</p>

        <h2>Cookies and advertising</h2>
        <p>There is no advertising on the site today. Google AdSense may be added later: once active, Google and its partners may use cookies or web beacons to serve ads based on your prior visits to this and other websites.</p>
        <p>You can opt out of personalized advertising in your Google ads settings, or opt out of third-party vendor cookies at aboutads.info. For visitors in the European Economic Area, the United Kingdom and Switzerland, consent is required by law: once ads are enabled, a consent message appears before any advertising cookie is set, and you can change your choice at any time from the link in that message.</p>

        <h2>Analytics</h2>
        <p>No analytics are deployed today. If they are added, only aggregate, non-identifying metrics (page views, referrers, country-level location) will be collected, and this page will be updated before the change takes effect.</p>

        <h2>Your rights</h2>
        <p>Because the site collects no content from you and has no accounts, there is usually no personal data to hand over or delete. If you believe we hold something about you — an email or an issue you sent — you can ask what it is, ask for a copy, or ask for it to be deleted through the contact page. Requests are answered on a best-effort basis and require no registration.</p>

        <h2>External links</h2>
        <p>Articles link to GitHub, model provider documentation and the sister site tools.ezaiops.com. Once you leave this site, the destination's policy applies; this page does not cover it.</p>

        <h2>Children's privacy</h2>
        <p>The site is written for people working in AI engineering and operations. It is not directed at children under 13, and no information is knowingly collected from them.</p>

        <h2>Changes to this policy</h2>
        <p>Material changes — enabling advertising, adding analytics, adding any feature that sends data off your device — will be reflected here and the date at the top of this page will change. There is no mailing list to notify, so this page is the record.</p>

        <h2>Contact</h2>
        <p>Questions about this policy can be raised through the <a href="/en/contact/">contact page</a>.</p>
"""

ABOUT_ZH = """
        <p>这个站只写一件事：<strong>当 AI Agent 真正跑在生产里，你怎么知道它做对了、花了多少钱、卡在哪里。</strong>不是模型评测，不是提示词技巧，是可观测性、成本与运维——那些把 demo 推上线之后才会遇到的问题。</p>

        <h2>写什么</h2>
        <ul>
          <li><strong>可观测性</strong>：Trace、Metrics、Evaluation 三大支柱怎么落到 Agent 上，为什么传统 APM 看不见"做错了"。</li>
          <li><strong>Trace 的语义</strong>：一条 Agent 行为树到底长什么样，OpenTelemetry GenAI 语义约定怎么读。</li>
          <li><strong>评估</strong>：从规则打分到 LLM-as-a-Judge，怎么给"对不对"一个可复现的分数。</li>
          <li><strong>成本</strong>：token 花在哪、什么情况下会悄悄失控、自托管和 API 的账怎么算。</li>
          <li><strong>选型</strong>：可观测性工具的实际版图，以及端到端落地时的取舍。</li>
        </ul>

        <h2>写给谁</h2>
        <p>写给正在把 Agent 送上生产的人：需要向老板解释这个月账单为什么涨了三倍，需要回答"它昨天为什么答错了"，需要在几个方案之间做选择并承担后果。文章假设你会读日志、看得懂代码，但不假设你已经踩过所有坑。</p>

        <h2>怎么写的</h2>
        <p>尽量一手、可复现：能贴出真实的 trace 结构就不画示意图，能给出具体公式就不写"成本会显著上升"。涉及厂商能力与价格时，以官方文档为准并标注时间——这个领域的数字变化很快，一个半年前的结论可能已经不成立。</p>
        <p>本站不接受付费软文，也不做带赞助的排序。如果将来出现赞助内容，会单独标注。</p>

        <h2>和工具站的关系</h2>
        <p>姊妹站 <a href="https://tools.ezaiops.com/">tools.ezaiops.com</a> 提供一批免费、纯浏览器本地运行的工具：LLM 成本计算、模型价格对比、子网与 Cron 计算、JWT 调试等。很多文章里的账，是用那边的计算器算出来的。</p>

        <h2>谁在维护</h2>
        <p>由 ezaiops 维护。源码与 issue 在 <a href="https://github.com/ezaiops">GitHub</a> 上，纠错与选题建议都欢迎——最快的渠道见<a href="/contact/">联系页</a>。</p>
"""

ABOUT_EN = """
        <p>This site is about one thing: <strong>once an AI agent is running in production, how do you know it did the right thing, what it cost, and where it got stuck.</strong> Not model reviews, not prompt tricks — observability, cost and operations, the problems that only show up after the demo ships.</p>

        <h2>What we write about</h2>
        <ul>
          <li><strong>Observability</strong>: how trace, metrics and evaluation apply to agents, and why traditional APM cannot see "did the wrong thing".</li>
          <li><strong>Trace semantics</strong>: what an agent's behaviour tree actually looks like, and how to read the OpenTelemetry GenAI conventions.</li>
          <li><strong>Evaluation</strong>: from rule-based scoring to LLM-as-a-Judge, and how to give "right vs. wrong" a reproducible score.</li>
          <li><strong>Cost</strong>: where the tokens go, how a bill runs away quietly, and how self-hosting compares with per-token pricing.</li>
          <li><strong>Tooling</strong>: the real landscape of observability products and the trade-offs of wiring them end to end.</li>
        </ul>

        <h2>Who it is for</h2>
        <p>People shipping agents to production: the ones who have to explain why this month's bill tripled, answer "why did it get that wrong yesterday", and pick between options while owning the consequences. The writing assumes you can read logs and code; it does not assume you have already hit every trap.</p>

        <h2>How it is written</h2>
        <p>As first-hand and reproducible as possible: a real trace structure instead of a sketch, a concrete formula instead of "costs rise significantly". Where provider capabilities and prices are involved, the official documentation is the source and the date is noted — numbers in this field move fast, and a six-month-old conclusion may no longer hold.</p>
        <p>No paid placements and no sponsored rankings. If sponsored content ever appears, it will be labelled as such.</p>

        <h2>Relationship to the tools site</h2>
        <p>The sister site <a href="https://tools.ezaiops.com/">tools.ezaiops.com</a> hosts free tools that run entirely in your browser: LLM cost estimation, model price comparison, subnet and cron calculators, a JWT debugger and more. A lot of the arithmetic in these posts was done there.</p>

        <h2>Who maintains it</h2>
        <p>ezaiops. Source and issues live on <a href="https://github.com/ezaiops">GitHub</a>; corrections and topic suggestions are welcome — the fastest route is the <a href="/en/contact/">contact page</a>.</p>
"""

CONTACT_ZH = """
        <p>纠错、选题建议、合作咨询都欢迎。<strong>GitHub 是唯一渠道</strong>：没有支持邮箱，没有工单系统，也没有在线客服——这个站是静态的，没有后端来跑这些。</p>

        <h2>内容纠错</h2>
        <p>这是最有价值的一类反馈，会优先处理。请尽量附上：</p>
        <ul>
          <li>出错的页面与具体段落。</li>
          <li>你认为正确的说法，以及支撑它的来源（官方文档、规范、可复现的 trace 或代码）。</li>
          <li>如果涉及价格或厂商能力，注明你核对的日期——这类信息时效性很强。</li>
        </ul>

        <h2>选题建议</h2>
        <p>说你正在被什么问题卡住，比说"写写 XX 吧"有用得多。如果某个问题在多个团队里反复出现，它通常值得写一篇。</p>

        <h2>广告与合作</h2>
        <p>展示广告通过 Google AdSense 投放，没有可谈的空间。文章里不做带赞助的排序或推荐；如果未来出现赞助内容，会明确标注。</p>

        <h2>隐私相关问题</h2>
        <p>同样通过 GitHub 提出。本站的<a href="/privacy/">隐私政策</a>说明了收集什么、不收集什么。</p>

        <h2>响应时间</h2>
        <p>尽力而为，没有服务承诺。纠错通常几天内处理；选题建议会按"有多少人真正需要"来排。如果文章里的结论已经明显过时，请在标题里写清楚，会往前排。</p>

        <h2>在哪里找我们</h2>
        <p><a href="https://github.com/ezaiops">github.com/ezaiops</a> —— issue、讨论、代码都在这里。</p>
"""

CONTACT_EN = """
        <p>Corrections, topic suggestions and partnership questions are all welcome. <strong>GitHub is the only channel</strong>: there is no support inbox, no ticket system and no chat widget — the site is static and has no backend to run them.</p>

        <h2>Correcting an article</h2>
        <p>This is the most valuable kind of feedback and it gets handled first. Please include:</p>
        <ul>
          <li>The page and the specific passage that is wrong.</li>
          <li>What you believe is correct, and the source that supports it (official docs, a specification, a reproducible trace or snippet).</li>
          <li>If it concerns pricing or provider capabilities, the date you checked — this information ages quickly.</li>
        </ul>

        <h2>Suggesting a topic</h2>
        <p>Describe the problem you are stuck on rather than the article you have in mind. If a problem keeps recurring across teams, it usually deserves a post.</p>

        <h2>Advertising and partnerships</h2>
        <p>Display advertising runs through Google AdSense; there is nothing to negotiate. Articles carry no sponsored rankings or recommendations, and any sponsored content would be clearly labelled.</p>

        <h2>Privacy questions</h2>
        <p>Ask through GitHub as well. The <a href="/en/privacy/">privacy policy</a> covers what is and is not collected.</p>

        <h2>Response time</h2>
        <p>Best effort, no service level. Corrections usually land within a few days; topic suggestions are weighed by how many people actually need them. If a conclusion in an article is clearly out of date, say so in the title and it moves up.</p>

        <h2>Where to find us</h2>
        <p><a href="https://github.com/ezaiops">github.com/ezaiops</a> — issues, discussions and code all live there.</p>
"""

PAGES = [
    ("privacy", "zh", "隐私政策 · EZ AI Ops Tips",
     "ezaiops.com 的隐私政策：本站不收集你的输入，只涉及托管日志与广告 Cookie。",
     "本站", "隐私政策", PRIVACY_ZH),
    ("privacy", "en", "Privacy policy · EZ AI Ops Tips",
     "Privacy policy for ezaiops.com: the site collects no input from you; only hosting logs and, later, advertising cookies.",
     "Site", "Privacy policy", PRIVACY_EN),
    ("about", "zh", "关于本站 · EZ AI Ops Tips",
     "轻松自动化笔记写什么：AI Agent 可观测性、评估、成本与运维的一手实践。写给正在把 Agent 送上生产的人。",
     "关于", "关于本站", ABOUT_ZH),
    ("about", "en", "About · EZ AI Ops Tips",
     "What this site covers: first-hand notes on AI agent observability, evaluation, cost and production operations.",
     "About", "About this site", ABOUT_EN),
    ("contact", "zh", "联系我们 · EZ AI Ops Tips",
     "纠错、选题建议与合作的联系方式：GitHub 是唯一渠道，内容纠错优先处理。",
     "联系", "联系我们", CONTACT_ZH),
    ("contact", "en", "Contact · EZ AI Ops Tips",
     "How to reach ezaiops.com: corrections, topic suggestions and partnerships, via GitHub.",
     "Contact", "Contact", CONTACT_EN),
]


def main():
    for page, lang, title, desc, kicker, h1, body in PAGES:
        folder = os.path.join(DOCS, "" if lang == "zh" else "en", page)
        os.makedirs(folder, exist_ok=True)
        html = build(lang, page, title, desc, kicker, h1, body)
        with io.open(os.path.join(folder, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        print("wrote %s/%s/index.html" % ("docs" if lang == "zh" else "docs/en", page))

    # add footer links to every existing page that lacks them
    patched = 0
    for dirpath, _, filenames in os.walk(DOCS):
        if "index.html" not in filenames:
            continue
        path = os.path.join(dirpath, "index.html")
        rel = os.path.relpath(path, DOCS).replace(os.sep, "/")
        if rel.split("/")[0] in ("about", "contact", "privacy") or rel.split("/")[:2] in (["en", "about"], ["en", "contact"], ["en", "privacy"]):
            continue
        is_en = rel.startswith("en/")
        s = io.open(path, encoding="utf-8").read()
        if 'href="/%sabout/"' % ("en/" if is_en else "") in s:
            continue
        old = ('<span><a href="https://tools.ezaiops.com/?lang=%s">%s</a></span>'
               % ("en" if is_en else "zh", "Free tools →" if is_en else "免费工具站 →"))
        if old not in s:
            print("  footer not matched:", rel)
            continue
        if is_en:
            new = ('<span><a href="/en/about/">About</a> · <a href="/en/contact/">Contact</a> · '
                   '<a href="/en/privacy/">Privacy</a></span>\n      ' + old)
        else:
            new = ('<span><a href="/about/">关于</a> · <a href="/contact/">联系</a> · '
                   '<a href="/privacy/">隐私</a></span>\n      ' + old)
        io.open(path, "w", encoding="utf-8", newline="\n").write(s.replace(old, new, 1))
        patched += 1
    print("footers patched:", patched)


if __name__ == "__main__":
    main()
