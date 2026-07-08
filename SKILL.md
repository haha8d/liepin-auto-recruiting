---
name: liepin-recruiter
description: "猎聘平台招聘自动化 v2.5 - 支持CDP直连已登录Chrome，无需重复登录。核心：候选人搜索、AI智能评分框架、简历链接生成(resIdEncode)、HTML报告输出、QQ邮箱SMTP发送。本文件不含任何公司/个人敏感信息，敏感配置见 references/company_context.md。适用于任何岗位。触发词：猎聘搜索、猎聘招聘、搜人才、找候选人、猎聘评分、候选人筛选、获取联系方式"
allowed-tools: "Bash, Read, Write, Edit, Agent, WebFetch, WebSearch"
---

# 猎聘招聘自动化 (Liepin Recruiter) v2.5

通过 **CDP 直连用户已登录的 Chrome 浏览器**（基于 Playwright CDP 协议），零登录成本，完成从**搜索→评分→生成链接→发送邮件**的全流程招聘自动化。

> **v2.5 说明（2026-07-08）**：本文件为**通用方法论**，不含任何公司名称、HR 姓名、邮箱、授权码等敏感信息。
> 所有敏感配置与**公司当前在招岗位的专属要求**（评分模板、搜索关键词、话术）均外置于 `references/company_context.md`，执行任务时加载并填充 `{{占位符}}`。

---

## ⚠️ 敏感信息加载约定

执行任何招聘任务前，先读取 `references/company_context.md`，将以下占位符替换为实际值：

| 占位符 | 含义 | 来源 |
|--------|------|------|
| `{{COMPANY_NAME}}` | 公司名称 | company_context §1 |
| `{{HR_NAME}}` | HR 姓名 | company_context §2 |
| `{{HR_EMAIL}}` | HR 邮箱 | company_context §2 |
| `{{SENDER_EMAIL}}` | 发件邮箱 | company_context §3 |
| `{{QQ_AUTH_CODE}}` | QQ 邮箱 SMTP 授权码 | company_context §3 |

**岗位专属定义**（评分维度、搜索关键词、站内话术）一律以 `references/company_context.md` 第 4 节为准；本文件下方的评分/话术框架仅为通用方法论示例。

---

## 🚀 快速开始

### 使用示例（占位符需先替换）

```
在猎聘上搜索{岗位}候选人
帮我从猎聘找{岗位}，{目标城市}地区，{经验要求}
猎聘搜索：{岗位}，要求有{核心要求}
执行完整的猎聘招聘流程：搜索{岗位}（{目标城市}）→ AI评分 → 生成简历链接 → 发送HTML邮件到 {{HR_EMAIL}}
```

---

## 核心流程详解

### Phase 0: CDP 连接（推荐方式）

> 复用用户已登录的 Chrome，无需扫码，无需启动新浏览器。

**前置条件**：
1. 用户 Chrome 已开启远程调试（`--remote-debugging-port=9222`）
2. 用户已在 Chrome 中登录猎聘（`https://lpt.liepin.com`）

**操作步骤**：

```bash
# 1. 检查 Chrome CDP 端口是否可达
curl -s http://localhost:9222/json 2>/dev/null | python3 -c "import sys,json; [print(t['id'], t['url'][:80]) for t in json.load(sys.stdin)]"

# 若 9222 被占用，使用 web-access skill 的 CDP Proxy（端口 3456）
node "<web-access-skill>/scripts/check-deps.mjs"

# 2. 列出所有已打开的 Chrome tab
curl -s http://localhost:3456/targets 2>/dev/null | python3 -c "
import sys,json
data=json.load(sys.stdin)
for t in data:
    print(f'ID: {t[\"id\"]}')
    print(f'  URL: {t[\"url\"][:80]}')
    print(f'  Title: {t[\"title\"][:50]}')
"

# 3. 找到猎聘 tab 的 target ID 后，验证登录状态
curl -s "http://localhost:3456/eval?target=TARGET_ID" -d 'document.title'
```

