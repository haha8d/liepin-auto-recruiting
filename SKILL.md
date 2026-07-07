---
name: liepin-recruiter
description: "猎聘平台招聘自动化 v2.3 - 支持CDP直连已登录Chrome，无需重复登录。核心升级：简历链接获取（resIdEncode）、HTML格式输出、QQ邮箱SMTP发送。功能：候选人搜索、AI智能评分、简历链接生成、HTML报告、邮件发送、站内沟通触达、批量导出CSV。适用于任何岗位（CFO/CTO/算法工程师/产品经理/工艺开发工程师等）。触发词：猎聘搜索、猎聘招聘、搜人才、找候选人、猎聘评分、候选人筛选、获取联系方式"
allowed-tools: "Bash, Read, Write, Edit, Agent, WebFetch, WebSearch"
---

# 猎聘招聘自动化 (Liepin Recruiter) v2.3

通过 **CDP 直连用户已登录的 Chrome 浏览器**（基于 Playwright CDP 协议），零登录成本，完成从**搜索→评分→生成链接→发送邮件**的全流程招聘自动化。

> **v2.3 核心升级（2026-07-07）**：
> 1. ✅ **简历链接获取方式升级**：使用 `resIdEncode` 参数（不再使用转发链接）
> 2. ✅ **列表展示方式升级**：HTML格式输出（含表格和"查看简历"按钮）
> 3. ✅ **发邮件方式升级**：QQ邮箱SMTP（已验证授权码有效，不会过期）
> 4. ✅ **完整评分模板库**：7套预设评分模板（CFO、CTO、算法工程师、产品经理、投融资、HRD、工艺开发工程师）
> 5. ✅ **完整沟通话术模板库**：高管岗位、专业岗位、应届生、消息跟进等话术

---

## 🚀 快速开始

### 安装（WorkBuddy）

**方式一：对话中直接安装（推荐）**

在 WorkBuddy 对话中输入：

```
帮我安装这个 skill：
https://github.com/haha8d/liepin-auto-recruiting
```

**方式二：下载 zip 手动导入**

1. 下载 `liepin-auto-recruiting-2.3.zip`
2. 打开 WorkBuddy → Skills 管理页面
3. 点击「导入 Skill」→ 选择 zip 文件
4. 导入成功后即可使用

### 使用示例

**基础搜索：**
```
在猎聘上搜索CFO候选人
帮我从猎聘找算法工程师，北京地区，3年以上经验
猎聘搜索：投融资总监，要求有IPO经验
```

**带评分：**
```
猎聘搜索CFO候选人并评分，权重：上市经历30分+注册会计师15分+审计背景10分
猎聘搜算法工程师并排名，985院校20+AI实习15+开源项目15+北京地区10
```

**完整流程（搜索+评分+生成链接+发送邮件）：**
```
执行完整的猎聘招聘流程：搜索CFO（北京地区）→ AI评分 → 生成简历链接 → 发送HTML邮件到 hr@example.com
```

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
| 🔗 简历链接生成 | 使用 resIdEncode 生成简历详情页链接 | 免费 |
| 📧 HTML报告生成 | 生成格式化HTML报告（含简历链接和"查看简历"按钮） | 免费 |
| 📧 邮件发送 | 通过QQ邮箱SMTP发送HTML报告 | 免费 |

---

## 核心流程详解

### Phase 0: CDP 连接（推荐方式）

> **优势**：复用用户已登录的 Chrome，无需扫码，无需启动新浏览器。

**前置条件**：
1. 用户 Chrome 已开启远程调试（`--remote-debugging-port=9222`）
2. 用户已在 Chrome 中登录猎聘（`https://lpt.liepin.com`）

**操作步骤：**

