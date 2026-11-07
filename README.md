# offer-value · 这个 Offer 能选吗？

基于真实证据和个人职业目标的 Codex Offer 决策辅助 Skill。支持单 Offer 深度尽调、多 Offer 横向比较及谈薪准备。

仓库名称为 `offer-value`，Skill 调用名保留 `offer-decision`。

## 安装与调用

将仓库作为 Codex Desktop 工作区打开，或在仓库根目录启动 Codex CLI。项目级技能位于 `.agents/skills/offer-decision/`。

```text
$offer-decision 这个 Offer 能选吗？公司：某公司；岗位：某岗位；Base：深圳。
$offer-decision 比较两份 Offer，我更看重职业资本与长期发展。
$offer-decision 我下周谈薪，已有口头 Offer，但薪资尚未确认。
```

也可将 `.agents/skills/offer-decision` 整个目录复制到其他项目的 `.agents/skills/` 下。仓库不会自动修改用户级 Skill 或全局配置。技能选择由 Codex 宿主负责；新会话自动发现尚未实测。

## 工作方式

八个研究模块覆盖行业、岗位、企业、Base、职业资本、薪酬、风险机会成本与决策谈薪。研究细则渐进加载，Python 脚本执行确定性计算与校验。

- 重要判断关联 Evidence Ledger，显示来源、时间、可信度和冲突。
- 未知薪资保持 null，不把招聘报价当个人 Offer。
- 固定保障和浮动收入分开；提供生活预算、时薪和储蓄情景。
- 先检查关键门槛，再展示区间评分、证据覆盖与敏感性分析。
- 证据不足时给出 HOLD；谈薪模式可建议 NEGOTIATE，不表示可以签约。
- 不自动联系 HR、接受或拒绝 Offer。

默认输出十四节中文 Markdown 报告。自然语言与用户主动提供的 Markdown/TXT/JSON/PDF 由 Codex 整理；脚本不解析自然语言或 PDF。没有可用本地 PDF 工具时保留未读状态。

## 运行环境

Python 3.10+，仅使用标准库，无 pip 或外部仓库运行依赖。联网研究使用 Codex 当前可用工具；无网络时可运行明确标记的离线报告。

```bash
python3 .agents/skills/offer-decision/scripts/run_offer.py \
  .agents/skills/offer-decision/assets/offer.example.json --out runs/minimal

python3 .agents/skills/offer-decision/scripts/score_offer.py \
  examples/comparison-synthetic.json --compare

python3 .agents/skills/offer-decision/scripts/validate_skill.py \
  .agents/skills/offer-decision

python3 -m unittest discover -s .agents/skills/offer-decision/tests -v
```

输出目录必须不存在，以免覆盖旧记录。更多输入契约见 Skill 的 references 与 assets。

## 结构

```text
.agents/skills/offer-decision/
  SKILL.md
  agents/openai.yaml
  references/   # 八个研究模块及共同规范
  scripts/      # 评分、薪酬、证据校验、报告与离线入口
  assets/       # 空画像、虚构示例及报告模板
  tests/        # 单元与命令行集成测试
docs/
examples/       # 仅虚构测试数据
```

## 验证与限制

67 项测试覆盖缺失薪资、证据冲突、权重、阻断、币种、证据截止日、经济计算及离线编排。静态检查只验证本项目支持的 YAML 标量、引用及文件语法，不等同于官方验证器或宿主调用测试。测试记录见 `docs/test-results.md`。

证据真实性、来源适配与评分理由仍需人工审查。区间不是统计置信区间，阈值未按就业结果校准。税务支持参数化中国居民年度综合所得或人工净收入；不自动维护社保政策，不支持跨境税、股权税或自动换汇。支持币种见 `.agents/skills/offer-decision/references/compensation.md`。

脚本不联网、不上传用户材料。Codex 宿主仍使用其模型服务，不承诺推理全部本地运行。私人资料放 `private/` 或 `runs/`，不要提交简历、合同、真实 Offer 或凭证。本仓库只包含通用内容与虚构算例。

## 设计与后续

架构及边界见 `docs/architecture.md`；五个参考项目、许可核验范围和复用取舍见 `docs/reference-projects.md`。本实现不复制上游代码，不依赖这些仓库运行。

后续优先改进政策/汇率版本、证据快照与语义检查、更多真实 JD 样本和跨环境宿主验收。
