---
name: liepin-recruiter
description: "猎聘平台招聘自动化 v2.0 - 支持CDP直连已登录Chrome，无需重复登录。功能：候选人搜索、AI智能评分、简历筛选、联系方式获取、站内沟通触达、批量导出CSV。适用于任何岗位（CFO/CTO/算法工程师/产品经理/工艺开发工程师等）。触发词：猎聘搜索、猎聘招聘、搜人才、找候选人、猎聘评分、候选人筛选、获取联系方式"
allowed-tools: "Bash, Read, Write, Edit, Agent, WebFetch, WebSearch"
---

# 猎聘招聘自动化 (Liepin Recruiter) v2.0

通过 **CDP 直连用户已登录的 Chrome 浏览器**（基于 Playwright CDP 协议），零登录成本，完成从**搜索→评分→筛选→触达→导出**的全流程招聘自动化。

> **v2.0 核心升级**：支持 CDP 直连模式，复用用户日常 Chrome 浏览器（已登录态），无需扫码、无需启动独立浏览器。

---

## 核心能力总览

| 功能 | 说明 | 费用 |
|------|------|------|
| 🔍 候选人搜索 | 按关键词/城市/薪资/经验/学历/行业等多维条件搜索 | 免费 |
| 🤖 AI智能评分 | 根据自定义权重对候选人打分排序，输出TOP N榜单 | 免费 |
| 📋 简历详情查看 | 浏览完整简历，提取关键信息 | 免费 |
| 📞 联系方式获取 | 获取手机号/邮箱（需50猎币/人≈¥50） | 付费 |
| 💬 站内沟通触达 | 发送「立即沟通」或「意向沟通」消息 | 免费 |
| 📊 批量数据导出 | 导出为结构化CSV文件 | 免费 |

---

## 使用方法

### 基础用法

```
在猎聘上搜索CFO候选人
帮我从猎聘找算法工程师，北京地区，3年以上经验
猎聘搜索：投融资总监，要求有IPO经验
```

### 高级用法（带评分）

```
猎聘搜索CFO候选人并评分，权重：上市经历30分+注册会计师15分+审计背景10分
猎聘搜算法工程师并排名，985院校20+AI实习15+开源项目15+北京地区10
```

### 完整流程

```
执行完整的猎聘招聘流程：搜索CFO→AI评分→导出TOP20→尝试联系→生成报告
```

---

## 工作流详解

### Phase 0: CDP 连接（v2.0 新增，推荐方式）

> **优势**：复用用户已登录的 Chrome，无需扫码，无需启动新浏览器。

**前置条件**：
1. 用户 Chrome 已开启远程调试（`--remote-debugging-port=9222`）
2. 用户已在 Chrome 中登录猎聘（`https://lpt.liepin.com`）

**操作步骤**：

```bash
# 1. 检查 Chrome CDP 端口是否可达
curl -s http://localhost:9222/json 2>/dev/null | python3 -c "import sys,json; [print(t['id'], t['url'][:80]) for t in json.load(sys.stdin)]"

# 若 9222 被占用（如 teamcoherence），使用 web-access skill 的 CDP Proxy（端口 3456）
# 启动 CDP Proxy（自动发现 Chrome CDP 端口并代理）
node "/Users/lxq/.workbuddy/skills/skill_2053083109158420480/scripts/check-deps.mjs"

# 2. 列出所有已打开的 Chrome tab
curl -s http://localhost:3456/targets 2>/dev/null | python3 -c "
import sys,json
data=json.load(sys.stdin)
for t in data:
    print(f'ID: {t[\"id\"]}')
    print(f'  URL: {t[\"url\"][:80]}')
    print(f'  Title: {t[\"title\"][:50]}')
    print()
"

# 3. 找到猎聘 tab 的 target ID（如 9F8288C4ADA95C7097A41B0D2A2102F6）
# 4. 通过 CDP Proxy 执行 JS 验证登录状态
curl -s "http://localhost:3456/eval?target=TARGET_ID" -d 'document.title'

# 5. 截图确认
curl -s "http://localhost:3456/screenshot?target=TARGET_ID&file=/tmp/liepin_status.png"
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
})()
'

# 点击元素（JS click，适用于非 React SPA）
curl -s -X POST "http://localhost:3456/eval?target=TARGET_ID" -d '
document.querySelector("button:text-is(\"搜索\")").click();
"clicked"'

# 滚动加载更多
curl -s -X POST "http://localhost:3456/eval?target=TARGET_ID" -d '
window.scrollBy(0, 1000);
"scrolled"'

# 关闭 tab（可选，建议保留用户原有 tab）
curl -s "http://localhost:3456/close?target=TARGET_ID"
```

