"""Monte Carlo uncertainty ranges for v4. Asymmetric: demand better calibrated than productivity."""

UNCERTAIN_PARAMS = {
    # DEMAND — tighter ranges (better calibrated)
    "demand.tech_debt_initial_pct":       (25.0, 55.0),   # HIGH: McKinsey/SO
    "demand.backlog_initial_months":      (3.0,  12.0),   # LOW: proxy data
    "demand.underserved_fraction":        (0.05, 0.50),   # NONE: assumption
    "demand.induced_market_size":         (0.05, 0.40),   # NONE: assumption
    "demand.parkinson_coefficient":       (0.10, 0.70),   # NONE: assumption
    "demand.ai_debt_premium":             (0.10, 0.55),   # MEDIUM: CMU SEI 2024
    "context.annual_cost_reduction_rate": (0.03, 0.28),   # NONE: key driver
    "demand.max_cumulative_expansion":    (0.20, 1.00),   # NONE: Baumol constraint

    # PRODUCTIVITY — wider ranges (weakly calibrated)
    "labor.alpha_experienced":  (-0.40,  0.15),   # MEDIUM: METR RCT
    "labor.alpha_routine":      ( 0.05,  0.60),   # LOW-MEDIUM: non-RCT
    "labor.f_auto":             ( 0.20,  0.60),   # MEDIUM: McKinsey/SO
    "labor.f_verify":           ( 0.05,  0.55),   # NONE
    "labor.g_tools":            ( 0.03,  0.55),   # NONE
    "production.phi":           ( 0.70,  1.00),   # NONE

    # ADOPTION
    "adoption.p":  (0.01, 0.07),   # LOW
    "adoption.q":  (0.20, 0.55),   # LOW
}
