# Module 6 · Compensation & Living Economics
字段和公式见 assets/compensation.example.json。所有金额使用同一 currency；未知用 null，已确认没有才写 0。fixed_monthly × guaranteed_months + guaranteed_allowance_annual 为保障税前年收入；奖金、提成、年终奖只进显式 target_variable_annual。保底十三薪须有书面依据；口头目标奖金不是保底。期权不算现金，单列归属/行权/流动性与归零风险。公司缴存公积金不计当月自由现金。
脚本只有 generic 与 CN_resident_annual 两种估计。中国居民综合所得年度税率需传当前政策 URL 和 as_of；扣除额/个人社保公积金/专项附加扣除须人工核实。未知个人扣款则税后 null，可另跑标明假设的情景；不默认深圳比例适用于其他城市。年终奖独立计税、非居民、跨境税和股权税不支持；整年满勤、全年一致工资、奖金并入综合所得假设要显示。有效期由操作者核验，不把 as_of 当官方保证。
年净收入/12 是年度月均，不是每月工资到账；常规现金/月与递延奖金分列说明。储蓄=净收入−12×月预算−首年一次性成本；两三年累计默认工资/成本不增长、无投资收益、持续就业。时薪除以实际工作小时×52；通勤可另加，明确是否含加班/通勤。搬迁永久费用和可退押金分别报告。
不同币种禁止直接加减/排名；汇率须有方向、日期、来源，未来外汇和生活成本波动仍须区间。MVP 对经济结果不自动换汇；先人工统一币种后计算。

已知固定月薪和保底月数时，known_fixed_gross_annual保留固定年薪；未知保底补贴会令总保障年收入仍null，guaranteed_gross_lower_bound仅表示已知固定部分下界，不是把未知补贴确认为0。generic净薪override不得高于已知保障税前；额外收入应单列，不混进保障净薪。
MVP支持CNY/USD/EUR/GBP/HKD/JPY/SGD/AUD/CAD/CHF/NZD/INR/KRW/TWD；其他币种明确拒绝，不把任意三字母当有效ISO币种。
