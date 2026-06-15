"""Detailed, human-readable Monte Carlo reports (market and firm).

Every Monte Carlo run writes a timestamped markdown report to output/reports/.
Each report explains the results in plain language and ends with an appendix
that reproduces the parameter-range table using the ACTUAL ranges used in
that run (read back from the same config the run loaded).
"""
import math
import os
from datetime import datetime

import yaml

from market_model.core.monte_carlo import (
    _pct, load_mc_ranges, DEFAULT_MC_RANGES_PATH,
)

REPORT_DIR = "output/reports"

CAVEAT = (
    "> **How to read this.** These are distributions over model outputs given "
    "parameter uncertainty — **not** probability forecasts of the future. A wide "
    "range reflects how little we know about the inputs, not random chance. "
    "Employment figures are an index relative to today: `1.0` = today's level, "
    "`1.5` = 50% more, `0.7` = 30% fewer."
)


def _stamp():
    """Return (filename_stamp, human_readable) for the current local time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d_%H%M%S"), now.strftime("%Y-%m-%d %H:%M:%S")


def _pct_row(label, vals, fmt="{:.3f}"):
    cells = " | ".join(fmt.format(_pct(vals, p)) for p in (10, 25, 50, 75, 90))
    return f"| {label} | {cells} |"


# ─────────────────────────────────────────────────────────────────────────────
# APPENDIX — actual ranges used
# ─────────────────────────────────────────────────────────────────────────────

def _ranges_appendix(ranges_path, market_ranges, firm_ranges, firm_categorical):
    """Reproduce the monte_carlo_ranges.md tables with the ranges actually used."""
    spec = {}
    if ranges_path and os.path.exists(ranges_path):
        with open(ranges_path) as f:
            spec = yaml.safe_load(f) or {}
    market_spec = spec.get("market", {}) or {}
    firm_spec = spec.get("firm", {}) or {}
    cat_spec = spec.get("firm_categorical", {}) or {}

    def meta(section, name, key):
        entry = section.get(name) or {}
        v = entry.get(key)
        return "—" if v is None else v

    lines = [
        "## Appendix — Parameter ranges used in this run",
        "",
        f"Source: `{ranges_path}`"
        + ("" if (ranges_path and os.path.exists(ranges_path))
           else " *(file not found — built-in defaults were used)*"),
        "",
        "These are the exact sampling bands drawn from for this run. "
        "**MC low / MC high** is the uniform band each variable was drawn from; "
        "**Hard min / Hard max** are the absolute bounds (informational).",
        "",
        "### Market model",
        "",
        "| Variable | Description | Hard min | Hard max | MC low | MC high |",
        "|---|---|---|---|---|---|",
    ]
    for name, (lo, hi) in market_ranges.items():
        lines.append(
            f"| `{name}` | {meta(market_spec, name, 'description')} | "
            f"{meta(market_spec, name, 'hard_min')} | {meta(market_spec, name, 'hard_max')} | "
            f"{lo} | {hi} |"
        )

    lines += [
        "",
        "### Firm model (continuous)",
        "",
        "| Variable | Description | Hard min | Hard max | MC low | MC high |",
        "|---|---|---|---|---|---|",
    ]
    for name, (lo, hi) in firm_ranges.items():
        lines.append(
            f"| `{name}` | {meta(firm_spec, name, 'description')} | "
            f"{meta(firm_spec, name, 'hard_min')} | {meta(firm_spec, name, 'hard_max')} | "
            f"{lo} | {hi} |"
        )

    lines += [
        "",
        "### Firm model (categorical)",
        "",
        "| Variable | Description | Categories (probability) |",
        "|---|---|---|",
    ]
    for name, dist in firm_categorical.items():
        cats = ", ".join(f"{k} ({v})" for k, v in dist.items())
        lines.append(f"| `{name}` | {meta(cat_spec, name, 'description')} | {cats} |")

    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# MARKET REPORT
# ─────────────────────────────────────────────────────────────────────────────

def write_market_mc_report(results, n_years, n_iterations, seed=42,
                           params_label="config/market_params.yaml",
                           ranges_path=DEFAULT_MC_RANGES_PATH,
                           out_dir=REPORT_DIR):
    """Write a detailed market Monte Carlo report. Returns the file path."""
    market_ranges, firm_ranges, firm_categorical = load_mc_ranges(ranges_path)
    stamp, human = _stamp()
    n = len(results)
    if n == 0:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"market_monte_carlo_{stamp}.md")
        with open(path, "w") as f:
            f.write(f"# Market Monte Carlo Report\n\nGenerated {human}. No results.\n")
        return path

    peaks = [r.peak_employment for r in results]
    peak_yrs = [r.peak_year for r in results]
    beys = [r.break_even_year for r in results if r.break_even_year is not None]
    bey_nevers = sum(1 for r in results if r.break_even_year is None)
    finals = [r.final_employment for r in results]
    margins = [r.margin_yr10 * 100 for r in results]
    g_demands = [r.g_demand_yr10 * 100 for r in results]
    g_prods = [r.g_productivity_yr10 * 100 for r in results]

    pct_above_1 = sum(1 for v in finals if v > 1.0) / n
    pct_above_11 = sum(1 for v in finals if v > 1.1) / n
    pct_below_09 = sum(1 for v in finals if v < 0.9) / n
    pct_below_07 = sum(1 for v in finals if v < 0.7) / n
    pct_jevons = sum(1 for m in margins if m > 0) / n

    med_final = _pct(finals, 50)
    med_margin = _pct(margins, 50)

    # Parameter influence (Pearson correlation with final employment)
    correlations = []
    if results[0].params_drawn:
        for param in results[0].params_drawn.keys():
            vals = [r.params_drawn.get(param, 0) for r in results]
            mv, mo = sum(vals) / n, sum(finals) / n
            cov = sum((vals[i] - mv) * (finals[i] - mo) for i in range(n))
            sv = math.sqrt(sum((v - mv) ** 2 for v in vals))
            so = math.sqrt(sum((o - mo) ** 2 for o in finals))
            if sv > 0 and so > 0:
                correlations.append((param, cov / (sv * so)))
        correlations.sort(key=lambda x: abs(x[1]), reverse=True)

    direction = "leans toward growth" if med_final >= 1.0 else "leans toward contraction"
    margin_story = (
        "demand is still outrunning productivity at the end of the horizon"
        if med_margin > 0 else
        "productivity has pulled ahead of demand by the end of the horizon"
    )

    L = []
    L.append("# Market Monte Carlo Report")
    L.append("")
    L.append(f"- **Generated:** {human}")
    L.append(f"- **Iterations:** {n_iterations:,} ({n:,} completed successfully)")
    L.append(f"- **Simulation horizon:** {n_years} years")
    L.append(f"- **Base parameters:** `{params_label}`")
    L.append(f"- **Random seed:** {seed}")
    L.append("")
    L.append(CAVEAT)
    L.append("")
    L.append("## 1. Primary outputs")
    L.append("")
    L.append("Percentiles across all runs (P50 = median; P10–P90 = middle 80%).")
    L.append("")
    L.append("| Metric | P10 | P25 | P50 | P75 | P90 |")
    L.append("|---|---|---|---|---|---|")
    L.append(_pct_row("Peak employment index", peaks))
    L.append(_pct_row("Peak year", peak_yrs, "{:.0f}"))
    if beys:
        L.append(_pct_row("Break-even year (when it declines)", beys, "{:.0f}"))
    L.append(_pct_row(f"Final employment (year {n_years})", finals))
    L.append("")
    L.append(f"- **Employment never declines in {bey_nevers / n:.1%} of runs.**")
    L.append("")
    L.append(f"In the typical (median) run, employment {direction}, ending at "
             f"**{med_final:.3f}×** today's level.")
    L.append("")
    L.append(f"## 2. The break-even margin (year {n_years})")
    L.append("")
    L.append("Employment direction is a race between **demand growth** (more software "
             "wanted) and **productivity growth** (each engineer does more). The "
             "difference is the **margin**.")
    L.append("")
    L.append("| Quantity | P10 | P25 | P50 | P75 | P90 |")
    L.append("|---|---|---|---|---|---|")
    L.append(_pct_row("Demand growth (%/yr)", g_demands, "{:.1f}"))
    L.append(_pct_row("Productivity growth (%/yr)", g_prods, "{:.1f}"))
    L.append(_pct_row("Margin (Demand − Productivity, %/yr)", margins, "{:+.1f}"))
    L.append("")
    L.append(f"- **Jevons paradox holds (demand outruns productivity) in "
             f"{pct_jevons:.1%} of runs.** In the median run, {margin_story} "
             f"(margin {med_margin:+.1f}%/yr).")
    L.append("")
    L.append("## 3. Verdicts — how often does each outcome occur?")
    L.append("")
    L.append(f"| Outcome at year {n_years} | Share of runs |")
    L.append("|---|---|")
    L.append(f"| Final employment > baseline (1.0×) — net job growth | **{pct_above_1:.1%}** |")
    L.append(f"| Final employment > 1.1× — clear expansion | {pct_above_11:.1%} |")
    L.append(f"| Final employment < 0.9× — clear contraction | {pct_below_09:.1%} |")
    L.append(f"| Final employment < 0.7× — severe contraction | {pct_below_07:.1%} |")
    L.append("")
    if correlations:
        L.append("## 4. What drives the outcome")
        L.append("")
        L.append("Pearson correlation between each drawn parameter and final employment "
                 "(sign = direction, magnitude = strength):")
        L.append("")
        L.append("| Parameter | Correlation | Higher values → |")
        L.append("|---|---|---|")
        for param, corr in correlations[:8]:
            arrow = "more engineers" if corr > 0 else "fewer engineers"
            L.append(f"| `{param}` | {corr:+.3f} | {arrow} |")
        L.append("")
    L.append("## 5. Bottom line")
    L.append("")
    L.append(f"- The median decade {direction} (final {med_final:.3f}×); "
             f"{pct_above_1:.0%} of runs end above today's baseline and "
             f"{pct_below_07:.0%} fall below 0.7×.")
    L.append(f"- Demand-vs-productivity is { 'roughly balanced' if 45 <= pct_jevons*100 <= 55 else ('demand-led' if pct_jevons > 0.5 else 'productivity-led') } "
             f"(Jevons holds in {pct_jevons:.0%} of runs).")
    if correlations:
        top = correlations[0]
        L.append(f"- The strongest single driver is `{top[0]}` (r = {top[1]:+.2f}).")
    L.append("- Treat the spread as a map of our ignorance, not a probability of the future.")
    L.append("")
    L.append(_ranges_appendix(ranges_path, market_ranges, firm_ranges, firm_categorical))

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"market_monte_carlo_{stamp}.md")
    with open(path, "w") as f:
        f.write("\n".join(L))
    return path


# ─────────────────────────────────────────────────────────────────────────────
# FIRM REPORT
# ─────────────────────────────────────────────────────────────────────────────

def write_firm_mc_report(results, n_years, n_iterations, profile_name="",
                         seed=42, ranges_path=DEFAULT_MC_RANGES_PATH,
                         out_dir=REPORT_DIR):
    """Write a detailed firm Monte Carlo report. Returns the file path."""
    market_ranges, firm_ranges, firm_categorical = load_mc_ranges(ranges_path)
    stamp, human = _stamp()
    n = len(results)
    if n == 0:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"firm_monte_carlo_{stamp}.md")
        with open(path, "w") as f:
            f.write(f"# Firm Monte Carlo Report\n\nGenerated {human}. No results.\n")
        return path

    peaks = [r.peak_employment for r in results]
    finals = [r.final_employment for r in results]
    juniors = [r.final_junior for r in results]
    seniors = [r.final_senior for r in results]
    market_finals = [r.market_final for r in results]
    gaps = [r.final_senior - r.final_junior for r in results]
    beys = [r.break_even_year for r in results if r.break_even_year is not None]
    bey_nevers = sum(1 for r in results if r.break_even_year is None)

    pct_above = sum(1 for v in finals if v > 1.0) / n
    pct_expand = sum(1 for v in finals if v > 1.30) / n
    pct_harvest = sum(1 for v in finals if v < 0.85) / n
    pct_senior_gt_junior = sum(1 for r in results if r.final_senior > r.final_junior) / n

    fork_counts = {}
    for r in results:
        fork_counts[r.fork_primary] = fork_counts.get(r.fork_primary, 0) + 1

    med_final = _pct(finals, 50)
    direction = "leans toward growth" if med_final >= 1.0 else "leans toward contraction"

    L = []
    L.append("# Firm Monte Carlo Report")
    L.append("")
    L.append(f"- **Generated:** {human}")
    if profile_name:
        L.append(f"- **Firm profile:** {profile_name}")
    L.append(f"- **Iterations:** {n_iterations:,} ({n:,} completed successfully)")
    L.append(f"- **Simulation horizon:** {n_years} years")
    L.append(f"- **Random seed:** {seed}")
    L.append("")
    L.append(CAVEAT)
    L.append("")
    L.append("This run varies **both** the market parameters and the firm's own "
             "characteristics, so the spread reflects uncertainty in what the firm "
             "looks like *and* what the market does.")
    L.append("")
    L.append("## 1. Headcount index distribution")
    L.append("")
    L.append("| Metric | P10 | P25 | P50 | P75 | P90 |")
    L.append("|---|---|---|---|---|---|")
    L.append(_pct_row("Peak headcount (firm)", peaks))
    L.append(_pct_row(f"Final headcount, year {n_years} (firm)", finals))
    L.append(_pct_row("Final junior index", juniors))
    L.append(_pct_row("Final senior index", seniors))
    L.append(_pct_row("Final market index (reference)", market_finals))
    if beys:
        L.append(_pct_row("Break-even year (when it declines)", beys, "{:.0f}"))
    L.append("")
    L.append(f"- **Headcount never declines in {bey_nevers / n:.1%} of runs.**")
    L.append(f"- The median run {direction}, ending at **{med_final:.3f}×** today's headcount.")
    L.append("")
    L.append("## 2. Verdicts")
    L.append("")
    L.append("| Outcome | Share of runs |")
    L.append("|---|---|")
    L.append(f"| Final headcount > baseline (1.0×) | **{pct_above:.1%}** |")
    L.append(f"| Final headcount > 1.30× (expand) | {pct_expand:.1%} |")
    L.append(f"| Final headcount < 0.85× (harvest) | {pct_harvest:.1%} |")
    L.append(f"| Senior index > junior index | {pct_senior_gt_junior:.1%} |")
    L.append("")
    L.append("## 3. Management fork distribution")
    L.append("")
    L.append("Which strategy the firm's leadership defaults to across runs:")
    L.append("")
    L.append("| Fork | Share of runs |")
    L.append("|---|---|")
    for fork in ["HARVEST", "REINVEST", "EXPAND", "IMPROVE"]:
        L.append(f"| {fork} | {fork_counts.get(fork, 0) / n:.1%} |")
    L.append("")
    L.append("## 4. Senior vs. junior gap")
    L.append("")
    L.append("Positive gap = senior employment rises relative to junior (the widening "
             "skill pyramid).")
    L.append("")
    L.append("| Metric | P10 | P25 | P50 | P75 | P90 |")
    L.append("|---|---|---|---|---|---|")
    L.append(_pct_row("Senior − Junior gap", gaps))
    L.append("")
    L.append(f"- Senior outperforms junior in **{pct_senior_gt_junior:.1%}** of runs.")
    L.append("")
    L.append("## 5. Bottom line")
    L.append("")
    L.append(f"- The median firm {direction} (final {med_final:.3f}×); "
             f"{pct_above:.0%} of runs end above today's headcount.")
    top_fork = max(fork_counts, key=fork_counts.get)
    L.append(f"- The most common management response is **{top_fork}** "
             f"({fork_counts[top_fork] / n:.0%} of runs).")
    L.append(f"- The senior tier beats the junior tier in {pct_senior_gt_junior:.0%} of "
             f"runs — the skill-pyramid widening shows up at firm level too.")
    L.append("")
    L.append(_ranges_appendix(ranges_path, market_ranges, firm_ranges, firm_categorical))

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"firm_monte_carlo_{stamp}.md")
    with open(path, "w") as f:
        f.write("\n".join(L))
    return path
