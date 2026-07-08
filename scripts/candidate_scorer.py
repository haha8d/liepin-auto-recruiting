#!/usr/bin/env python3
"""
猎聘候选人评分工具 (Candidate Scorer) v2.5
通用化的AI评分引擎，支持任意岗位的候选人打分排序

用法:
  python3 candidate_scorer.py --input candidates.csv --template cfo --output scored.csv
  python3 candidate_scorer.py --input candidates.csv --custom "CFO经验(30),CPA(15),四大(15)" --output scored.csv

参数:
  --input    输入CSV文件（猎聘导出的候选人数据）
  --template 使用预设通用模板 (cfo|cto|algorithm|pm|investment|hrd)
  --custom   自定义评分规则，格式: "维度名(权重),维度名(权重)"
  --output   输出文件路径（默认: scored_candidates.csv）
  --top      仅输出TOP N条（默认: 全部）
  --target-city  目标城市（用于地区匹配加分）

说明:
  公司专属角色模板（含具体权重/关键词/设备要求）统一维护在
  references/company_context.md 第4节，不在本脚本内置。
  如某岗位在 company_context 中定义了专属模板，建议直接用 --custom 传入对应规则。
"""

import csv
import json
import re
import argparse
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ScoringRule:
    """单条评分规则"""
    name: str
    weight: int
    criteria: str
    keywords: List[str] = None
    negative_keywords: List[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.negative_keywords is None:
            self.negative_keywords = []


@dataclass
class Candidate:
    """候选人数据结构"""
    rank: int = 0
    name: str = ""
    age: int = 0
    experience_years: int = 0
    education: str = ""
    location: str = ""
    expected_city: str = ""
    position: str = ""
    salary: str = ""
    industry: str = ""
    company1: str = ""
    title1: str = ""
    period1: str = ""
    company2: str = ""
    title2: str = ""
    period2: str = ""
    school: str = ""
    major: str = ""
    tags: str = ""
    match_keywords: str = ""
    notes: str = ""
    target_city: str = ""  # 用于地区匹配判断

    # 评分结果
    score: int = 0
    score_details: Dict[str, int] = None
    score_reasoning: str = ""

    def __post_init__(self):
        if self.score_details is None:
            self.score_details = {}


# ============================================================
# 预设评分模板库 v2.0
# ============================================================

SCORING_TEMPLATES: Dict[str, List[ScoringRule]] = {
    "cfo": [
        ScoringRule("上市公司CFO经验", 30,
            "有上市公司CFO/财务总监经验得满分；拟上市公司扣5分",
            ["CFO", "首席财务官", "财务总监", "财务VP", "上市", "IPO"]),
        ScoringRule("注册会计师CPA", 15,
            "有CPA/ACCA得满分；中级会计职称扣5分",
            ["CPA", "ACCA", "注册会计师", "CMA", "CFA"]),
        ScoringRule("四大/顶级事务所", 15,
            "德勤/普华永道/毕马威/安永经验得满分",
            ["德勤", "普华永道", "毕马威", "安永", "PwC", "Deloitte", "KPMG", "EY", "四大", "Big4"]),
        ScoringRule("审计背景", 10,
            "有审计总监/经理/合伙人经验",
            ["审计", "Audit", "会计师事务所", "内控"]),
        ScoringRule("MBA/EMBA", 8,
            "中欧/长江等Top MBA满分",
            ["MBA", "EMBA", "工商管理硕士"]),
        ScoringRule("行业匹配", 5,
            "与目标行业相关",
            []),
        ScoringRule("名校背景", 5,
            "985/QS前100/清北复交",
            ["清华", "北大", "复旦", "交大", "浙大", "中欧", "长江", "人大"]),
        ScoringRule("资深加分", 5,
            "15年+加2分，20年+加5分",
            []),
    ],

    "cto": [
        ScoringRule("大厂技术管理经验", 25,
            "BAT/字节/TMD等技术VP/总监以上",
            ["CTO", "技术总监", "技术VP", "首席技术官", "研发总监"]),
        ScoringRule("技术栈匹配", 20,
            "与目标技术栈一致",
            []),
        ScoringRule("团队管理规模", 15,
            "管理50人+团队满分",
            ["管理", "带领", "团队", "Leader", "负责人"]),
        ScoringRule("开源影响力", 10,
            "GitHub高星项目或知名开源贡献",
            ["开源", "GitHub", "开源项目", "KVM", "docker", "Kubernetes"]),
        ScoringRule("名校/PhD", 10,
            "CS名校或博士学位",
            ["博士", "PhD", "清华", "北大", "MIT", "Stanford"]),
        ScoringRule("创业/IPO经历", 10,
            "创业公司CTO或上市技术负责人",
            ["创业", "联合创始人", "Co-founder", "IPO", "上市"]),
        ScoringRule("架构能力", 10,
            "大规模系统架构设计",
            ["架构", "Architecture", "高并发", "分布式", "微服务"]),
    ],

    "algorithm": [
        ScoringRule("院校背景", 20,
            "CS/AI强校满分",
            ["清华", "北大", "浙大", "上交", "复旦", "中科大", "南大", "哈工大",
             "985", "CMU", "MIT", "Stanford", "Berkeley"]),
        ScoringRule("AI算法实习/项目", 15,
            "大厂AI实习或高质量论文/项目",
            ["实习", "AI", "算法", "深度学习", "机器学习", "NLP", "CV",
             "大模型", "LLM", "PyTorch", "TensorFlow"]),
        ScoringRule("开源/GitHub", 15,
            "高质量开源贡献",
            ["GitHub", "开源", "Star", "Contributor", "huggingface"]),
        ScoringRule("地区匹配", 10,
            "目标城市优先",
            []),
        ScoringRule("技术栈匹配", 10,
            "Python/C++/PyTorch/TensorFlow/JAX",
            ["Python", "C++", "PyTorch", "TensorFlow", "JAX", "CUDA"]),
        ScoringRule("论文发表", 10,
            "顶会论文一作",
            ["CVPR", "ICCV", "NeurIPS", "ICML", "AAAI", "ACL",
             "EMNLP", "ICLR", "论文", "一作"]),
        ScoringRule("竞赛获奖", 10,
            "ACM/Kaggle等竞赛",
            ["ACM", "Kaggle", "数学建模", "金牌", "Gold", "一等奖"]),
        ScoringRule("简历新鲜度", 10,
            "近期活跃加分",
            ["今天活跃", "7天内活跃", "30天内活跃", "在线"]),
    ],

    "pm": [
        ScoringRule("产品经验年限", 20,
            "5年+完整0-1产品经验满分",
            ["产品经理", "PM", "产品总监", "高级产品", "资深产品"]),
        ScoringRule("行业匹配", 20,
            "有目标行业产品经验",
            []),
        ScoringRule("B端/C端能力", 15,
            "按目标方向匹配",
            ["B端", "C端", "SaaS", "ToB", "ToC"]),
        ScoringRule("数据驱动能力", 15,
            "数据分析/A/B测试/增长经验",
            ["数据", "分析", "A/B", "增长", "用户研究", "埋点"]),
        ScoringRule("大厂背景", 10,
            "头部互联网公司产品经验",
            ["字节", "腾讯", "阿里", "百度", "美团", "滴滴", "快手"]),
        ScoringRule("学历", 10,
            "本科以上；硕士加分",
            ["硕士", "MBA", "本科"]),
        ScoringRule("项目成果", 10,
            "从0到1成功案例或显著增长",
            ["从0到1", "DAU", "营收", "增长", "百万", "千万"]),
    ],

    "investment": [
        ScoringRule("IPO/上市经验", 30,
            "完整IPO操盘经验（A股/H股/美股）",
            ["IPO", "上市", "A股", "港股", "美股", "纳斯达克", "科创板", "创业板"]),
        ScoringRule("融资资源/渠道", 20,
            "有VC/PE/FA机构人脉或成功融资案例",
            ["融资", "VC", "PE", "投资", "FA", "路演", "尽调", "DD"]),
        ScoringRule("尽职调查/合规", 15,
            "DD/合规内控/财务审计经验",
            ["尽职调查", "合规", "内控", "财务审计", "法务", "风控"]),
        ScoringRule("行业认知", 15,
            "对目标行业深度理解",
            []),
        ScoringRule("资本市场资质", 10,
            "保代资格/CFA/CPA",
            ["保代", "CFA", "CPA", "FRM", "证券从业"]),
        ScoringRule("沟通谈判力", 10,
            "投资人对接/路演/融资谈判经验",
            ["谈判", "路演", "投资人", "董事会", "股东"]),
    ],

    "hrd": [
        ScoringRule("HR管理经验", 25,
            "HRD/HRVP级别管理经验",
            ["HRD", "HRVP", "HR总监", "人力资源总监", "CHRO"]),
        ScoringRule("招聘能力", 20,
            "大规模招聘/猎头管理/RPO经验",
            ["招聘", "猎头", "RPO", "人才获取", "Recruiting"]),
        ScoringRule("薪酬绩效", 15,
            "薪酬体系设计/股权激励设计经验",
            ["薪酬", "绩效", "股权激励", "OKR", "KPI", "Compensation"]),
        ScoringRule("组织发展OD", 15,
            "OD/组织变革/文化建设项目经验",
            ["OD", "组织发展", "组织变革", "文化", "变革管理"]),
        ScoringRule("行业匹配", 10,
            "目标行业HR经验",
            []),
        ScoringRule("名企背景", 10,
            "头部企业或咨询公司背景",
            ["美世", "怡安翰威特", "韦莱韬悦", "光辉国际", "HayGroup"]),
    ],

    # 注：公司专属角色模板（如生物医药工艺开发工程师）不再内置，
    # 统一维护在 references/company_context.md 第4节，执行时按岗位加载。
}


def parse_custom_rules(rule_str: str) -> List[ScoringRule]:
    """
    解析自定义评分规则字符串

    格式示例:
      "CFO经验(30):CFO,财务总监,IPO;CPA(15):注册会计师,ACCA"
      "院校背景(20),AI实习(15),开源(15)"
    """
    rules = []

    # 尝试完整格式：维度名(权重):关键词1,关键词2
    # 注意：分号分隔不同维度
    parts = [p.strip() for p in rule_str.split(';') if p.strip()]

    for part in parts:
        # 匹配 "维度名(权重):关键词1,关键词2" 格式
        full_match = re.match(r'^(.+?)\((\d+)\)\s*:\s*(.+)$', part)
        if full_match:
            name = full_match.group(1).strip()
            weight = int(full_match.group(2))
            keywords = [k.strip() for k in full_match.group(3).split(',') if k.strip()]
            rules.append(ScoringRule(
                name=name,
                weight=weight,
                criteria=f"自定义: {name}",
                keywords=keywords
            ))
        else:
            # 尝试简洁格式："维度名(权重)"
            simple_match = re.match(r'^(.+?)\((\d+)\)$', part)
            if simple_match:
                name = simple_match.group(1).strip()
                weight = int(simple_match.group(2))
                # 将维度名按/或,分割作为关键词
                keywords = re.split(r'[/,、，\s]+', name)
                keywords = [k for k in keywords if k]
                rules.append(ScoringRule(
                    name=name,
                    weight=weight,
                    criteria=f"自定义: {name}",
                    keywords=keywords
                ))

    # 如果分号格式未解析到任何规则，尝试逗号分隔的简洁格式
    if not rules:
        # "维度名(权重),维度名(权重)" 格式
        comma_parts = [p.strip() for p in rule_str.split(',') if p.strip()]
        for part in comma_parts:
            simple_match = re.match(r'^(.+?)\((\d+)\)$', part)
            if simple_match:
                name = simple_match.group(1).strip()
                weight = int(simple_match.group(2))
                keywords = re.split(r'[/,、，\s]+', name)
                keywords = [k for k in keywords if k]
                rules.append(ScoringRule(
                    name=name,
                    weight=weight,
                    criteria=f"自定义: {name}",
                    keywords=keywords
                ))

    return rules


def score_candidate(candidate: Candidate, rules: List[ScoringRule], target_city: str = "") -> Tuple[int, Dict[str, int], str]:
    """
    对单个候选人进行评分

    Returns:
        (总分, 各维度得分明细, 评分理由)
    """
    details = {}
    reasoning_parts = []
    total_score = 0

    # 将候选人所有信息合并为文本用于关键词匹配
    candidate_text = json.dumps({
        "name": candidate.name,
        "position": candidate.position,
        "title1": candidate.title1,
        "company1": candidate.company1,
        "title2": candidate.title2,
        "company2": candidate.company2,
        "school": candidate.school,
        "major": candidate.major,
        "tags": candidate.tags,
        "match_keywords": candidate.match_keywords,
        "notes": candidate.notes,
        "industry": candidate.industry,
        "education": candidate.education,
        "location": candidate.location,
        "expected_city": candidate.expected_city,
    }, ensure_ascii=False).lower()

    for rule in rules:
        score = 0
        matched_items = []

        # 特殊处理：工作年限加分
        if not rule.keywords and "资深" in rule.name:
            if candidate.experience_years >= 20:
                score = min(rule.weight, 5)
                matched_items.append(f"20年+经验(+{score})")
            elif candidate.experience_years >= 15:
                score = min(rule.weight, 2)
                matched_items.append(f"15年+经验(+{score})")

        # 特殊处理：简历新鲜度
        elif not rule.keywords and ("新鲜度" in rule.name or "活跃" in rule.name):
            if "今天活跃" in candidate.tags or "在线" in candidate.tags:
                score = rule.weight
                matched_items.append("今天活跃/在线")
            elif "7天内活跃" in candidate.tags:
                score = int(rule.weight * 0.8)
                matched_items.append("7天内活跃")
            elif "30天内活跃" in candidate.tags:
                score = int(rule.weight * 0.5)
                matched_items.append("30天内活跃")

        # 特殊处理：地区匹配
        elif not rule.keywords and ("地区" in rule.name or "城市" in rule.name or "地点" in rule.name):
            if target_city:
                if target_city in (candidate.location or "") or target_city in (candidate.expected_city or ""):
                    score = rule.weight
                    matched_items.append(f"地点匹配({target_city})")
            # 无target_city时不打分（保持0）

        # 关键词匹配评分
        else:
            for kw in rule.keywords:
                if kw.lower() in candidate_text:
                    # 按匹配的关键词数量分配分数
                    partial = max(1, rule.weight // max(len(rule.keywords), 1))
                    score = min(score + partial, rule.weight)
                    matched_items.append(kw)
                    if score >= rule.weight:
                        break

        details[rule.name] = score
        total_score += score

        if score > 0:
            reasoning_parts.append(f"{rule.name}({score}): {', '.join(matched_items)}")

    reasoning = "; ".join(reasoning_parts) if reasoning_parts else "无明显匹配项"
    return total_score, details, reasoning


def read_candidates_csv(filepath: str) -> List[Candidate]:
    """读取猎聘导出的CSV文件"""
    candidates = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                c = Candidate()
                c.rank = safe_int(row.get('排名', '0'))
                c.name = row.get('姓名', '')
                c.age = safe_int(row.get('年龄', '0'))
                c.experience_years = safe_int(row.get('工作年限', '0'))
                c.education = row.get('学历', '')
                c.location = row.get('现居地', '')
                c.expected_city = row.get('期望城市', '')
                c.position = row.get('期望职位', '')
                c.salary = row.get('期望薪资', '')
                c.industry = row.get('行业', '')
                c.company1 = row.get('最近公司1', '')
                c.title1 = row.get('最近职位1', '')
                c.period1 = row.get('最近时间1', '')
                c.company2 = row.get('最近公司2', '')
                c.title2 = row.get('最近职位2', '')
                c.period2 = row.get('最近时间2', '')
                c.school = row.get('学校1', '')
                c.major = row.get('专业1', '')
                c.tags = row.get('标签', '')
                c.match_keywords = row.get('匹配关键词', '')
                c.notes = row.get('备注', '')
                candidates.append(c)
    except Exception as e:
        print(f"[ERROR] 读取CSV失败: {e}", file=sys.stderr)
    return candidates


def write_scored_csv(candidates: List[Candidate], filepath: str):
    """输出评分后的CSV文件"""
    fieldnames = [
        '排名', '姓名', '年龄', '工作年限', '学历', '现居地', '期望城市',
        '期望职位', '期望薪资', '行业', '总分', '评分详情', '评分理由',
        '最近公司1', '最近职位1', '最近时间1',
        '最近公司2', '最近职位2', '最近时间2',
        '学校1', '专业1', '标签', '备注'
    ]

    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, c in enumerate(candidates, 1):
            writer.writerow({
                '排名': i,
                '姓名': c.name,
                '年龄': c.age,
                '工作年限': c.experience_years,
                '学历': c.education,
                '现居地': c.location,
                '期望城市': c.expected_city,
                '期望职位': c.position,
                '期望薪资': c.salary,
                '行业': c.industry,
                '总分': c.score,
                '评分详情': json.dumps(c.score_details, ensure_ascii=False),
                '评分理由': c.score_reasoning,
                '最近公司1': c.company1,
                '最近职位1': c.title1,
                '最近时间1': c.period1,
                '最近公司2': c.company2,
                '最近职位2': c.title2,
                '最近时间2': c.period2,
                '学校1': c.school,
                '专业1': c.major,
                '标签': c.tags,
                '备注': c.notes,
            })


def safe_int(val: str, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return default


def main():
    parser = argparse.ArgumentParser(description='猎聘候选人智能评分工具 v2.0')
    parser.add_argument('--input', '-i', required=True, help='输入CSV文件')
    parser.add_argument('--template', '-t', choices=list(SCORING_TEMPLATES.keys()),
                        help=f'预设评分模板: {", ".join(SCORING_TEMPLATES.keys())}')
    parser.add_argument('--custom', '-c', help='自定义评分规则: "维度(权重):关键词,关键词;维度(权重):关键词"')
    parser.add_argument('--output', '-o', default='scored_candidates.csv', help='输出文件')
    parser.add_argument('--top', '-n', type=int, default=0, help='仅输出TOP N条')
    parser.add_argument('--target-city', default='', help='目标城市（用于地区匹配加分）')
    args = parser.parse_args()

    # 确定评分规则
    if args.template:
        rules = SCORING_TEMPLATES[args.template]
        print(f"[INFO] 使用预设模板: {args.template} ({len(rules)}个维度)")
    elif args.custom:
        rules = parse_custom_rules(args.custom)
        print(f"[INFO] 使用自定义规则 ({len(rules)}个维度)")
    else:
        print("[ERROR] 必须指定 --template 或 --custom")
        parser.print_help()
        return

    # 读取候选人数据
    candidates = read_candidates_csv(args.input)
    print(f"[INFO] 读取到 {len(candidates)} 条候选人记录")

    if not candidates:
        print("[WARN] 没有可处理的候选人数据")
        return

    # 逐个评分
    for c in candidates:
        c.target_city = args.target_city
        score, details, reasoning = score_candidate(c, rules, args.target_city)
        c.score = score
        c.score_details = details
        c.score_reasoning = reasoning

    # 按分数降序排列
    candidates.sort(key=lambda x: x.score, reverse=True)

    # 截取TOP N
    if args.top > 0:
        candidates = candidates[:args.top]
        print(f"[INFO] 输出 TOP {args.top}")

    # 输出结果
    write_scored_csv(candidates, args.output)
    print(f"\n[DONE] 评分完成! 结果已保存至: {args.output}")

    # 打印TOP 10摘要
    print("\n=== TOP 候选人 ===")
    header = f"{'排名':<4} {'姓名':<8} {'年龄':<4} {'经验':<4} {'学历':<6} {'公司':<20} {'职位':<16} {'总分'}"
    print(header)
    print("-" * len(header))
    for i, c in enumerate(candidates[:10], 1):
        company = c.company1[:18] if c.company1 else "(未知)"
        title = c.title1[:14] if c.title1 else "(未知)"
        print(f"{i:<4} {c.name:<8} {c.age or '?':<4} {c.experience_years or '?':<4} "
              f"{c.education[:6]:<6} {company:<20} {title:<16} {c.score}")


if __name__ == '__main__':
    main()