### Phase 1: 搜索候选人（备用，使用 playwright-cli）

> 当 CDP 直连不可用时，使用 playwright-cli 启动独立浏览器。

**步骤：**
1. 打开 `https://lpt.liepin.com`（猎聘HR后台）
2. 验证登录状态（确认显示用户名）
3. 点击左侧「搜索人才」
4. 在搜索框输入关键词（如 `CFO`、`算法工程师`、`投融资总监`）
5. 设置筛选条件（可选）：
   - **目标城市**：不限 / 北京 / 上海 / 深圳 / 其他
   - **期望城市**：不限 / 北京 / 上海 / 其他
   - **经验**：在校应届 / 1-3年 / 3-5年 / 5-10年 / 自定义
   - **教育**：本科 / 硕士 / 博士/博士后 / 大专 / 中专/技高 / 高中及以下
   - **统招要求**：是 / 否
   - **院校要求**：可指定院校名称
6. 点击「搜索」按钮
7. 等待结果加载，记录总数

**搜索关键词技巧：**
- 英文职位名直接输入：`CFO`、`CEO`、`CTO`
- 中文职位名：`财务总监`、`算法工程师`
- 多个关键词用空格隔开：`CFO 上市 IPO`
- 行业关键词：`新能源`、`医疗器械`、`生物制药`、`细胞培养`

### Phase 2: AI智能评分与排序

**评分模型设计原则：**
根据岗位JD定义**评分维度和权重**，总分100分。

#### 示例1：CFO岗位评分模板

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 上市公司/CFO经验 | 30分 | 有上市公司CFO/财务总监经验得满分，拟上市公司扣5分，无则0分 |
| 注册会计师(CPA) | 15分 | 有CPA得满分 |
| 四大/顶级事务所 | 15分 | 德勤/普华永道/毕马威/安永经验得满分，其他Top所扣3-5分 |
| 审计背景 | 10分 | 有审计总监/经理经验得分 |
| MBA/EMBA | 8分 | 有MBA/EMBA学位得分 |
| 行业匹配 | 5分 | 与目标行业相关得满分 |
| 名校背景 | 5分 | 985/211/QS前100得满分 |
| 工作年限加分 | +2~5分 | 10年+加2分，20年+加5分 |

#### 示例2：算法工程师评分模板

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 985/顶尖院校 | 20分 | 清北复交等985院校满分 |
| AI/算法实习 | 15分 | 有大厂AI实习/项目经验 |
| 开源项目/GitHub | 15分 | 有高质量开源贡献 |
| 地区匹配 | 10分 | 目标城市优先 |
| 技术栈匹配 | 10分 | Python/PyTorch/TensorFlow等 |
| 论文发表 | 10分 | 有顶会论文 |
| 竞赛获奖 | 10分 | ACM/Kaggle等 |
| 简历新鲜度 | 10分 | 近期活跃加分 |

