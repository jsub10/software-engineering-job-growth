"""CSV export for v5."""
import csv, os

def export_all(all_results, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    names = list(all_results.keys())
    n = list(all_results.values())[0].n_years

    with open(os.path.join(output_dir, "breakeven_final_year.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario","g_demand","g_productivity","margin","flip_at",
                    "jevons","backlog_mo","debt_pct","emp_index"])
        for nm, run in all_results.items():
            be = run.breakeven[-1]; emp = run.employment_index.get(n, 0)
            w.writerow([nm, f"{be.g_demand:.4f}", f"{be.g_productivity:.4f}",
                        f"{be.margin:.4f}", f"{be.productivity_to_flip:.4f}",
                        "holds" if be.jevons_holds else "fails",
                        f"{be.backlog_level:.1f}", f"{be.debt_level:.1f}", f"{emp:.4f}"])

    with open(os.path.join(output_dir, "stocks_all_years.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario","year","backlog_months","debt_pct","debt_drag",
                    "g_demand","g_productivity","margin","adoption","jevons"])
        for nm, run in all_results.items():
            for be in run.breakeven:
                w.writerow([nm, be.year, f"{be.backlog_level:.2f}", f"{be.debt_level:.2f}",
                            f"{be.debt_productivity_drag:.4f}", f"{be.g_demand:.4f}",
                            f"{be.g_productivity:.4f}", f"{be.margin:.4f}",
                            f"{be.adoption_fraction:.3f}", "holds" if be.jevons_holds else "fails"])
