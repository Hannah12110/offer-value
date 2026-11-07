---
name: offer-decision
description: "Load when 用户问这个 Offer 能选吗、公司值得去吗、多 Offer 比较、谈薪或换城市工作，需要结合职业目标开展有证据的机会尽调。"
---
# 这个 Offer 能选吗？
支持 A 单 Offer 尽调、B 多 Offer 比较、C 谈薪准备。只提供建议，不替用户接受、拒绝或联系雇主。概念框架：经济回报 + 职业资本增量 + 未来选择权 − 机会成本 − 不确定性；各项不混作货币加减。

## 执行
1. 将自然语言或用户主动提供的本地 Markdown/TXT/JSON/PDF 整理为 assets 中的输入结构。最少公司、岗位、城市即可开始；先确认决策时限、主体歧义、强约束、薪资结构和目标中的关键缺口，每轮最多问三个优先问题，同时推进不依赖回答的研究。PDF 使用当前环境可用的本地读取工具；没有工具则标记未读，不能假装读过。不得上传私人材料至研究服务；公开搜索查询只含必要公开关键词，不含简历内容。
2. 读取 [研究流程](references/research-workflow.md) 和 [证据规范](references/evidence-policy.md)。区分 confirmed、verbal、pre_salary、interview；UNKNOWN 用 JSON null。同名公司先列候选，未消歧不归并财务/诉讼。按联网工具实际可用性执行研究；失败保留模块结果和失败原因，离线用用户材料与假设继续。
3. 按模块需要加载：[行业](references/industry-research.md)、[岗位](references/role-research.md)、[公司](references/company-diligence.md)、[Base](references/location-intelligence.md)、[职业资本](references/career-capital.md)、[经济模型](references/compensation.md)、[风险机会成本](references/risks-opportunity-cost.md)、[决策谈薪](references/decision-negotiation.md)。A 覆盖全部；B 每个 Offer 同口径、同权重、同证据截止日；C 优先岗位/薪酬/风险/决策，其他模块仍报告已知和缺口。
4. 为重要结论建 Evidence Ledger；使用 [评分量表与数据契约](references/scoring-rubric.md) 创建子指标、区间、证据引用和规则状态。先运行 scripts/validate_evidence.py，再运行 scripts/score_offer.py 和 scripts/calculate_compensation.py。脚本相对路径均以本 Skill 目录为基准；不依赖当前工作目录。
5. 结合脚本结果按 assets/report-template.md 写十四节中文报告；可将各节写进 JSON sections 后运行 scripts/render_report.py，脚本自动附评分、经济结果、证据链接。每项判断标 [FACT]、[ESTIMATE]、[INFERENCE] 或 [UNKNOWN]。事实/观点类型另存 claim_kind；假设用 ESTIMATE 并显式说明 assumption。引用证据 ID 与来源链接。保留分歧和待核验项，不以评分制造确定感。
6. 执行权重和关键未知项敏感性分析，展示乐观/基准/不利情景及不接受的反事实，不编概率。给出 ACCEPT / CONDITIONAL_ACCEPT / NEGOTIATE / HOLD / DECLINE；证据状态单独显示 INSUFFICIENT_EVIDENCE。低覆盖或关键缺口不得强行接受。报告落盘前检查每条重要结论与证据、三个生活预算、90 天和 6/12/24 月检查点。

## 输入输出
以 assets/profile.example.json、offer.example.json 和 assessment.example.json 为可运行结构示例；示例仅含虚构占位，绝不默认成任何用户画像。结构化研究输入和输出保存在用户指定项目目录；只读取用户授权材料，避免覆盖原件。脚本全为 Python 3.10+ 标准库，无网络调用。研究由当前 Codex 的浏览能力完成；脚本不会自行抓取或调用模型。未安装可选工具不妨碍离线计算。入口识别依赖 Codex 加载本目录，不能声称静态校验等于已在新会话触发验证。