#### 示例3：生物医药工艺开发工程师评分模板（v2.0 新增）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 细胞培养经验 | 20分 | 大规模细胞培养（贴壁/悬浮/生物反应器）经验 |
| 生物反应器操作 | 20分 | KrosFlo/Repligen/波浪式反应器操作经验，CellCube优先 |
| CMC/工艺开发 | 20分 | CMC工艺开发/放大/技术转移经验 |
| 干细胞/iPSC/CGT | 15分 | 干细胞/iPSC/免疫细胞/基因治疗产品工艺经验 |
| 学历背景 | 10分 | 生物工程/生物技术/药学硕士以上 |
| 地点匹配 | 10分 | 目标城市（如北京）优先 |
| 工作年限加分 | +2~5分 | 5年+生物工艺经验加分 |

**通用评分流程：**
1. 从搜索结果中逐条读取候选人信息（姓名、年龄、经验、公司、职位、学历、学校、专业、标签、活跃状态）
2. 对照评分标准逐项打分
3. 计算加权总分
4. 按**分数降序**排列
5. 输出TOP N候选人的结构化表格
6. 对每位候选人附上**评分理由**

### Phase 3: 简历详情查看

**步骤：**
1. 在搜索结果列表中找到目标候选人
2. **勾选候选人左侧的复选框**
3. 点击底部「浏览简历」按钮
4. 或**直接点击候选人卡片**打开详情页
5. 等待详情页加载（约3-5秒）

**简历详情页可获取的信息：**
- 👤 姓名（部分脱敏为**）
- 📅 年龄 / 工作年限
- 🎓 学历 / 学校 / 专业（是否统招）
- 📍 现居地 / 期望城市
- 💰 期望薪资
- 🏢 最近公司 / 职位 / 在职时间
- ✨ 个人优势描述（专业能力总结）
- 📱 联系方式（付费获取）

**注意：** 如果点击「浏览简历」提示"请先选择需要批量查看的简历"，说明复选框未正确选中。此时应改为**直接点击候选人名字卡片**进入详情。

### Phase 4: 获取联系方式

**⚠️ 关键限制：猎聘平台对联系方式实行付费保护机制。**

| 项目 | 详情 |
|------|------|
| 单价 | **50 猎币/人** (≈ ¥50) |
| 有效期 | 365天 |
| 支付方式 | 猎聘APP扫码支付 |
| 包含内容 | 手机号码、邮箱等 |

**操作步骤：**
1. 在候选人详情页面右侧找到 **「获取电话」** 按钮（蓝色，带电话图标📞）
2. 点击该按钮
3. 弹出付费窗口，显示候选人全名和二维码
4. 用猎聘APP扫码支付后即可获得联系方式

**替代方案（免费）：**
- **方案A - 站内沟通**：点击「立即沟通」（蓝色大按钮），发送站内消息
- **方案B - 意向沟通**：点击「意向沟通」，系统代发意向邀请
- 方案A/B均为免费，可在不获取电话的情况下先触达候选人

### Phase 5: 批量数据导出

将搜索和评分结果导出为结构化CSV文件：

```csv
排名,姓名,年龄,工作年限,学历,现居地,期望城市,期望职位,期望薪资,
行业,评分,评分理由,最近公司1,最近职位1,最近时间1,
最近公司2,最近职位2,最近时间2,学校1,专业1,标签,匹配关键词,备注
```

**字段说明：**
- `排名` - AI评分后的排名
- `评分理由` - 各维度得分明细
- `标签` - 平台自动标注的特征（在线/今天活跃/隐藏等）
- `匹配关键词` - 与JD匹配的关键词
- `备注` - 特殊情况说明（如经验不符、期望过高）

### Phase 6: 站内消息触达

**greet_candidate()函数实现：**

1. 在搜索结果中找到目标候选人
2. 点击候选人卡片右侧的 **「立即沟通」** 按钮
3. 系统跳转到 `/chat/im` 页面（聊天界面）
4. 在输入框中输入预设的招呼语（根据岗位定制）
5. 发送消息

**招呼语模板示例：**

> CFO岗位：
> 「您好，我是呈诺医学的HR。看到您在金风科技担任CFO的丰富经验，我们正在寻找一位有上市公司财务管理经验的CFO，不知是否有兴趣了解一下？」