```bash
# 1. 检查 Chrome CDP 端口是否可达
curl -s http://localhost:9222/json 2>/dev/null | python3 -c "import sys,json; [print(t['id'], t['url'][:80]) for t in json.load(sys.stdin)]"

# 若 9222 被占用，使用 CDP Proxy（端口 3456）
# 启动 CDP Proxy（自动发现 Chrome CDP 端口并代理）
node "<web-access-skill-path>/scripts/check-deps.mjs"

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

# 3. 找到猎聘 tab 的 target ID
# 4. 通过 CDP Proxy 执行 JS 验证登录状态
curl -s "http://localhost:3456/eval?target=TARGET_ID" -d 'document.title'

# 5. 截图确认
curl -s "http://localhost:3456/screenshot?target=TARGET_ID&file=/tmp/liepin_status.png"
```

**CDP 操作 API（通过 Proxy）：**

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
"clicked"
'

# 滚动加载更多
curl -s -X POST "http://localhost:3456/eval?target=TARGET_ID" -d '
window.scrollBy(0, 1000);
"scrolled"
'
```

### Phase 1: 搜索候选人

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

#### 搜索关键词策略

**搜索关键词技巧：**
- **英文职位名**直接输入：`CFO`、`CEO`、`CTO`
- **中文职位名**：`财务总监`、`算法工程师`
- **多个关键词**用空格隔开：`CFO 上市 IPO`
- **行业关键词**：`新能源`、`医疗器械`、`生物制药`、`细胞培养`
- **技能关键词**：`Python`、`PyTorch`、`细胞培养`、`生物反应器`
- **组合搜索示例**：
  - CFO搜索：`CFO 财务总监 上市公司`
  - 算法工程师搜索：`算法工程师 AI 机器学习 PyTorch`
  - 工艺开发工程师搜索：`细胞培养 生物反应器 CMC 工艺开发`

**不同岗位类型的搜索策略：**

| 岗位类型 | 推荐搜索关键词 | 补充说明 |
|----------|---------------|-------------|
| CFO/财务高管 | `CFO` `财务总监` `首席财务官` `财务VP` | 可加上`上市公司` `IPO` `融资`等关键词 |
| CTO/技术高管 | `CTO` `技术总监` `首席技术官` `研发VP` | 可加上技术栈关键词 |
| 算法工程师 | `算法工程师` `AI算法` `机器学习` `深度学习` | 可加上`PyTorch` `TensorFlow` `NLP` `CV`等 |
| 产品经理 | `产品经理` `PM` `产品总监` | 可加上行业关键词 |
| 投融资 | `投融资` `投资总监` `VP 投资` `IR总监` | 可加上`IPO` `融资` `尽职调查`等 |
| HRD | `HRD` `人力资源总监` `HRVP` `OD总监` | 可加上行业关键词 |
| 工艺开发工程师 | `细胞培养` `生物反应器` `工艺开发` `CMC` `上游工艺` | 可加上`KrosFlo` `CellCube` `iPSC` `CAR-T`等 |

**筛选条件设置规则：**

| 筛选条件 | 设置建议 | 说明 |
|----------|----------|------|
| **目标城市** | 根据岗位要求设置 | 不限 / 北京 / 上海 / 深圳 / 其他 |
| **期望城市** | 通常与目标城市一致 | 避免候选人期望城市与工作岗位地点不匹配 |
| **经验** | 根据岗位级别设置 | 在校应届 / 1-3年 / 3-5年 / 5-10年 / 自定义 |
| **教育** | 根据岗位要求设置 | 本科 / 硕士 / 博士/博士后 / 大专 |
| **统招要求** | 根据岗位要求 | 是 / 否（部分岗位不要求统招） |
| **院校要求** | 可指定院校名称 | 如`清华大学` `北京大学` `浙江大学` |
| **年龄** | 根据岗位要求 | 可设置年龄范围 |
| **当前状态** | 通常选择"在职" | 在职 / 离职 / 不限 |

**搜索结果优化技巧：**
1. **关键词不要太窄**：避免漏掉合适候选人（如搜索`CFO`时，也搜索`财务总监`）
2. **关键词不要太宽**：避免结果太多，增加筛选成本
3. **组合使用筛选条件**：城市+经验+学历组合筛选更精准
4. **查看"隐藏简历"**：部分优质候选人设置了"仅对企业可见"
5. **使用"最近活跃"排序**：优先联系近期活跃的候选人

---

### Phase 2: AI智能评分与排序

**评分模型设计原则：**
根据岗位JD定义**评分维度和权重**，总分100分。

#### 完整评分模板库（7套）

##### 模板1：CFO / 财务高管

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 上市公司/CFO经验 | **30** | 有上市公司CFO/财务总监得满分；拟上市公司扣5分；无则0分 |
| 注册会计师(CPA) | **15** | 有CPA/ACCA得满分；中级会计职称扣5分 |
| 四大/顶级事务所 | **15** | 德勤/普华永道/毕马威/安永得满分；国内Top10所扣3-5分 |
| 审计背景 | **10** | 有审计总监/经理/合伙人经验得分 |
| MBA/EMBA | **8** | 中欧/长江等Top MBA满分；普通MBA扣2-3分 |
| 行业匹配 | **5** | 与目标行业相关（如生物制药、新能源） |
| 名校背景 | **5** | 985/QS前100/清北复交 |
| 资深加分 | +2~+5 | 15年+加2分，20年+加5分 |

**适用场景：** 生物制药CFO、新能源CFO、拟上市公司CFO、集团财务总监

##### 模板2：CTO / 技术高管

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 大厂技术管理经验 | **25** | BAT/字节/TMD等技术VP/总监以上 |
| 技术栈匹配 | **20** | 与目标技术栈一致 |
| 团队管理规模 | **15** | 管理50人+团队满分；20-50人扣5分 |
| 开源影响力 | **10** | GitHub高星项目/KVM/docker等知名开源贡献 |
| 名校背景 | **10** | CS名校/PhD优先 |
| 创业/IPO经历 | **10** | 有创业公司CTO或上市技术负责人经验 |
| 架构能力 | **10** | 有大规模系统架构设计经验 |

**适用场景：** 公司CTO、技术VP、研发总监、平台架构师

##### 模板3：算法工程师 (AI/ML)

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 院校背景 | **20** | 清北复交浙科等CS/AI强校满分；其他985扣5分 |
| AI算法实习/项目 | **15** | 有大厂AI实习或高质量论文/项目 |
| 开源/GitHub | **15** | 有高质量开源贡献（GitHub Star>100或核心Contributor） |
| 地区匹配 | **10** | 目标城市优先 |
| 技术栈匹配 | **10** | PyTorch/TensorFlow/JAX + Python/C++ |
| 论文发表 | **10** | CVPR/ICCV/NIPS/ICML/AAAI等顶会一作 |
| 竞赛获奖 | **10** | ACM金牌/Kaggle Gold/数学建模国奖 |
| 简历新鲜度 | **10** | 30天内活跃加分；应届生额外加分 |

**适用场景：** AI算法工程师、机器学习工程师、NLP算法、CV算法

##### 模板4：产品经理

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 产品经验年限 | **20** | 5年+完整0-1产品经验满分 |
| 行业匹配 | **20** | 有目标行业（医疗/SaaS/金融等）产品经验 |
| B端/C端能力 | **15** | 按目标方向匹配 |
| 数据驱动能力 | **15** | 有数据分析/A/B测试/增长经验 |
| 大厂背景 | **10** | 头部互联网公司产品经验 |
| 学历 | **10** | 本科以上；硕士加分 |
| 项目成果 | **10** | 有从0到1成功案例或DAU/营收显著增长 |

**适用场景：** 高级产品经理、产品总监、B端产品经理、C端产品经理

##### 模板5：投融资总监 / VP

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| IPO/上市经验 | **30** | 有完整IPO操盘经验（A股/H股/美股） |
| 融资资源/渠道 | **20** | 有VC/PE/FA机构人脉或成功融资案例 |
| 尽职调查/合规 | **15** | 有DD/合规内控/财务审计经验 |
| 行业认知 | **15** | 对目标行业（生物医药/硬科技等）有深度理解 |
| 资本市场资质 | **10** | 保代资格/CFA/CPA等 |
| 沟通谈判力 | **10** | 有投资人对接/路演/融资谈判经验 |

**适用场景：** 投融资总监、IR总监、董秘、资本运作VP

##### 模板6：HRD / HRVP / HRBP

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| HR管理经验 | **25** | HRD/HRVP级别管理经验 |
| 招聘能力 | **20** | 有大规模招聘/猎头管理/RPO经验 |
| 薪酬绩效 | **15** | 有薪酬体系设计/股权激励设计经验 |
| 组织发展(OD) | **15** | 有OD/组织变革/文化建设项目经验 |
| 行业匹配 | **10** | 目标行业HR经验 |
| 名企背景 | **10** | 头部企业或咨询公司背景 |
| 乙方+甲方 | 加分 | 同时有乙方（猎头/咨询）和甲方经验 |

##### 模板7：工艺开发工程师（生物医药/细胞培养）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 细胞培养经验 | **20** | 大规模细胞培养（贴壁/悬浮/生物反应器）经验 |
| 生物反应器操作 | **20** | KrosFlo/Repligen/波浪式反应器操作经验，CellCube优先 |
| CMC/工艺开发 | **20** | CMC工艺开发/放大/技术转移经验 |
| 干细胞/iPSC/CGT | **15** | 干细胞/iPSC/免疫细胞/基因治疗产品工艺经验 |
| 学历背景 | **10** | 生物工程/生物技术/药学硕士以上 |
| 地点匹配 | **10** | 目标城市（如北京）优先 |
| 工作年限加分 | +2~5 | 5年+生物工艺经验加分 |

**适用场景：** 生物医药工艺开发工程师、细胞培养工程师、CMC工程师

##### 通用快速评分模板（轻量版）

当用户未指定详细评分标准时，使用此默认模板：

| 维度 | 默认权重 | 说明 |
|------|----------|------|
| 岗位核心技能 | **40** | 与JD最相关的核心能力 |
| 经验匹配度 | **25** | 工作年限+行业经验 |
| 教育背景 | **15** | 学历+学校+专业相关性 |
| 综合素质 | **10** | 稳定性+软实力+成长性 |
| 地区/薪资匹配 | **10** | 期望城市和薪资是否合理 |

**通用评分流程：**
1. 从搜索结果中逐条读取候选人信息（姓名、年龄、经验、公司、职位、学历、学校、专业、标签、活跃状态）
2. 对照评分标准逐项打分
3. 计算加权总分
4. 按**分数降序**排列
5. 输出TOP N候选人的结构化表格
6. 对每位候选人附上**评分理由**

---

### Phase 3: 获取简历链接（⭐ v2.3 核心升级）

> **v2.3 升级点**：使用 `resIdEncode` 参数生成简历详情页链接（不再使用转发链接）

#### 方法：使用 resIdEncode 参数（推荐）

猎聘个人主页链接的正确参数格式：
```
https://lpt.liepin.com/resume/detail?resIdEncode=<id>
```

**关键经验**：
- ✅ 必须使用 `resIdEncode`（不是 `resumeId`）
- ✅ 从搜索结果页的候选人卡片链接中提取 `resIdEncode` 值
- ✅ 此链接需要登录猎聘HR后台才能查看完整简历

#### 提取 resIdEncode 的方法

**方法1：从搜索结果页提取**
```javascript
// 在搜索结果页执行
document.querySelectorAll('a[href*="resIdEncode"]').forEach(a => {
  console.log(a.href);
});
```

**方法2：从候选人详情页 URL 获取**
- 打开候选人详情页
- URL 中 `resIdEncode=` 后面的部分即为该候选人的唯一标识

#### 生成 HTML 报告（⭐ v2.3 核心升级）

> **v2.3 升级点**：生成 HTML 格式的报告文件（含表格和"查看简历"按钮）

使用以下格式生成 HTML 文件：

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
  <!-- 更多候选人... -->
</table>

<div class="footer">
  <p>📧 <strong>招聘助手 - {公司名称}</strong></p>
  <p>生成时间：{生成日期} | 使用说明：点击"查看简历"按钮可直接打开猎聘简历详情页，需登录猎聘HR后台查看完整简历。</p>
</div>

</body>
</html>
```

