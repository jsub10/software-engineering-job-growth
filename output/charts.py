"""Chart generation for v5."""
import os

def _plt():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt

def plot_breakeven_fan(all_results, save_path):
    plt = _plt()
    n = len(all_results)
    cols = 2; rows = max(1, (n + 1) // 2)
    fig, axes = plt.subplots(rows, cols, figsize=(14, 4 * rows))
    axes_flat = axes.flatten() if n > 1 else [axes]
    for i, (name, run) in enumerate(all_results.items()):
        if i >= len(axes_flat): break
        ax = axes_flat[i]
        years = [r.year for r in run.breakeven]
        gd = [r.g_demand * 100 for r in run.breakeven]
        gp = [r.g_productivity * 100 for r in run.breakeven]
        gdl = [r.g_demand_low * 100 for r in run.breakeven]
        gdh = [r.g_demand_high * 100 for r in run.breakeven]
        ax.fill_between(years, gdl, gdh, alpha=0.2, color="#2196F3")
        ax.plot(years, gd, color="#2196F3", lw=2, label="Demand growth")
        ax.plot(years, gp, color="#F44336", lw=2, label="Productivity growth")
        ax.axhline(0, color="black", lw=0.5, alpha=0.3)
        for r in run.breakeven:
            ax.axvspan(r.year-0.5, r.year+0.5, alpha=0.12,
                       color="#C8E6C9" if r.jevons_holds else "#FFCDD2")
        ax.set_title(name, fontsize=10, fontweight="bold")
        ax.set_xlabel("Year"); ax.set_ylabel("%/yr"); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    for j in range(i+1, len(axes_flat)): axes_flat[j].set_visible(False)
    fig.suptitle("Break-Even Analysis v5\n(Green=Jevons holds; Red=fails)", fontsize=12, fontweight="bold")
    plt.tight_layout(); os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight"); plt.close()

def plot_stocks(all_results, save_path):
    plt = _plt()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    colors = ["#2196F3","#F44336","#4CAF50","#FF9800","#9C27B0","#00BCD4","#795548","#607D8B"]
    for i, (name, run) in enumerate(all_results.items()):
        years = [r.year for r in run.breakeven]
        ax1.plot(years, [r.backlog_level for r in run.breakeven],
                 color=colors[i % len(colors)], lw=2, marker="o", ms=3, label=name)
        ax2.plot(years, [r.debt_level for r in run.breakeven],
                 color=colors[i % len(colors)], lw=2, marker="s", ms=3, label=name)
    ax1.set_title("Backlog Stock (months)"); ax1.set_xlabel("Year"); ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)
    ax2.set_title("Technical Debt (% of capacity)"); ax2.set_xlabel("Year"); ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)
    fig.suptitle("Dynamic Demand Stocks — v5", fontsize=12, fontweight="bold")
    plt.tight_layout(); os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight"); plt.close()

def plot_employment_index(all_results, save_path):
    plt = _plt()
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#2196F3","#F44336","#4CAF50","#FF9800","#9C27B0","#00BCD4","#795548","#607D8B"]
    for i, (name, run) in enumerate(all_results.items()):
        years = sorted(run.employment_index.keys())
        vals = [run.employment_index[y] for y in years]
        ax.plot(years, vals, label=name, color=colors[i%len(colors)], lw=2, marker="o", ms=4)
    ax.axhline(1.0, color="black", ls="--", lw=1, alpha=0.5, label="baseline")
    ax.set_xlabel("Year"); ax.set_ylabel("Employment Index")
    ax.set_title("Employment Index — SECONDARY OUTPUT\n(lower confidence than break-even)")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3); plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight"); plt.close()

def plot_monte_carlo(results, save_path):
    plt = _plt()
    indices = [r["employment_index"] for r in results]
    margins = [r["margin"] * 100 for r in results]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    mean_i = sum(indices)/len(indices)
    ax1.hist(indices, bins=50, color="#2196F3", edgecolor="white", lw=0.3, alpha=0.8)
    ax1.axvline(1.0, color="red", ls="--", lw=2, label="baseline")
    ax1.axvline(mean_i, color="orange", lw=2, label=f"mean={mean_i:.3f}")
    pct = sum(1 for x in indices if x > 1.0)/len(indices)
    ax1.text(0.98,0.95,f"EmpIdx>1 in\n{pct:.1%}", transform=ax1.transAxes,
             ha="right",va="top",bbox=dict(facecolor="wheat",alpha=0.5))
    ax1.set_xlabel("Employment Index"); ax1.set_ylabel("Count")
    ax1.set_title("Employment Index Distribution"); ax1.legend(); ax1.grid(True, alpha=0.3)
    mean_m = sum(margins)/len(margins)
    ax2.hist(margins, bins=50, color="#4CAF50", edgecolor="white", lw=0.3, alpha=0.8)
    ax2.axvline(0, color="red", ls="--", lw=2, label="break-even")
    ax2.axvline(mean_m, color="orange", lw=2, label=f"mean={mean_m:.1f}%/yr")
    pct_pos = sum(1 for m in margins if m > 0)/len(margins)
    ax2.text(0.98,0.95,f"Jevons holds\n{pct_pos:.1%}", transform=ax2.transAxes,
             ha="right",va="top",bbox=dict(facecolor="wheat",alpha=0.5))
    ax2.set_xlabel("Demand-Productivity Margin (%/yr)")
    ax2.set_title("Break-Even Margin Distribution\n(PRIMARY output)")
    ax2.legend(); ax2.grid(True, alpha=0.3)
    fig.suptitle(f"Monte Carlo Results (n={len(results)})", fontsize=12, fontweight="bold")
    plt.tight_layout(); os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight"); plt.close()

def plot_firm_comparison(firm_data, save_path):
    plt = _plt()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    colors = ["#2196F3","#F44336","#4CAF50","#FF9800"]
    fork_markers = {"HARVEST":"v","REINVEST":"s","EXPAND":"^","IMPROVE":"D"}
    for i, (name, results, fork, debt_traj) in enumerate(firm_data):
        years = [r.year for r in results]
        idxs = [r.headcount_index for r in results]
        m = fork_markers.get(fork, "o")
        c = colors[i % len(colors)]
        ax1.plot(years, idxs, label=f"{name} [{fork}]", color=c, lw=2, marker=m, ms=6)
        ax2.plot(years, debt_traj, label=f"{name}", color=c, lw=2, marker="o", ms=4)
    ax1.axhline(1.0, color="black", ls="--", lw=1, alpha=0.5)
    ax1.set_xlabel("Year"); ax1.set_ylabel("Headcount Index")
    ax1.set_title("Firm Headcount by Management Fork\n(▼=Harvest ■=Reinvest ▲=Expand ◆=Improve)")
    ax1.legend(fontsize=9); ax1.grid(True, alpha=0.3)
    ax2.set_xlabel("Year"); ax2.set_ylabel("Technical Debt (% capacity)")
    ax2.set_title("Firm Technical Debt Evolution\n(AI debt premium drives accumulation)")
    ax2.legend(fontsize=9); ax2.grid(True, alpha=0.3)
    plt.tight_layout(); os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight"); plt.close()