> 算法工程师岗位：
> 「您好同学，看到您的算法背景很优秀！我们是呈诺医学（细胞治疗赛道），正在招募AI/算法方向的同学，如果您对医疗AI感兴趣，欢迎聊聊~」

> 工艺开发工程师岗位（生物医药）：
> 「您好，看到您在{公司}担任细胞培养/工艺开发相关职位，我们正在寻找有生物反应器（KrosFlo KR2i）和大规模细胞培养经验的工艺开发工程师，地点北京，不知是否有兴趣了解一下？」

**速度控制要求（重要！）：**
- ⚠️ **每次操作间隔≥2秒**，避免被猎聘检测封禁
- ⚠️ 不要短时间内批量发送大量消息
- ⚠️ 单日建议最多触达20-30位候选人

---

## playwright-cli 操作规范

### 核心原则（已验证踩坑）

1. **React SPA点击必须用Playwright原生click**：猎聘是React应用，JS注入的`el.click()`/`dispatchEvent`会被React合成事件系统忽略。**必须用 `playwright-cli run-code` 走CDP Input.dispatchMouseEvent通道**
2. **操作间隔2-5秒**：避免高频请求被平台封禁
3. **截图确认关键步骤**：每次重要操作后screenshot验证结果

### 必要命令序列

```bash
# 1. 打开浏览器并导航到目标页面
playwright-cli open "https://www.liepin.com/"        # 猎聘前台（用于扫码登录）
playwright-cli open "https://lpt.liepin.com"          # 猎聘HR后台（需先登录）

# 2. 等待加载
sleep 3

# 3. 截图查看当前状态
playwright-cli screenshot                              # 截图保存到 .playwright-cli/page-*.png

# 4. 执行JavaScript（获取页面数据、查找元素等）
playwright-cli eval "document.title"                   # 简单表达式
playwright-cli eval "document.querySelector('.selector')?.textContent"  # 查找元素文本

# 5. 点击元素（⚠️ React SPA必须用run-code的page.click()！）
playwright-cli run-code "async (page) => { await page.click('CSS选择器'); }"

# 6. 输入文本
playwright-cli run-code "async (page) => {
  const el = await page.waitForSelector('CSS选择器');
  await el.fill('输入内容');
}"

# 7. 滚动页面
playwright-cli run-code "async (page) => {
  await page.evaluate(() => window.scrollBy(0, 1000));
}"

# 8. 获取页面快照/文本内容
playwright-cli run-code "async (page) => {
  return await page.evaluate(() => document.body.innerText);
}"

# 9. 关闭浏览器（任务结束后调用）
playwright-cli close
```

### 登录流程（APP扫码模式，已验证可用）

```bash
# 1. 打开猎聘首页
playwright-cli open "https://www.liepin.com/"
sleep 3

# 2. 截图确认未登录状态（右上角应显示"登录/注册"）
playwright-cli screenshot

# 3. 定位二维码登录图标并点击（切换到APP扫码模式）
# 二维码图标选择器: DIV._40108xY5VS （位置约1176,72，尺寸56x56）
playwright-cli run-code "async (page) => { await page.click('._40108xY5VS'); }"
sleep 2

# 4. 再次截图确认二维码显示
playwright-cli screenshot
# → 此时显示「APP扫码」弹窗 + 大二维码

# 5. 等待用户扫码（人工介入）
# 用户用猎聘APP → 「我的」页面顶部扫一扫

# 6. 验证登录成功
playwright-cli screenshot
# 右上角应显示用户名（如"刘晓庆"）而非"登录/注册"
```

### Session管理规则
- **一个任务只做一次 open 和一次 close**
- 中间多次导航不需要关闭浏览器（复用同一browser实例）
- **close在任务结束后调用**，避免僵尸Chromium进程
- 如果浏览器意外断开，重新 `open` 即可