#### 转发链接（已废弃）

~~在个人主页点击"转发"→"转发链接"可生成无需登录即可查看的分享链接（`mr.liepin.com` 开头）~~

**已确认**：直接使用 `resIdEncode` 链接即可，无需生成转发链接。

---

### Phase 4: 发送邮件（⭐ v2.3 核心升级）

> **v2.3 升级点**：使用 QQ 邮箱 SMTP 发送邮件（已验证授权码有效，不会过期）

#### 方式1：QQ 邮箱 SMTP（推荐，已验证有效）

**前置条件**：
1. 开通 QQ 邮箱 IMAP/SMTP 服务，获取授权码
2. 设置环境变量：
```bash
export QQ_EMAIL_ACCOUNT="<your-qq-email>@qq.com"
export QQ_EMAIL_AUTH_CODE="<your-auth-code>"
```

**发送命令**（使用 qq-email skill 的 send.js）：
```bash
cat <HTML文件路径> | \
  QQ_EMAIL_ACCOUNT="<your-qq-email>@qq.com" \
  QQ_EMAIL_AUTH_CODE="<your-auth-code>" \
  node <qq-email-skill-path>/scripts/send.js "<收件人>" "<主题>" --stdin --html
```

**示例**：
```bash
cat ./候选人链接_北京.html | \
  QQ_EMAIL_ACCOUNT="your-email@qq.com" \
  QQ_EMAIL_AUTH_CODE="your-auth-code" \
  node scripts/send.js "hr@example.com" "猎聘候选人简历链接 - CFO和IT岗位（北京地区）" --stdin --html
```