**CDP 操作 API（通过 Proxy）**：

```bash
# 导航到指定 URL
curl -s -X POST --data-raw 'https://lpt.liepin.com/search' "http://localhost:3456/navigate?target=TARGET_ID"

# 执行 JS（读取 DOM、提取数据）
curl -s -X POST "http://localhost:3456/eval?target=TARGET_ID" -d '
(function() {
    const items = document.querySelectorAll(".search-result-item");
    return items.length;
})()'

# 滚动加载更多
curl -s -X POST "http://localhost:3456/eval?target=TARGET_ID" -d 'window.scrollBy(0, 1000);'
```

---

### Phase 1: 搜索候选人

**步骤**：
1. 打开 `https://lpt.liepin.com`（猎聘 HR 后台）
2. 验证登录状态（确认显示用户名）
3. 点击左侧「搜索人才」
4. 输入岗位关键词（**具体关键词见 `company_context.md` 第 4 节各岗位**）
5. 设置筛选条件
6. 点击「搜索」按钮，等待结果加载

#### 筛选条件设置

| 筛选条件 | 选项 | 说明 |
|----------|------|------|
| **目标城市** | 不限 / 北京 / 上海 / 深圳 / 其他 | 按岗位要求设置 |
| **期望城市** | 通常与目标城市一致 | 避免期望不匹配 |
| **经验** | 在校应届 / 1-3年 / 3-5年 / 5-10年 / 自定义 | 按岗位级别 |
| **教育** | 本科 / 硕士 / 博士 / 大专 | 按岗位要求 |
| **统招要求** | 是 / 否 | 部分岗位不要求统招 |
| **院校要求** | 可指定院校名称 | 如 `清华大学` |
| **年龄 / 当前状态** | 可设置 | 通常选"在职" |

#### 搜索关键词技巧（通用）

- 英文职位名直接输入：`CFO`、`CTO`
- 中文职位名：`财务总监`、`算法工程师`
- 多个关键词空格隔开：`CFO 上市 IPO`
- 行业/技能关键词：`生物制药`、`细胞培养`、`Python`
- **具体岗位的关键词与组合以 `company_context.md` 第 4 节为准**

---

### Phase 2: AI 智能评分与排序

**评分模型设计原则**：根据岗位 JD 定义**评分维度和权重**，总分 100 分。

> **岗位专属评分模板**：见 `references/company_context.md` 第 4 节（各岗位有专属权重与关键词）。
> **通用角色评分框架**：见 `references/scoring_templates.md`（CFO/CTO/算法/产品/投融资/HRD 等通用模板）。

#### 通用快速评分模板（未指定详细标准时的默认）

| 维度 | 默认权重 | 说明 |
|------|----------|------|
| 岗位核心技能 | **40** | 与 JD 最相关的核心能力 |
| 经验匹配度 | **25** | 工作年限 + 行业经验 |
| 教育背景 | **15** | 学历 + 学校 + 专业相关性 |
| 综合素质 | **10** | 稳定性 + 软实力 + 成长性 |
| 地区 / 薪资匹配 | **10** | 期望城市和薪资是否合理 |

#### 通用评分流程

1. 读取候选人信息（姓名、年龄、经验、公司、职位、学历、学校、专业、标签、活跃状态）
2. 对照评分标准逐项打分
3. 计算加权总分
4. 按**分数降序**排列
5. 输出 TOP N 结构化表格
6. 附**评分理由**

---

### Phase 3: 获取简历链接（⭐ 核心能力）

> 使用 `resIdEncode` 参数生成简历详情页链接（不再使用转发链接）。

```text
https://lpt.liepin.com/resume/detail?resIdEncode=<id>
```

**关键经验**：
- ✅ 必须使用 `resIdEncode`（不是 `resumeId`）
- ✅ 从搜索结果页候选人卡片链接中提取 `resIdEncode` 值
- ✅ 该链接需登录猎聘 HR 后台才能查看完整简历

**提取方法**：

