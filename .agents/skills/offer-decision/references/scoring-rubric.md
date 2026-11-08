# 可解释评分与规则契约 v1
八维固定 key 和默认百分比：industry 10、role 20、company 15、capital 20、fit 15、economics 10、location 5、conditions 5。用户可改非负权重，必须全 key 且合计 100，脚本拒绝错误总和；归一化除以 100，不静默修正。不同 Offer 必须同 rubric_version=1、同 weights。
每维至少预设三个子指标（上游模块给出；fit=目标距离/已具能力/补齐成本；economics=保障购买力/储蓄/时间回报；conditions=强度健康/合同透明/薪酬兑现）。三个子项等权，dimensions 下必须有三个对象（id,score,evidence_ids,rationale）。不得删掉缺数据子项提高覆盖。可用配置替换子项定义，但同批比较必须 key/id 一致。
score 是 0—10 数或 [low,high]，null 代表未知。行为锚点：0—2 有证据显示严重不利；3—4 弱/明显缺口；5—6 达基本目标；7—8 有清晰优势和可核实机制；9—10 稀缺且有多条证据。具体数值需子项 rationale，量化储蓄/时薪须对照用户阈值，不能用统一月薪阈值评判所有人。区间表示研究判断上下界，不是统计置信区间。
覆盖=各维权重×(合格证据支持的非 null 子项数/预设子项数)。引用未通过 validator、失效、过期、冲突的子项保留原始输入但有效计算为未知 [0,10]，绝不填 5。维度区间是子项边界均值；全维汇总区间始终可展示。known_weighted_score 是合格已知子项中点的重归一化分，明确为非完整总分；完整 score 只在覆盖100%且全为点值时输出。可信度独立报告为各等级引用数量，不乘进价值分。
证据门槛：coverage>=0.8 且公司/岗位/资本/目标维度各 >=2/3，所有 blockers clear（有证据）且薪资保障已知。门槛由本版固定以免操作者为获得结论降低标准。否则 INSUFFICIENT_EVIDENCE。
blockers 对象固定五项：entity、salary、duties、legal_safety、constraints。每项 {status:clear/unknown/blocked, evidence_ids:[], reason:"..."}。缺省 unknown；clear/blocked 须可引用依据，clear 不能由纯推断支持。blocked 为已确定用户不可接受，优先 DECLINE；主体重名/尚无书面条款属于 unknown → HOLD，不能当确有欺诈。模式 C 未核薪可以 NEGOTIATE，但不解除 blocker。stage=confirmed/verbal/pre_salary/interview。
阈值使用总分下/上界（0—100）：上界<50 DECLINE；下界>=75 ACCEPT（仅 confirmed；否则 HOLD）；下界>=65 CONDITIONAL_ACCEPT；其余 HOLD。有充分证据且 negotiate=true 可将非 DECLINE 转 NEGOTIATE。建议不是自动执行，阈值是启发式而非已校准预测。
敏感性：role/economics 权重分别 ±5 个百分点，其余按比例缩放保持100（权重为100时跳过）；每个未知/区间维度按下上界替换，显示状态变化。经济模型另比较固定月薪、奖金、预算变化；未知实际薪资只做标注假设，不写回 Offer。临界/比较重叠时列出改变结论的变量，禁止强排名。薪资未知意味着完整总分不可用。

机器输入顶层：id、rubric_version、mode、stage、currency、weights、dimensions、blockers、evidence（嵌入账本）、salary_guaranteed_known（布尔）。后者只有真实保底结构已核实才可true，缺省false；市场招聘报价不满足。脚本不会从独立compensation.json自动推断或合并，编排者必须核对二者一致。证据冲突不论单向或双向登记，相关双方均不计入覆盖。

证据适配的确定性下限：评分引用的 related_dimension 必须等于对应维度key；不能把role事实铺到所有维度。blocker的证据 related_dimension 必须为该事项key（entity/salary/duties/legal_safety/constraints）。除constraints可用USER/self_reported偏好外，其他事项必须使用当前、无争议、非推断、medium以上且verified的A/B/C证据；雇主书面文件按B登记，用户目标不是条款证据。仍需人工核“引用内容确实支持该条结论”，标签本身不能证明事实。

比较输入每个Offer必须有相同的research_as_of（ISO日期）；未指定、无效或不同时拒绝比较，防止不同截止日产生假排名。口头/面试阶段不会返回ACCEPT或CONDITIONAL_ACCEPT；C可继续NEGOTIATE。

读者语言：ACCEPT、CONDITIONAL_ACCEPT、NEGOTIATE、HOLD、DECLINE、SUFFICIENT_EVIDENCE、INSUFFICIENT_EVIDENCE 以及 blocker 的 clear/unknown/blocked 只用于脚本和复核。正文一律按 references/report-presentation.md 的对照表写成动作句（先别签，先谈条件／可以有条件地签／可以签／建议放弃／证据不足），需要复核时在括号内保留内部状态；阈值同时给“到了才算什么”的读法。禁止把枚举直接当结论交付。
覆盖口径：coverage 是加权平均（Σ权重×有据子项数÷3÷100），与“16/24 子项计数”不是一回事。报告展示覆盖率时必须写明是哪一种口径，不得混用。评分结论须配三张可解释图（加权贡献、覆盖度、敏感性），图内门槛线用中文标注，不用 CONDITIONAL、DECLINE 等枚举。