#### 方式2：QQ 邮箱 MCP（需要两步确认）

**优点**：直接调用，无需配置  
**缺点**：需要两步确认，确认令牌5分钟过期

**使用步骤**：
1. 第一次调用 `mcp__qq-mail__SendMessage` → 返回 `confirmation_token`
2. 展示邮件信息给用户确认
3. 用户确认后，再次调用并传入 `confirmation_token`

#### 常用收件人

| 姓名 | 邮箱 | 说明 |
|------|------|------|
| {HR姓名} | {hr}@{company}.com | {公司名称} HR |

---

### Phase 5: 站内消息触达

**greet_candidate()函数实现：**

1. 在搜索结果中找到目标候选人
2. 点击候选人卡片右侧的 **「立即沟通」** 按钮
3. 系统跳转到 `/chat/im` 页面（聊天界面）
4. 在输入框中输入预设的招呼语（根据岗位定制）
5. 发送消息

#### 沟通话术模板库

##### 通用规则
- 语气：专业但不生硬，简洁友好
- 长度：控制在100-200字以内（猎聘站内消息有字数限制）
- 必须包含：公司名称 + 岗位 + 一句话亮点 + 行动召唤
- 速度控制：每条消息间隔≥5秒，避免被平台限制

##### 高管岗位话术（CFO/CTO/CEO级别）

