# 猎聘招聘自动化 Skill (Liepin Auto-Recruiting v2.5)

WorkBuddy AI 猎聘平台招聘自动化 Skill —— 通过 CDP 直连用户已登录的 Chrome 浏览器，零登录成本，完成从**搜索→评分→生成链接→发送邮件**的全流程招聘自动化。

> **v2.5 说明（2026-07-08）**：本仓库只包含**通用招聘流程**与**通用角色评分/话术模板库**。所有公司敏感信息（公司名称、HR 姓名/邮箱、邮箱授权码、公司当前在招岗位的专属 JD/评分/话术）均外置为 `references/company_context.md`，该文件**仅本地保存，不纳入本仓库**。SKILL 中使用 `{{COMPANY_NAME}}` 等占位符，执行任务时由使用者从本地 `company_context.md` 加载并填充。

## ✨ 核心能力

| 功能 | 说明 | 费用 |
|------|------|------|
| 🔍 候选人搜索 | 按关键词/城市/薪资/经验/学历/行业等多维条件搜索 | 免费 |
| 🤖 AI智能评分 | 根据自定义权重对候选人打分排序，输出TOP N榜单 | 免费 |
| 📋 简历详情查看 | 浏览完整简历，提取关键信息 | 免费 |
| 📞 联系方式获取 | 获取手机号/邮箱（需50猎币/人≈¥50） | 付费 |
| 💬 站内沟通触达 | 发送「立即沟通」或「意向沟通」消息 | 免费 |
| 📊 批量数据导出 | 导出为结构化CSV文件 | 免费 |
| 🔗 简历链接生成 | 使用 resIdEncode 生成简历详情页链接 | 免费 |
| 📧 HTML报告生成 | 生成格式化HTML报告（含"查看简历"按钮） | 免费 |
| 📧 邮件发送 | 通过QQ邮箱SMTP发送HTML报告 | 免费 |

## 🚀 快速开始

### 安装（WorkBuddy）

**方式一：对话中直接安装（推荐）**

```
帮我安装这个 skill：
https://github.com/haha8d/liepin-auto-recruiting
```

**方式二：下载 zip 手动导入**

1. 下载 `liepin-auto-recruiting-2.5.zip`
2. 打开 WorkBuddy → Skills 管理页面
3. 点击「导入 Skill」→ 选择 zip 文件
4. 导入成功后即可使用

### 本地化配置（敏感信息外置）

```bash
# 复制并填写本地专属配置（此文件请勿提交到仓库）
cp references/company_context.example.md references/company_context.md
# 编辑 company_context.md，填入你的公司名称、HR 邮箱、QQ 授权码、岗位专属定义
```

> 若仓库未附带示例文件，可手动创建 `references/company_context.md`，按 SKILL.md「敏感信息加载约定」一节填写。

### 使用示例

```
在猎聘上搜索CFO候选人
帮我从猎聘找算法工程师，北京地区，3年以上经验
执行完整的猎聘招聘流程：搜索CFO（北京地区）→ AI评分 → 生成简历链接 → 发送HTML邮件
```

## 🔧 工作流

### Phase 0: CDP 连接（推荐）

> **优势**：复用用户已登录的 Chrome，无需扫码，无需启动独立浏览器。

**前置条件：**
1. Chrome 已开启远程调试（`--remote-debugging-port=9222`）
2. 用户已在 Chrome 中登录猎聘（`https://lpt.liepin.com`）

Skill 会自动通过 CDP Proxy（端口 3456）连接已打开的 Chrome Tab，无需任何额外操作。

### Phase 1: 搜索候选人

1. 打开 `https://lpt.liepin.com`（猎聘HR后台）
2. 验证登录状态（确认显示用户名）
3. 点击左侧「搜索人才」
4. 在搜索框输入关键词（如 `CFO`、`算法工程师`）
5. 设置筛选条件（可选）：目标城市、期望城市、经验、教育、行业等
6. 点击「搜索」按钮，等待结果加载

**搜索关键词通用技巧：**
- 英文职位名直接输入：`CFO`、`CTO`
- 中文职位名：`财务总监`、`算法工程师`
- 多个关键词用空格隔开：`CFO 上市 IPO`
- 组合搜索：职位名 + 行业/技能关键词

> 以 CFO 为例：基础搜索 `CFO` → 扩充召回 `财务总监 首席财务官 财务VP` → 精准搜索 `CFO 上市公司 IPO`

