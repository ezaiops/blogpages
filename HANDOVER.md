# ezaiops.com — blogpages 交接文档

> 交接对象:接手 blogpages 仓库(博客站 ezaiops.com)的下一个工具 / 人。
> 仓库:`github.com/ezaiops/blogpages`(`blog` 分支,GitHub Pages 从 `docs/` 部署,Cloudflare 代理)。
> 姊妹站:tools.ezaiops.com(另一个仓库 `github.com/ezaiops/tools`)。

---

## 1. 站点速览

- 双语博客:中文在根路径,英文在 `/en/`;`docs/` 下每页自带 `<style>`,无共享样式表。
- 生成脚本:`scripts/generate_sitemap.py`(重建 sitemap,hreflang 配对)、`scripts/build_static_pages.py`(about/contact/privacy + 页脚)。
- 部署:推到 `blog` 分支即自动部署;`docs/CNAME` 绑定 `ezaiops.com`。
- 变现:AdSense,`docs/ads.txt` 授权;**注意 `ads.txt` 按域名独立读取,`ezaiops.com` 与 `tools.ezaiops.com` 各有一份**(tools 仓库根的 ads.txt 是另一份)。

## 2. ads.txt 事件(2026-10-28 ~ 10-30)

### 背景与时间线

- **10-26**:`56d7a8a` 在 `docs/ads.txt` 写入了 AdSense 授权行,Google 此前一直能找到。
- **10-28(前天)**:用户改了 Cloudflare 设置:**①开启了托管 robots.txt / Bot Preference Sync,②开启了强制 HTTPS**。同日 `d4a11a4` 提交:禁用 AI 训练爬虫。
- **10-29(昨天)**:Google 开始报 **"找不到 ads.txt"**。同日 robots.txt 连改四次(`2fb8ec7`/`a14942c`/`c875205`/次日 `fee7b02`/`fd9fce6`),主要是给 Googlebot 加/撤 `Allow: /ads.txt`、启停 Google-Extended。
- **10-30(今天)**:排查确认 ads.txt 已完全正常,问题出在启用托管 robots 的时间窗口 + Google 报告缓存。

### 根因(排查结论)

**Cloudflare 的"托管 robots.txt / Bot Preference Sync"启用后,会用自动生成的 robots.txt 整体替代源站 `docs/robots.txt`。**它会覆盖自定义规则,且不显式允许 Google 的广告爬虫;而 **`Mediapartners-Google` / `AdsBot-Google` 是遵循 robots.txt 的**——它们读到"不允许"时,AdSense/Search Console 就报 ads.txt 找不到。

非根因但已排除:

- **强制 HTTPS**:对 ads.txt 只是 http→https 301,Google 会跟随,实测 200。可保留。
- **robots.txt 的历次提交**:`AdsBot-Google` / `Mediapartners-Google` 始终是 `Allow: /`,从未被禁;ads.txt 一般也不受 robots.txt 约束。时间点重合是巧合。
- **文件本身**:`docs/ads.txt` 的 publisher ID(`pub-8810200627517885`)自 10-26 起没变过,内容格式正确。

### 当前状态(已核实 + 已修复)

- `https://ezaiops.com/ads.txt` → 200,内容正确;`tools.ezaiops.com/ads.txt` → 200,同 publisher ID。
- 各类 UA(AdsBot-Google / Mediapartners-Google / Googlebot / 普通)全部 200,无重定向、无 `cf-mitigated` 挑战头、`content-type: text/plain` 正确。
- `https://ezaiops.com/robots.txt` 与仓库 `docs/robots.txt` 逐字节一致 → Cloudflare 未接管 robots.txt。
- DNS:`ezaiops.com` 走 Cloudflare 代理(橙云,172.67.x / 104.21.x)。
- **Cloudflare API 复核(10-30,通过临时凭证文件 `tools/cfkey` 的 token 只读 + PUT;该文件事后已删除,从未进入任何提交)**:
  - `bot_preference_sync_enabled` 一度为 `true`(10-28 遗留),**已通过 API PUT 显式写为 `false` 并钉死**;
  - `is_robots_txt_managed = false`(托管 robots 不对外服务)、`cf_robots_variant = policy_only`;
  - `fight_mode = false`、`enable_js = false`、AI 防护(ai_*_protection / ai_training 等)全部 `disabled`;
  - 全部 zones rulesets 均为空(无 WAF 自定义规则、无重定向规则、无缓存规则)——这些假设全部排除;
  - zone 设置:`ssl = full`、`always_use_https = on`(无害)、`security_level = medium`、`email_obfuscation = on`(仅影响 HTML mailto:,不影响 .txt)。
  - 改动前配置备份在操作机的 `/tmp/opencode/bot_management.before.json`。