###### CFO / 财务高管

**模板A（上市公司方向）：**
```
{姓名}老师您好！我是{公司名}的HR。看到您在{最近公司}担任{职位}的丰富经验，特别是在{具体领域}方面的深厚积累。我们公司目前正在寻找一位有上市/IPO财务管理经验的CFO，不知您是否方便聊聊？
```

**模板B（拟IPO方向）：**
```
您好，关注到您的财务管理和资本运作背景非常优秀。我们是{行业}赛道的{公司阶段}企业，计划在未来2-3年推进IPO，正在寻找一位有丰富经验的CFO加入核心团队。如果感兴趣，欢迎进一步沟通~
```

###### CTO / 技术高管

```
您好！我是{公司}的HR负责人。看到您在技术管理领域的卓越履历，特别是{核心技术栈/团队规模}方面的经验与我们高度契合。我们正在招募一位CTO来带领{N}人技术团队推进{核心项目}，期待与您深入交流。
```

###### 投融资总监/VP

```
{姓名}总好！我是{公司}的HR。了解到您在投融资和资本市场方面的丰富经验，特别是{IPO/融资/尽调}经历让我们印象深刻。我们是一家处于{融资轮次}阶段的{行业}企业，正在寻找一位投融资负责人协助完成下一轮融资，不知是否有兴趣了解？
```

