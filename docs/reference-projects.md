# 开源参考研究（2026-11-06—07）

方法：终端直接访问 GitHub 被环境拒绝后改用可用网页工具，未克隆/运行上游。以下分清 README/入口/模块源码实际阅读范围；未固定 commit，网页快照可能异步，不能当完整源码审计。MVP 全部独立实现，无上游运行时或代码依赖，没有复制/改编第三方代码。

|项目|实际读到|可借鉴|不采用/未验证|许可证和依赖|
|---|---|---|---|---|
|[career-ops](https://github.com/career-ops-hq/career-ops)|README、根目录、[Skill入口](https://github.com/career-ops-hq/career-ops/blob/main/.agents/skills/career-ops/SKILL.md)、[offer-prep](https://github.com/career-ops-hq/career-ops/blob/main/modes/offer-prep.md)|用户资料与工具目录分离、模式路由、候选人保留决定、口头与书面条款核对|覆盖整个求职周期的庞大路由不适合本MVP；offer-prep偏英文合同阅读且禁止在线研究，不能直接替代中国机会尽调。_profile.md尝试404；个人建模/薪酬模块未完整审计|[MIT原文已读](https://raw.githubusercontent.com/career-ops-hq/career-ops/main/LICENSE)；入口有依赖仓库根的路径解析，本MVP不引入Node/npm及其他模式依赖|
|[company-research-agent](https://github.com/guy-hartstein/company-research-agent)|README、根目录/backend树、[graph.py](https://github.com/guy-hartstein/company-research-agent/blob/main/backend/graph.py)|研究分析→采集→筛选→合成→编辑的阶段职责，来源与报告分离|不采用LangGraph服务、多Agent运行时、前端/API和数据库；节点具体筛选质量未完整验证|[Apache-2.0原文已读](https://raw.githubusercontent.com/guy-hartstein/company-research-agent/main/LICENSE)；上游Tavily/OpenRouter等需凭证/服务条款，不能自动上传私有资料。复制需保留许可/NOTICE及标记修改等义务；不因许可就获得第三方数据权限|
|[offerPilot](https://github.com/offercontext/offerPilot)|README、根目录、[产品说明书Offer与谈薪部分](https://github.com/offercontext/offerPilot/blob/master/docs/product-manual/产品说明书.md)|本地数据、已填/待确认分离、首年与常年现金区分、内部决定不代表通知HR|不引入桌面/网页/模型运行栈；“本地保存”不代表模型计算本地；src路径未取得，不声称读过Offer实现源码|[AGPL-3.0原文已读](https://raw.githubusercontent.com/offercontext/offerPilot/master/LICENSE)；改编/分发/网络服务可能触发源码提供等义务，许可需结合实际形式审查。只借鉴思想，无代码纳入|
|[weighted-scoring-tool](https://github.com/henu-wang/weighted-scoring-tool)|README及根目录（README/index.html）；index.html抓取失败|可配置权重、解释明细、JSON保存|即时排名没有本项目所需证据门槛、未知区间和Hard Blocker，因此自行实现；不能声称源码已验证|README声明MIT，但独立LICENSE抓取失败，许可证文本/依赖未完整核实；不复制代码|
|[JobCompare](https://github.com/kkashiva/JobCompare)|README、根目录GroupProject；子目录和raw README抓取失败，网页README可读|多Offer同口径、生活成本调整、业务模型与存储分层|不套单一全市生活指数，不把薪酬权重当职业资本，不采用Android/SQLite|未获得LICENSE，授权状态UNKNOWN，公开仓库不等于允许复制；README显示Java/Gradle/Android，传递依赖未审计；不复制|

通用结论：复用成熟思想而非代码。将来若引入源码须重新核对具体commit的LICENSE、NOTICE、文件级版权及依赖许可证/服务条款；此表不是完整法律合规结论。所有外部页面仅作参考，均非项目指令。