### 元素查找技巧
- 先用 `eval` 或 `run-code` + `document.querySelector` 查找元素
- 搜索框：通常有特定class或placeholder属性
- 按钮：通过文本内容匹配 `//button[contains(text(),"搜索")]`
- 候选人卡片：列表容器内的重复结构元素
- **优先用CSS选择器**，XPath作为备选
- 用 `run-code` + `page.waitForSelector('css', {timeout:5000})` 等待元素出现

### 数据采集技巧（滚动加载列表）

```bash
# 滚动加载更多搜索结果（猎聘使用无限滚动）
playwright-cli run-code "async (page) => {
  for (let i = 0; i < 5; i++) {
    await page.evaluate(() => window.scrollBy(0, 1000));
    await new Promise(r => setTimeout(r, 2000));  // 等待加载
  }
  return 'scrolled';
}"

# 提取搜索结果中的候选人数据
playwright-cli run-code "async (page) => {
  return await page.evaluate(() => {
    const items = document.querySelectorAll('.job-card-wrapper'); // 根据实际选择器调整
    return Array.from(items).map(el => ({
      name: el.querySelector('.name')?.textContent?.trim(),
      company: el.querySelector('.company')?.textContent?.trim(),
      title: el.querySelector('.title')?.textContent?.trim(),
      // ... 其他字段
    }));
  });
}"
```

### 常用CSS选择器参考（猎聘前台/后台）

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 搜索框 | `input[placeholder*="搜索"]` 或 `.search-input input` | 主搜索框 |
| 搜索按钮 | `.search-btn` 或 `button:has-text("搜索")` | 搜索按钮 |
| 候选人卡片 | `.job-card-wrapper` | 搜索结果项 |
| 候选人姓名 | `.name` 或 `.candidate-name` | 名字 |
| 立即沟通按钮 | `button:has-text("立即沟通")` | 沟通按钮 |
| APP扫码图标 | `._40108xY5VS` | 专用登录页(/login)二维码切换按钮，位置x≈921,y≈230,32×32,带base64背景图 |
| APP扫码Tab | `text=APP扫码` | 二维码面板中的"APP扫码"选项卡（区别于"微信扫码"、"账号登录"） |
| 登录状态 | `.user-nav .name` 或 header中的用户名 | 判断是否已登录 |

---

## candidate_scorer.py 使用说明（v2.0）

评分工具位于 `scripts/candidate_scorer.py`，支持预设模板和自定义规则。

### 预设模板

| 模板名 | 适用岗位 |
|--------|----------|
| `cfo` | CFO/财务总监/首席财务官 |
| `cto` | CTO/技术总监/首席技术官 |
| `algorithm` | 算法工程师/AI工程师/机器学习 |
| `pm` | 产品经理/高级产品经理 |
| `investment` | 投融资总监/VP/IR总监 |
| `hrd` | HRD/HRVP/人力资源总监 |
| `bioprocess` | 工艺开发工程师（生物医药/细胞培养） |

### 使用示例

```bash
# 使用预设模板评分
python3 scripts/candidate_scorer.py \
  --input 工艺工程师_生物医药_评分结果.csv \
  --template bioproces \
  --target-city 北京 \
  --output 工艺工程师_评分结果.csv \
  --top 20

# 自定义评分规则
python3 scripts/candidate_scorer.py \
  --input candidates.csv \
  --custom "CFO经验(30):CFO,财务总监,IPO;CPA(15):注册会计师,ACCA;四大(15):德勤,普华永道" \
  --output scored.csv \
  --top 10
```

### 自定义规则格式

```
"维度名(权重):关键词1,关键词2;维度名(权重):关键词1,关键词2"
```

- 分号 `;` 分隔不同维度
- 冒号 `:` 后跟该维度的匹配关键词（逗号分隔）
- 若省略冒号及后面部分，则使用维度名作为关键词

---

## 通用化参数模板

### 不同岗位类型的搜索参数参考