### Phase 2: AI智能评分

通用角色评分模板库见 `references/scoring_templates.md`（含 CFO/CTO/算法/产品/投融资/HRD 等通用模板）。**公司专属权重/关键词覆盖**维护在本地 `references/company_context.md`（不在此仓库）。以 CFO 作为示例模板：

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 上市公司CFO经验 | 30 | 有上市公司CFO/财务总监经验得满分 |
| 注册会计师CPA | 15 | 有CPA/ACCA得满分 |
| 四大/顶级事务所 | 15 | 德勤/普华永道/毕马威/安永得满分 |
| 审计背景 | 10 | 有审计总监/经理经验 |
| MBA/EMBA | 8 | 有MBA/EMBA学位 |
| 行业匹配 | 5 | 与目标行业相关 |
| 名校背景 | 5 | 985/QS前100/清北复交 |
| 资深加分 | +2~5 | 15年+加2分，20年+加5分 |

> 其他岗位请参照 `references/scoring_templates.md` 的通用模板，或在本地 `company_context.md` 中定义公司专属权重，或直接用 `--custom` 自定义规则（见下方「评分工具」）。

### Phase 3: 获取简历链接

> 使用 `resIdEncode` 参数生成简历详情页链接（不再使用转发链接）

```
https://lpt.liepin.com/resume/detail?resIdEncode=<id>
```

- ✅ 必须使用 `resIdEncode`（不是 `resumeId`）
- ✅ 从搜索结果页的候选人卡片链接中提取 `resIdEncode` 值
- ✅ 此链接需要登录猎聘HR后台才能查看完整简历

### Phase 4: 生成HTML报告并发送邮件

生成HTML格式报告（含表格和"查看简历"按钮），通过QQ邮箱SMTP发送。凭据来自本地 `company_context.md`，勿硬编码：

```bash
# 凭据从本地 company_context.md 读取后注入环境变量
cat 候选人链接.html | \
  QQ_EMAIL_ACCOUNT="{{SENDER_EMAIL}}" \
  QQ_EMAIL_AUTH_CODE="{{QQ_AUTH_CODE}}" \
  node scripts/send.js "{{HR_EMAIL}}" "候选人简历链接" --stdin --html
```

> 也支持 QQ邮箱 MCP 方式发送（需要两步确认，确认令牌5分钟过期）

### Phase 5: 站内消息触达

自动发送定制化招呼语（按岗位自定义）。通用话术框架见 `references/message_templates.md`，公司专属话术在本地 `company_context.md`。以 CFO 为例：

```
{姓名}老师您好！我是{公司名}的HR。看到您在{最近公司}担任{职位}的丰富经验，
特别是在{具体领域}方面的深厚积累。我们公司目前正在寻找一位有上市/IPO财务管理经验的CFO，不知您是否方便聊聊？
```

> ⚠️ **速度控制**：每次操作间隔≥2秒，单日建议最多触达20-30位候选人，避免被平台检测封禁。

### Phase 6: 简历详情查看

直接点击候选人卡片进入详情页，可获取：姓名（部分脱敏）、年龄、工作年限、学历、学校、专业、现居地、期望城市、期望薪资、最近公司/职位等。

### Phase 7: 获取联系方式

> ⚠️ 猎聘平台对联系方式实行付费保护机制（50猎币/人≈¥50）。

**免费替代方案：**
- **方案A** - 站内沟通：点击「立即沟通」，发送站内消息
- **方案B** - 意向沟通：点击「意向沟通」，系统代发意向邀请

### Phase 8: 批量数据导出

将搜索和评分结果导出为结构化CSV文件，包含：排名、姓名、年龄、工作年限、学历、现居地、期望城市、期望职位、期望薪资、行业、评分、评分理由、最近公司、最近职位等字段。

## 📦 评分工具（candidate_scorer.py）

内置通用化AI评分引擎，预置通用角色模板（`cfo`/`cto`/`algorithm`/`pm`/`investment`/`hrd`），支持任意岗位通过 `--custom` 自定义评分。

### 使用方法

```bash
# 使用 cfo 示例模板评分
python3 scripts/candidate_scorer.py \
  --input candidates.csv \
  --template cfo \
  --output scored.csv

# 使用自定义规则评分
python3 scripts/candidate_scorer.py \
  --input candidates.csv \
  --custom "CFO经验(30):CFO,财务总监,IPO;CPA(15):注册会计师,ACCA" \
  --output scored.csv

# 输出TOP 20
python3 scripts/candidate_scorer.py \
  --input candidates.csv \
  --template cfo \
  --target-city 北京 \
  --top 20 \
  --output top20.csv
```