##### 专业岗位话术（工程师/产品/算法等）

###### 算法工程师

```
同学您好！👋 看到您的算法背景很棒——{具体亮点，如顶会论文/GitHub项目/大厂实习}。我们是{公司名}（{赛道描述，如细胞治疗/AI制药}），正在用AI解决{具体问题}的技术挑战。如果您对{医疗AI/前沿算法}方向感兴趣，欢迎随时聊聊~
```

###### 软件开发工程师

```
Hi！关注到您的{语言/框架}开发经验很扎实。我们是{公司}，正在打造{产品/系统}，技术栈是{技术栈列表}，团队氛围很好。目前开放{岗位名称}岗位，不知道您有没有兴趣了解一下？期待回复！
```

###### 产品经理

```
您好！看了您的产品经历，特别是在{B端/C端/某领域}的产品经验很有参考价值。我们正在寻找一位{高级/资深}产品经理来负责{产品线}的规划与迭代，如果方向匹配的话，欢迎聊聊机会~
```

###### 数据分析师/数据科学家

```
你好呀！看到您的数据分析能力很强——熟悉{工具/技能组合}。我们团队有很多有趣的数据可以挖（{业务场景简述}），如果你对用数据驱动业务决策感兴趣，欢迎来聊~
```

###### 工艺开发工程师（生物医药）

```
您好，看到您在{公司}担任细胞培养/工艺开发相关职位，我们正在寻找有生物反应器（KrosFlo KR2i）和大规模细胞培养经验的工艺开发工程师，地点北京，不知是否有兴趣了解一下？
```

##### 应届生/实习生话术

```
同学你好！🎓 看到{学历/学校}背景很优秀~ 我们{公司名}正在招{岗位}方向的{全职/实习}同学，团队里有很nice的mentor带，成长空间很大。如果你对{行业/方向}感兴趣，欢迎投递简历或直接聊聊！
```

##### 消息跟进模板

###### 第二次触达（首次无回复后3-5天）

```
{姓名}好，上次给您发的消息不知道有没有看到😊 再简单介绍一下：我们是做{业务简介}的，这个岗位的核心吸引点是{1-2个亮点，如股权激励/技术挑战/成长空间}。如果有兴趣的话随时联系我~
```

###### 面试邀约

```
{姓名}您好！经过初步沟通，我们对您的背景很认可，想邀请您进行一次面试交流：
📅 时间：{日期时间}
📍 方式：{线上会议/现场面试}
👥 面试官：{职位+姓名}
请问这个时间方便吗？
```

**速度控制要求（重要！）：**
- ⚠️ **每次操作间隔≥2秒**，避免被猎聘检测封禁
- ⚠️ 不要短时间内批量发送大量消息
- ⚠️ 单日建议最多触达20-30位候选人

---

### Phase 6: 简历详情查看

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

---

### Phase 7: 获取联系方式

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