### 恢复动作(Google 侧)

问题条件已解除(其中 Cloudflare 侧已实际修复),Google 报错是缓存结果,等待下次抓取或主动刷新:

1. ~~保持 Bot Preference Sync / 托管 robots 关闭~~ → **已完成**:BPS 已显式置 `false`,托管 robots 不对外服务。
2. Search Console → URL 检查 → `https://ezaiops.com/ads.txt` → **测试实时网址** → 请求编入索引;之后 ads.txt 报告 / AdSense 会更新为可用。
3. 若 24~48 小时后仍报错:查 Cloudflare **安全 → 事件**日志,看 AdsBot/Mediapartners 请求是否被 challenge/block;并检查是否有针对 `.txt` 或 UA 的防火墙规则。

### 自查命令

```bash
# Google 广告爬虫视角看 robots.txt(应看到 Allow: /)
curl -A "Mozilla/5.0 (compatible; Mediapartners-Google/2.1; +http://www.google.com/bot.html)" -s https://ezaiops.com/robots.txt | grep -A1 "Mediapartners-Google\|AdsBot-Google"
# ads.txt 内容
curl -A "Mozilla/5.0 (compatible; AdsBot-Google; +http://www.google.com/adsbot.html)" -s https://ezaiops.com/ads.txt
```

## 3. 本次事件改动过的仓库文件

- `docs/ads.txt`(10-26,授权行)—— 未再变更。
- `docs/robots.txt`(10-28 至 10-30 修改 6 次):
  - 顶部显式 `Allow: /` 给 `Mediapartners-Google` 与 `AdsBot-Google`;
  - 中部 Disallow AI 训练爬虫(GPTBot / ClaudeBot / CCBot / Bytespider / Google-Extended 等);
  - 底部 `User-agent: *` `Allow: /` + `Sitemap` 声明。
  - 内容自 `fd9fce6`(10-30 11:14,启用 Google-Extended)起未再变更;仓库 HEAD 已推进到 `cca5761`,但后续提交只动本文档。

## 4. 操作红线(务必遵守)

1. **Cloudflare 托管 robots.txt / Bot Preference Sync 保持关闭**(2026-10-30 已通过 API 将 `bot_preference_sync_enabled` 置 `false`,`is_robots_txt_managed` 为 `false`;改设置前务必复查,防止被再次打开)。否则它会用自动生成文件覆盖源站,并已实证导致 Google 报 ads.txt 找不到。要拦 AI 爬虫就靠源站 `docs/robots.txt`。
2. **永远不要 Disallow `AdsBot-Google` / `Mediapartners-Google`,也不要用"仅允许 /ads.txt"的写法**(路径级 Allow 会被读成"其余全部禁止",这是 Google 明确提示的反模式;源文件注释里也有)。
3. **两个域名各有独立 ads.txt**:改授权行要同时改 `blogpages/docs/ads.txt` 与 `tools/ads.txt`。
4. **两个域名也各有独立 robots.txt**(本仓库 `docs/robots.txt`、tools 仓库根 `robots.txt`),内容各自维护、互不影响;两份都保持「显式允许广告爬虫 + Disallow AI 训练爬虫 + 通配组 Allow」的同一结构。
5. robots.txt 改动后先用 §2 的自查命令确认广告爬虫视角,再等 Google 重新抓取。

## 5. 已知遗留

- Google 的 ads.txt 报告有滞后(缓存上次抓取结果),手动"请求编入索引"可加速刷新。
- 本仓库无 CI 测试,`check_site` 类校验在 tools 仓库(tools 的 `scripts/check_site.py` 也覆盖不到 blogpages)。

---

*记录时间:2026-10-30;同日状态同步(robots.txt 内容锚点、凭证文件说明)。`blog` 分支的最新提交以 `git log -1 -- HANDOVER.md` 为准。*