### 自定义规则格式

```
"维度名(权重):关键词1,关键词2;维度名(权重):关键词1,关键词2"
```

- 分号 `;` 分隔不同维度
- 冒号 `:` 后跟该维度的匹配关键词（逗号分隔）
- 若省略冒号及后面部分，则使用维度名作为关键词

## 🔬 技术说明

### 为什么用 Playwright CDP 而非 agent-browser？

1. **React SPA 兼容**：猎聘等 React 单页应用，`el.click()`/`dispatchEvent` 会被 React 合成事件系统忽略。**必须用 Playwright 的 `page.click()` 走 CDP Input.dispatchMouseEvent 通道**才能成功触发点击。
2. **登录态复用**：通过 CDP 直连用户日常 Chrome 浏览器，天然携带登录态，无需重复登录。
3. **防封禁**：操作间隔 2-5 秒，模拟真人行为。

### CDP 连接方式

Skill 支持两种 CDP 连接方式：

| 方式 | 说明 |
|------|------|
| **CDP Proxy（推荐）** | 通过 `web-access` skill 的 CDP Proxy（端口 3456）连接用户已打开的 Chrome Tab，零登录成本 |
| **playwright-cli** | 启动独立 Chromium 实例，需要扫码登录 |

## 📋 文件结构

```
liepin-auto-recruiting-2.5/
├── SKILL.md                       # Skill 主文档（WorkBuddy 加载，含 {{占位符}}）
├── README.md                      # 本文件
├── scripts/
│   └── candidate_scorer.py      # 候选人AI评分工具（预设通用角色模板 + --custom）
└── references/
    ├── scoring_templates.md      # 通用角色评分权重模板库（CFO/CTO/算法/产品/投融资/HRD）
    └── message_templates.md      # 通用沟通话术模板库
```

> ⚠️ `references/company_context.md`（公司敏感信息：公司名称、HR、授权码、岗位专属定义）只存在于**使用者本地**，请勿提交到本仓库。SKILL.md 中所有 `{{占位符}}` 均从该文件加载填充。

## 📝 版本历史

### v2.5 (2026-07-08)

- **敏感信息外置**：公司名称、HR 姓名/邮箱、QQ 授权码、公司当前在招岗位的专属 JD/评分/话术 全部外置为本地 `references/company_context.md`（**不纳入本仓库**）
- **SKILL.md 改为通用方法论**：仅保留流程与 `{{COMPANY_NAME}}`/`{{HR_NAME}}`/`{{HR_EMAIL}}`/`{{SENDER_EMAIL}}`/`{{QQ_AUTH_CODE}}` 占位符，执行时从本地 company_context 加载
- **模板库重新纳入版本管理**：`references/scoring_templates.md`、`message_templates.md` 保留为**通用角色库**（已去除公司专属暗示）
- **脚本瘦身**：`candidate_scorer.py` 移除公司专属模板，仅保留通用角色模板 + `--custom`

### v2.4 (2026-07-08)

- 调整仓库定位：只提交通用招聘流程（SKILL 本身）；岗位专属模板不纳入版本管理
- CFO 招聘作为示例模板贯穿全文

### v2.0 (2026-06-01)

- **新增 CDP 直连支持**：复用用户已登录 Chrome，无需扫码
- **新增** HTML 邮件生成功能
- **更新** 登录流程说明

### v1.0 (2026-05-22)

- 初始版本
- 基于 CFO 候选人实操验证
- 支持搜索、AI 评分、简历查看、联系方式获取、CSV 导出

## ⚠️ 注意事项与风险控制

### 平台安全

- **严禁高频操作**：每次点击间隔≥2秒
- **禁止批量爬取**：单次处理不超过100条结果
- **注意反爬**：若频繁出现验证码，暂停操作1小时后再试

### 数据隐私

- 候选人信息仅用于招聘目的
- 不得外传候选人联系方式
- 遵守《个人信息保护法》相关规定

### 费用提醒

- 获取联系方式前务必告知用户费用（50猎币/人）
- 建议先用免费站内沟通筛选意向候选人
- 再对有意向的候选人付费获取电话

## 📄 License

MIT License

## 🙏 致谢

- WorkBuddy 团队
- Playwright 团队
- 猎聘平台