| 岗位类型 | 推荐搜索关键词 | 推荐筛选条件 |
|----------|---------------|-------------|
| CFO/财务高管 | `CFO` `财务总监` `首席财务官` | 经验10年+，硕士优先，不限城市 |
| CTO/技术高管 | `CTO` `技术总监` `首席技术官` | 经验10年+，本科以上 |
| 算法工程师 | `算法工程师` `AI算法` `机器学习` | 经验1-5年，硕士优先，目标城市 |
| 产品经理 | `产品经理` `PM` | 经验3年+，不限 |
| 投融资 | `投融资` `投资总监` `VP 投资` | 经验5年+，有融资/IPO经验 |
| HRD | `HRD` `人力资源总监` `HRVP` | 经验8年+ |
| 工艺开发工程师 | `细胞培养` `生物反应器` `工艺开发` `CMC` | 经验3年+，硕士优先，生物医药行业 |

---

## 输出交付物

完成完整流程后，应交付：

| 交付物 | 格式 | 内容 |
|--------|------|------|
| 候选人排行榜 | Markdown表格 | TOP N候选人，含评分和理由 |
| CSV数据文件 | `.csv` | 全部搜索结果的详细数据 |
| 执行摘要 | 文字报告 | 搜索数量、TOP推荐、费用预估、下一步建议 |
| 联系方式（可选） | 文字/表格 | 已获取的手机号/邮箱（需付费） |
| HTML邮件 | `.html` | 格式化邮件，含TOP20表格，可发送给团队 |

---

## 注意事项与风险控制

### 平台安全
- ⛔ **严禁高频操作**：每次点击间隔≥2秒
- ⛔ **禁止批量爬取**：单次处理不超过100条结果
- ⛔ **注意反爬**：若频繁出现验证码，暂停操作1小时后再试

### 数据隐私
- 候选人信息仅用于招聘目的
- 不得外传候选人联系方式
- 遵守《个人信息保护法》相关规定

### 费用提醒
- 获取联系方式前务必告知用户费用（50猎币/人）
- 建议先用免费站内沟通筛选意向候选人
- 再对有意向的候选人付费获取电话

### 常见问题排查
| 问题 | 解决方案 |
|------|----------|
| 页面空白/未加载 | 增加 sleep 时间，检查网络 |
| 搜索无结果 | 确认关键词是否正确，放宽筛选条件 |
| 点击无反应 | 重新获取元素ID（snapshot -i），元素可能已变化 |
| 弹出验证码 | 暂停操作，等待冷却 |
| 浏览器卡死 | `playwright-cli close` 后重新 `open` |
| playwright-cli启动失败 | 检查Node.js：`node -e "console.log('ok')"`；确认playwright已安装 |
| 点击无反应（React页面） | 必须用 `run-code` + `page.click('CSS选择器')`，不能用JS的el.click() |
| 二维码不显示 | 确认已点击扫码图标 `._40108xY5VS`，截图验证 |
| CDP连接失败 | 确认Chrome已开启远程调试；尝试重启Chrome并附加 `--remote-debugging-port=9222` |

---

## 版本历史

### v2.0 (2026-06-01)
- **新增CDP直连支持**：复用用户已登录Chrome，无需扫码（通过web-access skill的CDP Proxy）
- **新增生物医药工艺开发工程师评分模板**（`bioprocess`）
- **修复** `candidate_scorer.py` 中的多个bug：
  - `csv.DictWriter` → `csv.DictWriter`（正确大小写）
  - `main()` 函数缩进问题修复
  - `parse_custom_rules()` 正则修复
  - 新增 `--target-city` 参数支持地区匹配加分
- **新增** HTML邮件生成功能（可直接发送格式化邮件）
- **更新** 登录流程说明（区分APP扫码模式和CDP直连模式）

### v1.0 (2026-05-22)
- 初始版本
- 基于CFO候选人实操验证
- 支持搜索、AI评分、简历查看、联系方式获取、CSV导出
- 通用化为适配任意岗位的完整招聘Skill
