"""Markdown report for v5 (scenario break-even summary)."""
import os
from datetime import date

def generate_report(all_results, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    n = list(all_results.values())[0].n_years
    lines = [
        "# Agentic Coding Labor Model v5 — Report",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Key Model Corrections (carried from v4)",
        "- Backlog: dynamic stock with Parkinson's Law inflow (never exhausts to zero)",
        "- Technical debt: accumulates with AI premium; feeds back into productivity",
        "- Underserved markets: deplete as penetrated; not infinite",
        "- Induced demand: finite total size via Bass diffusion",
        "- Aggregate demand ceiling: logistic saturation at 3× baseline",
        "- Firm model: revenue saturation, 35% absorption cap, IMPROVE branch",
        "",
        f"## Break-Even Analysis (Year {n}, final year)",
        "",
        "| Scenario | Demand | Prodctvy | Margin | Flip@ | Jevons | Backlog | Debt% | EmpIdx |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for nm, run in all_results.items():
        be = run.breakeven[-1]; emp = run.employment_index.get(n, 1.0)
        jevons = "**HOLDS**" if be.jevons_holds else "FAILS"
        lines.append(f"| {nm} | {be.g_demand:.2%} | {be.g_productivity:.2%} | "
                     f"{be.margin:+.2%} | >{be.productivity_to_flip:.2%} | {jevons} | "
                     f"{be.backlog_level:.1f}mo | {be.debt_level:.1f}% | {emp:.3f} |")
    lines += ["", f"> Backlog and Debt columns show stock levels at year {n} (final year).",
              "> EmpIdx is secondary output — lower confidence than break-even margin.", ""]
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
