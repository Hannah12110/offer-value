# Evidence Ledger
JSON 数组每项必须包含：evidence_id、claim、source_title、source_url、publisher、published_at、accessed_at、evidence_type、credibility、freshness、supports_or_conflicts、related_dimension、verification_status；另外 claim_kind、data_period、conflicts_with、private 可选。
类型 A 监管/政府/交易所/统计，B 企业自行披露，C 独立研究媒体，D 员工匿名观点，E 模型推断，USER 用户自报。credibility=high/medium/low/unknown；freshness=current/stale/unknown（由研究者按事实类型判断）；verification_status=verified/self_reported/unverified/conflicted。supports_or_conflicts=supports/conflicts/context。claim_kind=FACT/ESTIMATE/OPINION/INFERENCE/UNKNOWN。published_at 可 null，accessed_at ISO 日期必填，data_period 另存统计期间，不能借发布日期代替。
URL 是公开 http(s) 链接；本地私有证据 local://路径或 user://case/编号，private=true；不得伪造公网地址。个人履历/目标只能 user self_reported，不等于独立核实。推断用 inference://编号，不算已证实覆盖；估计不能仅因有引用而算可靠事实。
先按事实类型判断来源适配，再用一般优先序：监管统计 > 官方企业 > 独立研究媒体 > 原始真实 JD > 平台统计论坛 > 匿名。官方 JD 证明招聘要求强，证明现金流弱。高校转载招聘稿仍为企业自报。搜索摘要应标 unverified，打开正文核实后才 verified，无法打开写原因。原始页面可能更新，记录访问日和数据期间，保存必要摘录而非全文复制。
重大争议尽量交叉验证独立来源；矛盾用 conflicts_with 关联双方，不能删除不合意数据。仅确定“页面说了什么”不等于证实主张为真。判定 credible/current/verified 必须与来源和具体 claim 匹配。
脚本验证字段、枚举、日期、重复 ID、冲突引用和 URL，只证明结构完整；不证明页面真实、来源独立、结论有支撑或没有遗漏。评分仅将 verified/current/medium+ 的非推断非争议支持证据计入覆盖；保守不计自报公司宣传。用户目标维度允许 USER/self_reported/current 作为偏好证据。每个评分子项仍需文字解释，不能由证据数量自动打分。

related_dimension为单个评分维度key或blocker事项key。跨维引用若确有支持，应拆成不同claim并分别审查；不允许一个泛化事实自动覆盖所有维度。对同一原始来源的多claim不得误称独立来源。
