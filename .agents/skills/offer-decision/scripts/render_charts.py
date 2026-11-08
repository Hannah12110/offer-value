"""Render the three score charts as standalone HTML5 blocks (standard library only)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import read
from score_offer import WEIGHTS, sensitivity

NAVY = "#1A2B4A"
MID = "#758092"
LIGHT = "#BABFC9"
PALE = "#DDE0E4"
ACCENT = "#C8A05A"
RED = "#B3261E"
LABEL = {"industry": "行业", "role": "岗位", "company": "公司", "capital": "职业资本",
         "fit": "目标匹配", "economics": "经济", "location": "城市", "conditions": "条件"}

HEAD = ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="use-iframe" content="true">'
        '<meta name="html-box-height-mode" content="auto">'
        '<meta name="description" content="{desc}"><title>{title}</title>'
        '<style>html,body{margin:0;padding:0;background:#fff;'
        'font-family:-apple-system,"PingFang SC","Helvetica Neue",Arial,sans-serif;color:' + NAVY + ';}'
        '.wrap{width:100%;max-width:100%;box-sizing:border-box;padding:18px 22px 14px;}'
        '.ttl{font-size:15px;font-weight:700;letter-spacing:.3px;}'
        '.sub{font-size:12px;color:' + MID + ';margin-top:4px;line-height:1.5;}'
        '.lg{display:flex;flex-wrap:wrap;gap:16px;margin:10px 0 4px;font-size:11.5px;color:' + MID + ';}'
        '.dot{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:middle;}'
        '.src{font-size:11px;color:#8A929E;border-top:1px solid ' + PALE + ';padding-top:7px;margin-top:8px;line-height:1.5;}'
        '</style></head><body><div class="wrap">')


def head(title, desc):
    return HEAD.replace("{title}", title).replace("{desc}", desc.replace('"', "“"))


def text(x, y, s, size=11.5, fill=NAVY, anchor="start", weight="normal"):
    return ('<text x="' + str(round(x, 1)) + '" y="' + str(round(y, 1)) + '" font-size="' + str(size)
            + '" fill="' + fill + '" text-anchor="' + anchor + '" font-weight="' + weight + '">' + s + '</text>')


def chart_weight(base, thresholds):
    rows = [(k, base["dimensions"][k]["interval"], base["dimensions"][k]["weight"]) for k in WEIGHTS]
    width, height, x0, x1 = 820, 470, 150, 770
    scale = (x1 - x0) / 80.0
    svg = ['<svg width="100%" viewBox="0 0 ' + str(width) + ' ' + str(height) + '" role="img">']
    for value, colour, dash in ((50, MID, "3,3"), (65, RED, "4,3"), (75, LIGHT, "3,3")):
        xx = x0 + value * scale
        svg.append('<line x1="%.1f" y1="58" x2="%.1f" y2="410" stroke="%s" stroke-width="1.2" stroke-dasharray="%s"/>'
                   % (xx, xx, colour, dash))
        svg.append(text(xx, 50, str(value), 10.5, colour, "middle"))
    low_total = high_total = 0.0
    for i, (key, interval, weight) in enumerate(rows):
        y = 70 + i * 36
        lo, hi = interval[0] * weight / 10.0, interval[1] * weight / 10.0
        cum_lo, cum_hi = low_total + lo, low_total + hi
        svg.append(text(142, y + 4, LABEL[key] + " " + key + "（权重" + str(weight) + "）", 11.5, NAVY, "end"))
        svg.append('<rect x="' + str(x0) + '" y="' + str(y - 11) + '" width="%.1f" height="22" fill="%s"/>'
                   % (cum_lo * scale, NAVY))
        svg.append('<rect x="%.1f" y="%d" width="%.1f" height="22" fill="%s"/>'
                   % (x0 + cum_lo * scale, y - 11, (cum_hi - cum_lo) * scale, LIGHT))
        svg.append(text(x0 + cum_hi * scale + 6, y + 4, "+%.2f～%.2f" % (lo, hi), 11, MID))
        low_total, high_total = cum_lo, cum_hi
    y = 70 + len(rows) * 36 + 14
    svg.append('<line x1="' + str(x0) + '" y1="' + str(y - 24) + '" x2="' + str(x1) + '" y2="' + str(y - 24) + '" stroke="' + PALE + '"/>')
    svg.append(text(142, y + 4, "合计（0–100）", 12, NAVY, "end", "700"))
    svg.append('<rect x="' + str(x0) + '" y="' + str(y - 13) + '" width="%.1f" height="26" fill="%s"/>' % (low_total * scale, NAVY))
    svg.append('<rect x="%.1f" y="%d" width="%.1f" height="26" fill="%s"/>'
               % (x0 + low_total * scale, y - 13, (high_total - low_total) * scale, LIGHT))
    svg.append(text(x0 + high_total * scale + 6, y + 4, "%.1f–%.1f" % (low_total, high_total), 12, RED, "start", "700"))
    ay = y + 30
    svg.append('<line x1="' + str(x0) + '" y1="' + str(ay) + '" x2="' + str(x1) + '" y2="' + str(ay) + '" stroke="' + MID + '"/>')
    for tick in (0, 20, 40, 50, 60, 65, 70, 80):
        xx = x0 + tick * scale
        svg.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s"/>' % (xx, ay, xx, ay + 5, MID))
        svg.append(text(xx, ay + 18, str(tick), 10.5, MID, "middle"))
    svg.append(text(x0, ay + 36, "上限到 65 仍差 %.1f 分：这是“证据不足”，不是“分数略低”的形状" % (65 - high_total), 11, RED))
    svg.append('</svg>')
    html = head("八维加权贡献：分数从哪来、差在哪",
                "把每维“分数×权重”顺序叠加到 0–100 标尺，深色为下界、浅色为上界，红色虚线为 65 分“可以有条件地签”门槛。")
    html += '<div class="ttl">八维贡献叠加：总分由哪些维度垒起来</div>'
    html += '<div class="sub">横轴为 0–100 加权总分；每一段长度＝该维“区间分数×权重”，从下界顺序累加。灰色虚线 50 分（低于此建议放弃），红色虚线 65 分（可以有条件地签），浅色虚线 75 分（可以签且须书面）。</div>'
    html += ('<div class="lg"><span><i class="dot" style="background:' + NAVY + '"></i>下界贡献</span>'
             '<span><i class="dot" style="background:' + LIGHT + '"></i>上界增量</span>'
             '<span><i class="dot" style="background:' + RED + '"></i>65 分门槛</span></div>')
    html += ''.join(svg)
    html += '<div class="src">来源：评分规则 v1 八维权重；贡献＝区间分数×权重÷10，与第十节区间一致。' + thresholds + '</div></div></body></html>'
    return html


def chart_coverage(base):
    cov = [(k, base["dimensions"][k]["weight"], base["dimensions"][k]["coverage"]) for k in WEIGHTS]
    cov.sort(key=lambda r: (-r[2], -r[1]))
    width, height, x0, x1 = 820, 372, 216, 690
    scale = (x1 - x0) / 100.0
    svg = ['<svg width="100%" viewBox="0 0 ' + str(width) + ' ' + str(height) + '" role="img">']
    for i, (key, weight, coverage) in enumerate(cov):
        y = 64 + i * 34
        pct = int(round(coverage * 100))
        colour = NAVY if pct >= 100 else (ACCENT if pct >= 67 else RED)
        svg.append(text(206, y + 4, LABEL[key] + " " + key + "（权重" + str(weight) + "）", 11.5, NAVY, "end"))
        svg.append('<rect x="' + str(x0) + '" y="' + str(y - 11) + '" width="' + str(x1 - x0) + '" height="22" fill="#F5F6F8"/>')
        svg.append('<rect x="' + str(x0) + '" y="' + str(y - 11) + '" width="%.1f" height="22" fill="%s"/>' % (pct * scale, colour))
        svg.append(text(x0 + pct * scale + 8, y + 4, str(pct) + "%", 11.5, colour, "start", "700"))
    svg.append('<line x1="' + str(x0) + '" y1="' + str(height - 48) + '" x2="' + str(x1) + '" y2="' + str(height - 48) + '" stroke="' + MID + '"/>')
    for tick in (0, 33, 67, 100):
        svg.append(text(x0 + tick * scale, height - 30, str(tick) + "%", 10.5, MID, "middle"))
    thin = sum(w for k, w, c in cov if c < 2 / 3 - 1e-9)
    note = ("加权覆盖率 %.0f%%：33%% 的三维合计权重 %d，是结论最依赖、证据最薄的部分" % (base["coverage"] * 100, thin)
            if thin else "加权覆盖率 %.0f%%：八维覆盖均达 2/3 以上，分歧集中在分数区间而非证据缺口" % (base["coverage"] * 100))
    svg.append(text(x0, height - 10, note, 11, RED))
    svg.append('</svg>')
    html = head("覆盖度：哪些维度其实没证据",
                "八维覆盖度条形图：100% 表示三项子指标均有合格证据，33% 表示仅一项达标；用于解释分数为何不能直接当结论。")
    html += '<div class="ttl">覆盖度：哪些维度的分没有证据支撑</div>'
    html += '<div class="sub">覆盖度＝该维权重×（有合格证据支持的非空子项数／预设三个子项）。企业自报宣传只算 self_reported（企业自报），不计入合格证据。</div>'
    html += ('<div class="lg"><span><i class="dot" style="background:' + NAVY + '"></i>100%（3/3 子项有据）</span>'
             '<span><i class="dot" style="background:' + ACCENT + '"></i>67%（2/3）</span>'
             '<span><i class="dot" style="background:' + RED + '"></i>33%（1/3，判断最不可靠）</span></div>')
    html += ''.join(svg)
    html += '<div class="src">来源：证据规则与评分规则 v1；证据编号见证据台账。加权覆盖率与简单子项计数不同，不要混用。</div></div></body></html>'
    return html


def chart_sensitivity(result):
    base = result["base"]
    variants = [v for v in result["variants"] if "weight" in v["variable"]]
    rows = [("基准权重", base["score_interval"], NAVY)]
    rows += [("role" + v["variable"].split("weight")[1] + "／econ 反向", v["score_interval"], MID if i == 0 else LIGHT)
             for i, v in enumerate(variants[:2])]
    width, height, x0, x1 = 820, 330, 196, 720
    scale = (x1 - x0) / 80.0
    svg = ['<svg width="100%" viewBox="0 0 ' + str(width) + ' ' + str(height) + '" role="img">']
    for value, colour, dash in ((50, MID, "3,3"), (65, RED, "4,3")):
        xx = x0 + value * scale
        svg.append('<line x1="%.1f" y1="54" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.2" stroke-dasharray="%s"/>'
                   % (xx, xx, height - 60, colour, dash))
        svg.append(text(xx, 46, str(value), 10.5, colour, "middle"))
    for i, (name, interval, colour) in enumerate(rows):
        y = 96 + i * 52
        svg.append(text(190, y + 4, name, 11.5, NAVY, "end"))
        svg.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="7" stroke-linecap="round"/>'
                   % (x0 + interval[0] * scale, y, x0 + interval[1] * scale, y, colour))
        svg.append(text(x0 + interval[1] * scale + 10, y + 4, "%.1f–%.1f" % (interval[0], interval[1]), 11.5,
                        MID if colour == LIGHT else colour, "start", "700"))
    svg.append('<line x1="' + str(x0) + '" y1="' + str(height - 60) + '" x2="' + str(x1) + '" y2="' + str(height - 60) + '" stroke="' + MID + '"/>')
    for tick in (40, 50, 60, 65, 70, 80):
        svg.append(text(x0 + tick * scale, height - 42, str(tick), 10.5, MID, "middle"))
    svg.append(text(x0, height - 14, "三组权重全部落在 50–59：状态一次未翻转，结论不是某组权重凑出来的" if not result["decision_changes"]
                    else "权重变动后状态发生翻转：结论依赖权重假设，需在正文说明", 11, RED))
    svg.append('</svg>')
    html = head("敏感性：换一组权重，结论会不会变",
                "role 与 economics 权重各正负 5 个百分点后重算加权区间：结果是否仍落在 50-59、是否触碰 65 门槛或跌破 50。")
    html += '<div class="ttl">敏感性：换权重以后，落点动多少</div>'
    html += '<div class="sub">横轴 0–100；role／economics 权重互调 ±5 个百分点，其余维度等比缩放。结论若靠某一组权重才成立，就不是可复现的判断。</div>'
    html += ('<div class="lg"><span><i class="dot" style="background:' + NAVY + '"></i>基准区间</span>'
             '<span><i class="dot" style="background:' + MID + '"></i>首个权重扰动</span>'
             '<span><i class="dot" style="background:' + LIGHT + '"></i>反向权重扰动</span></div>')
    html += ''.join(svg)
    html += '<div class="src">来源：评分规则 v1 敏感性规则；权重变动后总分＝Σ（区间分数×权重）÷10，口径与基准一致。</div></div></body></html>'
    return html


def render_charts(data, outdir):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    analysis = data.get("assessment") if isinstance(data.get("assessment"), dict) else data
    result = sensitivity(analysis)
    offer = data.get("offer", {})
    tag = "／".join(str(offer.get(k)) for k in ("company", "role", "city") if offer.get(k)) or "研究对象"
    thresholds = "研究对象：" + tag + "；证据截止日：" + str(analysis.get("research_as_of") or "UNKNOWN") + "。"
    target = Path(outdir)
    if target.exists():
        raise ValueError("output directory exists; choose a new one")
    target.mkdir(parents=True)
    files = {"chart_weight.html": chart_weight(result["base"], thresholds),
             "chart_coverage.html": chart_coverage(result["base"]),
             "chart_sensitivity.html": chart_sensitivity(result)}
    for name, content in files.items():
        (target / name).write_text(content, encoding="utf-8")
    return {"outdir": str(target), "files": sorted(files), "decision": result["base"]["decision"],
            "coverage": result["base"]["coverage"], "score_interval": result["base"]["score_interval"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(render_charts(read(args.input), args.outdir), ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        sys.exit(2, "Invalid input: %s\n" % exc)
