"""Compose fourteen sections, computed decisions and traceable sources."""
import argparse
from pathlib import Path
from common import read,dump,PLAIN_DECISION,PLAIN_STATUS,PLAIN_BLOCKER,PLAIN_EVIDENCE_TYPE,PLAIN_VERIFY,PLAIN_CRED,PLAIN_FRESH
from score_offer import sensitivity
from calculate_compensation import calculate
HEADINGS=['Executive Decision','Personal Career Fit','Industry Outlook','Role Outlook','Company Due Diligence','Base Intelligence','Career Capital Matrix','Compensation & Scenario Model','Risks & Opportunity Costs','Weighted Decision','Questions for HR & Hiring Manager','Negotiation Strategy','90-Day Action Plan','Sources & Evidence']


def render(d):
    if not isinstance(d,dict):raise ValueError('input must be an object')
    analysis=d.get('assessment',{});result=sensitivity(analysis);base=result['base'];economics=calculate(d.get('compensation',{'currency':'CNY'}));sections=d.get('sections',{})
    parts=['# Offer Decision Report',f"[FACT] 研究对象：{d.get('offer',{}).get('company','UNKNOWN')} / {d.get('offer',{}).get('role','UNKNOWN')} / {d.get('offer',{}).get('city','UNKNOWN')}。用户自报；研究模式 {analysis.get('mode','A')}。"]
    for i,title in enumerate(HEADINGS,1):
        text=sections.get(title,'[UNKNOWN] 本节证据不足。待研究并回填；不从其他模块的结论推定本节事实。')
        parts.extend([f'## {i}. {title}',text])
        if i==1:
            parts.append(f"[INFERENCE] 结论：**{PLAIN_DECISION[base['decision']]}**（内部状态 {base['decision']}）；{PLAIN_STATUS[base['evidence_status']]}（{base['evidence_status']}）；加权覆盖率 {base['coverage']:.1%}。决策信心由研究说明，不等同于分数或成功概率。")
            parts.append('[INFERENCE] 阈值读法：50 分以下建议放弃；达到 65 分才谈“可以有条件地签”；达到 75 分且已拿到书面 offer 才谈“可以签”。')
        if i==8:parts.append('```json\n'+dump(economics)+'\n```')
        if i==10:
            parts.append('|维度|权重 %|有效区间 /10|覆盖率|\n|---|---:|---|---:|')
            for k,v in base['dimensions'].items():parts.append(f"|{k}|{v['weight']}|{v['interval']}|{v['coverage']:.0%}|")
            parts.append(f"[ESTIMATE] 全维区间 {base['score_interval']}；完整总分 {base['score'] if base['score'] is not None else 'UNKNOWN'}；{base['known_score_label']} {base['known_weighted_score']}。可信度引用分布 {base['credibility_counts']}。")
            parts.append('[UNKNOWN] 待核实关口：'+', '.join(PLAIN_BLOCKER[b]+'（'+b+'）' for b in base['unresolved_blockers']))
            parts.append('[INFERENCE] 图表：同目录 charts/ 下三张——加权贡献（分数怎么垒起来、距门槛差多少）、覆盖度（哪些维度没有合格证据）、敏感性（换权重结论是否翻转）。表负责查数，图负责定位；每图前提出问题、图后写读图结论。')
            parts.append('敏感性分析（假设不增加证据覆盖）：\n```json\n'+dump(result['variants'])+'\n```')
        if i==14:
            for e in analysis.get('evidence',[]):
                parts.append(f"- **{e['evidence_id']}** [{e.get('claim_kind','FACT')}] {e['claim']} — [{e['source_title']}]({e['source_url']})；{e['publisher']}，发布 {e['published_at'] or '日期未知'}，数据期 {e.get('data_period') or '未标注'}，访问 {e['accessed_at']}；来源类型 {PLAIN_EVIDENCE_TYPE.get(e['evidence_type'],e['evidence_type'])}（{e['evidence_type']}），核验 {PLAIN_VERIFY.get(e['verification_status'],e['verification_status'])}（{e['verification_status']}），可信度 {PLAIN_CRED.get(e['credibility'],e['credibility'])}，时效 {PLAIN_FRESH.get(e['freshness'],e['freshness'])}；冲突 {e.get('conflicts_with',[])}。")
    return '\n\n'.join(parts)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('--output',required=True);a=p.parse_args()
    try:
        path=Path(a.output)
        if path.exists():raise ValueError('output exists; choose a revision filename')
        path.write_text(render(read(a.input)),encoding='utf-8')
    except (ValueError,KeyError,TypeError,OSError) as e:p.exit(2,f'Invalid input: {e}\n')