```javascript
// 在搜索结果页执行
document.querySelectorAll('a[href*="resIdEncode"]').forEach(a => console.log(a.href));
```

#### 生成 HTML 报告（⭐ 核心能力）

HTML 格式报告，含表格和"查看简历"按钮。模板（注意 `{{COMPANY_NAME}}` 需替换）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>候选人简历链接 - {岗位名称}</title>
<style>
  body { font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif; margin:0; padding: 20px; background: #f5f6fa; color: #333; }
  h1 { color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 10px; }
  h2 { color: #34a853; margin-top: 30px; padding: 10px; background: #e8f5e9; border-radius: 6px; }
  table { width: 100%; border-collapse: collapse; margin: 15px 0 30px 0; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
  th { background: #1a73e8; color: white; padding: 12px 10px; text-align: left; font-size: 14px; }
  td { padding: 10px; border-bottom: 1px solid #eee; font-size: 13px; }
  tr:hover { background: #f0f7ff; }
  .link-btn { display: inline-block; padding: 4px 12px; background: #1a73e8; color: white; text-decoration: none; border-radius: 4px; font-size: 12px; }
  .link-btn:hover { background: #1557b0; }
  .salary { color: #e37400; font-weight: bold; }
  .footer { margin-top: 40px; padding: 15px; background: #e8f5e9; border-radius: 8px; color: #333; font-size: 13px; }
</style>
</head>
<body>
<h1>📋 候选人简历链接</h1>
<p>生成时间：{生成日期} | 共 <strong>{人数}</strong> 人</p>
<p>💡 点击"查看简历"按钮可直接打开猎聘简历详情页（需登录猎聘HR后台）</p>
<h2>一、{岗位名称}候选人 - 共{N}人</h2>
<table>
  <tr><th>序号</th><th>姓名</th><th>年龄</th><th>经验</th><th>期望城市</th><th>期望薪资</th><th>操作</th></tr>
  <tr><td>1</td><td>{姓名}</td><td>{年龄}</td><td>{经验}</td><td>{期望城市}</td><td class="salary">{期望薪资}</td><td><a class="link-btn" href="https://lpt.liepin.com/resume/detail?resIdEncode={resIdEncode}" target="_blank">查看简历</a></td></tr>
</table>
<div class="footer">
  <p>📧 <strong>招聘助手 - {{COMPANY_NAME}}</strong></p>
  <p>生成时间：{生成日期}</p>
</div>
</body>
</html>
```

---

### Phase 4: 发送邮件

> 使用 QQ 邮箱 SMTP 发送 HTML 报告。**凭据见 `company_context.md` §3，勿硬编码。**

```bash
cat <HTML文件> | \
  QQ_EMAIL_ACCOUNT={{SENDER_EMAIL}} \
  QQ_EMAIL_AUTH_CODE={{QQ_AUTH_CODE}} \
  node <qq-email-skill>/scripts/send.js "{{HR_EMAIL}}" "主题" --stdin --html
```

**备选：QQ 邮箱 MCP**（需两步确认，确认令牌 5 分钟过期）：
1. 第一次调用 `mcp__qq-mail__SendMessage` → 返回 `confirmation_token`
2. 展示邮件信息给用户确认
3. 用户确认后再次调用并传入 `confirmation_token`

---

### Phase 5: 站内消息触达

**步骤**：搜索结果中找到目标候选人 → 点击「立即沟通」→ 在聊天界面发送话术。

> **岗位专属话术**：见 `references/company_context.md` 第 4 节各岗位。
> **通用话术框架**：见 `references/message_templates.md`（含 {占位符}）。

**通用规则**：
- 语气专业简洁友好，100-200 字以内
- 必须包含：公司名称 + 岗位 + 一句话亮点 + 行动召唤
- 速度控制：每条消息间隔 ≥5 秒，避免平台限制
- 单日建议最多触达 20-30 位候选人

---

### Phase 6: 简历详情查看

1. 搜索结果中勾选候选人复选框 → 点击「浏览简历」；或直接点击卡片进入详情
2. 可获取：姓名（脱敏）、年龄、学历、期望城市/薪资、最近公司/职位、个人优势
3. 联系方式需付费获取（见 Phase 7）

---

### Phase 7: 获取联系方式（付费）

| 项目 | 详情 |
|------|------|
| 单价 | 50 猎币/人（≈¥50） |
| 支付方式 | 猎聘 APP 扫码 |
| 包含 | 手机号、邮箱 |

**免费替代**：站内「立即沟通」/「意向沟通」先触达，有意向后再付费获取电话。

---

### Phase 8: 批量数据导出

导出结构化 CSV：

```csv
排名,姓名,年龄,工作年限,学历,现居地,期望城市,期望职位,期望薪资,
行业,评分,评分理由,最近公司1,最近职位1,最近时间1,
最近公司2,最近职位2,最近时间2,学校1,专业1,标签,匹配关键词,备注
```

---

## candidate_scorer.py 使用说明

评分工具位于 `scripts/candidate_scorer.py`，支持预设通用模板与自定义规则。
**公司专属角色模板不再内置，统一在 `company_context.md` 第 4 节维护。**

### 预设通用模板

| 模板名 | 适用岗位 |
|--------|----------|
| `cfo` | CFO/财务总监 |
| `cto` | CTO/技术总监 |
| `algorithm` | 算法工程师 |
| `pm` | 产品经理 |
| `investment` | 投融资总监 |
| `hrd` | HRD/HRVP |

> 注意：预设模板为通用框架；若 `company_context.md` 第 4 节定义了同岗位的公司专属权重，以公司专属为准。

### 使用示例

```bash
# 使用预设通用模板
python3 scripts/candidate_scorer.py \
  --input candidates.csv --template cfo --target-city 北京 \
  --output scored.csv --top 20

# 按公司专属要求自定义（从 company_context 第4节取关键词）
python3 scripts/candidate_scorer.py \
  --input candidates.csv \
  --custom "维度名(权重):关键词1,关键词2;..." \
  --output scored.csv --top 10
```

### 自定义规则格式

```
"维度名(权重):关键词1,关键词2;维度名(权重):关键词1"
```

---

## 注意事项与风险控制

### 平台安全
- ⛔ 严禁高频操作：每次点击间隔 ≥2 秒
- ⛔ 禁止批量爬取：单次处理不超过 100 条
- ⛔ 频繁验证码时暂停 1 小时

### 数据隐私
- 候选人信息仅用于招聘目的
- 遵守《个人信息保护法》

### 费用提醒
- 获取联系方式前告知用户费用（50 猎币/人）
- 建议先用免费站内沟通筛选意向候选人

### 常见问题排查
| 问题 | 解决方案 |
|------|----------|
| 点击无反应（React 页面） | 必须用 `run-code` + `page.click('CSS选择器')`，不能用 JS 的 el.click() |
| CDP 连接失败 | 确认 Chrome 已开启远程调试 |
| 二维码不显示 | 确认已点击扫码图标 `._40108xY5VS`，截图验证 |

---

## 版本历史

### v2.5 (2026-07-08)
- **敏感信息外置**：公司名称、HR 姓名/邮箱、QQ 授权码、各岗位专属 JD/评分/话术 全部移至 `references/company_context.md`，SKILL.md 仅保留通用方法论与 `{{占位符}}`
- **去重**：移除重复段落
- **脚本瘦身**：`candidate_scorer.py` 移除公司专属 `bioprocess` 模板（移入 company_context）

### v2.4 (2026-07-08)
- 公开版本仅保留通用流程，岗位信息不纳入版本管理

### v2.3 (2026-07-07)
- 简历链接获取（resIdEncode）、HTML 报告、QQ 邮箱 SMTP

### v2.0 (2026-06-01)
- CDP 直连支持；HTML 邮件生成

### v1.0 (2026-05-22)
- 初始版本，基于 CFO 候选人实操验证