---

### Phase 8: 批量数据导出

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

---

## 完整工作流程总结

### 标准流程：搜索 → 评分 → 生成链接 → 发送邮件

```
用户："搜索CFO和IT候选人，限定北京地区"
  ↓
【Phase 1: 搜索候选人】
  1. 打开猎聘HR后台（CDP Proxy）
  2. 搜索"CFO" → 添加"北京"筛选 → 提取20人
  3. 搜索"IT GMP/LIMS" → 添加"北京"筛选 → 提取20人
  ↓
【Phase 2: AI评分】
  4. 根据岗位要求对每个候选人评分
  5. 生成 Markdown 报告
  ↓
【Phase 3: 获取简历链接】
  6. 从搜索结果提取 resIdEncode
  7. 构造简历详情页链接
  8. 生成 HTML 文件（表格 + 查看简历按钮）
  ↓
【Phase 4: 发送邮件】
  9. 用户："发邮件"
  10. 调用 QQ 邮箱 SMTP 发送
  11. 邮件已发送到指定邮箱
```

### 输出文件

| 文件 | 格式 | 内容 |
|------|------|------|
| `CFO候选人_北京.md` | Markdown | CFO候选人列表（20人） |
| `IT候选人_北京.md` | Markdown | IT候选人列表（20人） |
| `候选人链接_北京.html` | HTML | 格式化邮件内容，含40个简历链接 |

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
# 右上角应显示用户名而非"登录/注册"
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
| APP扫码图标 | `._40108xY5VS` | 专用登录页(/login)二维码切换按钮 |
| APP扫码Tab | `text=APP扫码` | 二维码面板中的"APP扫码"选项卡 |
| 登录状态 | `.user-nav .name` 或 header中的用户名 | 判断是否已登录 |

---

## candidate_scorer.py 使用说明

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
  --template bioprocess \
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

## 输出交付物

完成完整流程后，应交付：

| 交付物 | 格式 | 内容 |
|--------|------|------|
| 候选人排行榜 | Markdown表格 | TOP N候选人，含评分和理由 |
| CSV数据文件 | `.csv` | 全部搜索结果的详细数据 |
| 执行摘要 | 文字报告 | 搜索数量、TOP推荐、费用预估、下一步建议 |
| 联系方式（可选） | 文字/表格 | 已获取的手机号/邮箱（需付费） |
| HTML邮件 | `.html` | 格式化邮件，含TOP20表格和"查看简历"按钮 |

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

### v2.3 (2026-07-07)

- **⭐ 核心升级：简历链接获取方式**：使用 `resIdEncode` 参数生成简历详情页链接（不再使用转发链接）
- **⭐ 核心升级：列表展示方式**：HTML格式输出（含表格和"查看简历"按钮）
- **⭐ 核心升级：发邮件方式**：QQ邮箱SMTP（已验证授权码有效，不会过期）
- **新增：完整评分模板库**：7套预设评分模板（CFO、CTO、算法工程师、产品经理、投融资、HRD、工艺开发工程师）
- **新增：完整沟通话术模板库**：高管岗位、专业岗位、应届生、消息跟进等话术
- **新增：搜索关键词详细规则**：不同岗位类型的搜索策略和筛选条件设置规则
- **优化：文档结构重组**：按实际执行顺序重新组织Phase 0-8

### v2.0 (2026-06-01)
- **新增CDP直连支持**：复用用户已登录Chrome，无需扫码
- **新增生物医药工艺开发工程师评分模板**（`bioprocess`）
- **修复** `candidate_scorer.py` 中的多个bug
- **新增** HTML邮件生成功能（可直接发送格式化邮件）
- **更新** 登录流程说明（区分APP扫码模式和CDP直连模式）

### v1.0 (2026-05-22)
- 初始版本
- 基于CFO候选人实操验证
- 支持搜索、AI评分、简历查看、联系方式获取、CSV导出
