"""Tests for Agentic Labor Model v4."""
import pytest, yaml, copy, math


def base_params():
    with open("config/market_params.yaml") as f:
        return yaml.safe_load(f)


# ── Backlog Stock Tests ──────────────────────────────────────────────────────

class TestBacklogStock:
    def test_backlog_never_below_floor(self):
        from market_model.core.demand_stocks import BacklogParams, BacklogStock
        p = BacklogParams(initial_months=6.0, floor_months=2.0)
        stock = BacklogStock(p)
        for _ in range(15):
            stock.step(productivity_gain=0.50, adoption_fraction=0.80)
        assert stock.B >= p.floor_months

    def test_high_productivity_increases_outflow(self):
        from market_model.core.demand_stocks import BacklogParams, BacklogStock
        # Large initial stock, modest floor: floor constraint doesn't bind
        # High productivity should clear more per year than low productivity
        p = BacklogParams(initial_months=100.0, floor_months=2.0,
                          baseline_inflow_rate=0.0, parkinson_coefficient=0.0,
                          agentic_expansion_rate=0.0, base_completion_rate=0.1)
        s_high = BacklogStock(p); s_low = BacklogStock(p)
        r_high = s_high.step(0.50, 0.50)
        r_low = s_low.step(0.05, 0.10)
        assert r_high["outflow"] > r_low["outflow"], (
            f"High productivity ({r_high['outflow']:.1f}) should clear more than "
            f"low productivity ({r_low['outflow']:.1f})"
        )

    def test_parkinson_partially_offsets_productivity(self):
        from market_model.core.demand_stocks import BacklogParams, BacklogStock
        p_no_park = BacklogParams(parkinson_coefficient=0.0)
        p_high_park = BacklogParams(parkinson_coefficient=0.80)
        s_no = BacklogStock(p_no_park); s_hi = BacklogStock(p_high_park)
        for _ in range(5):
            s_no.step(0.30, 0.50)
            s_hi.step(0.30, 0.50)
        assert s_hi.B > s_no.B

    def test_demand_signal_positive_when_backlog_above_equilibrium(self):
        from market_model.core.demand_stocks import BacklogParams, BacklogStock
        p = BacklogParams(initial_months=12.0, floor_months=2.0)
        stock = BacklogStock(p)
        result = stock.step(0.05, 0.10)
        assert result["demand_signal"] >= 0


# ── Tech Debt Stock Tests ────────────────────────────────────────────────────

class TestTechDebtStock:
    def test_debt_never_below_structural_floor(self):
        from market_model.core.demand_stocks import TechDebtParams, TechDebtStock
        p = TechDebtParams(initial_pct=40.0, floor_fraction=0.15)
        stock = TechDebtStock(p)
        for _ in range(15):
            stock.step(0.20, 0.80)
        assert stock.TD >= p.initial_pct * p.floor_fraction

    def test_ai_premium_increases_debt_accumulation(self):
        from market_model.core.demand_stocks import TechDebtParams, TechDebtStock
        p_low = TechDebtParams(ai_debt_premium=0.0)
        p_high = TechDebtParams(ai_debt_premium=0.60)
        s_low = TechDebtStock(p_low); s_high = TechDebtStock(p_high)
        for _ in range(5):
            s_low.step(0.20, 0.70)
            s_high.step(0.20, 0.70)
        assert s_high.TD > s_low.TD

    def test_improve_strategy_reduces_debt_faster(self):
        from market_model.core.demand_stocks import TechDebtParams, TechDebtStock
        p = TechDebtParams(initial_pct=50.0)
        s_normal = TechDebtStock(p); s_improve = TechDebtStock(p)
        for _ in range(5):
            s_normal.step(0.10, 0.40, debt_focus_override=None)
            s_improve.step(0.10, 0.40, debt_focus_override=0.60)
        assert s_improve.TD < s_normal.TD

    def test_productivity_drag_increases_with_debt(self):
        from market_model.core.demand_stocks import TechDebtParams, TechDebtStock
        p_low = TechDebtParams(initial_pct=10.0)
        p_high = TechDebtParams(initial_pct=60.0)
        r_low = TechDebtStock(p_low).step(0.1, 0.3)
        r_high = TechDebtStock(p_high).step(0.1, 0.3)
        assert r_high["productivity_drag"] > r_low["productivity_drag"]


# ── Saturating Demand Tests ──────────────────────────────────────────────────

class TestSaturatingDemand:
    def test_underserved_depletes_over_time(self):
        from market_model.core.demand_saturation import UnderservedParams, UnderservedMarketStock
        p = UnderservedParams(initial_fraction=0.25, cost_threshold=0.10, floor_fraction=0.0)
        stock = UnderservedMarketStock(p)
        for _ in range(20):
            stock.step(cumulative_cost_reduction=0.50)
        assert stock.U < p.initial_fraction * 0.5  # depleted significantly

    def test_underserved_does_not_activate_before_threshold(self):
        from market_model.core.demand_saturation import UnderservedParams, UnderservedMarketStock
        p = UnderservedParams(cost_threshold=0.50)
        stock = UnderservedMarketStock(p)
        result = stock.step(cumulative_cost_reduction=0.30)
        assert result["demand_signal"] == 0.0
        assert not result["unlocked"]

    def test_induced_demand_bounded(self):
        from market_model.core.demand_saturation import InducedDemandParams, InducedDemandStock
        p = InducedDemandParams(total_market_size=0.20, start_year=1)
        stock = InducedDemandStock(p)
        total = sum(stock.step(y)["demand_signal"] for y in range(1, 31))
        assert total <= p.total_market_size + 0.01

    def test_ceiling_is_monotone(self):
        from market_model.core.demand_saturation import apply_aggregate_ceiling
        vals = [apply_aggregate_ceiling(d, D_max=3.0) for d in [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0]]
        for i in range(len(vals) - 1):
            assert vals[i+1] >= vals[i], f"Ceiling not monotone at index {i}"

    def test_ceiling_never_exceeds_D_max(self):
        from market_model.core.demand_saturation import apply_aggregate_ceiling
        for D_raw in [1.0, 2.0, 5.0, 10.0, 100.0]:
            assert apply_aggregate_ceiling(D_raw, D_max=3.0) <= 3.01

    def test_ceiling_passes_through_below_D_max(self):
        from market_model.core.demand_saturation import apply_aggregate_ceiling
        for D_raw in [1.0, 1.2, 1.5]:
            D_sat = apply_aggregate_ceiling(D_raw, D_max=3.0)
            assert abs(D_sat - D_raw) < 0.15, f"Ceiling too aggressive at D_raw={D_raw}"


# ── Market Model Integration Tests ───────────────────────────────────────────

class TestMarketModel:
    def test_base_run_completes(self):
        from market_model.core.model import MarketModel
        result = MarketModel(base_params()).run()
        assert len(result.breakeven) == 10

    def test_backlog_never_zero(self):
        from market_model.core.model import MarketModel
        result = MarketModel(base_params()).run()
        for be in result.breakeven:
            assert be.backlog_level > 0

    def test_debt_never_zero(self):
        from market_model.core.model import MarketModel
        result = MarketModel(base_params()).run()
        for be in result.breakeven:
            assert be.debt_level > 0

    def test_high_parkinson_raises_backlog(self):
        from market_model.core.model import MarketModel
        p_low = base_params(); p_low["demand"]["parkinson_coefficient"] = 0.05
        p_high = base_params(); p_high["demand"]["parkinson_coefficient"] = 0.75
        r_low = MarketModel(p_low).run(); r_high = MarketModel(p_high).run()
        assert r_high.breakeven[-1].backlog_level > r_low.breakeven[-1].backlog_level

    def test_high_ai_premium_raises_debt(self):
        from market_model.core.model import MarketModel
        p_low = base_params(); p_low["demand"]["ai_debt_premium"] = 0.0
        p_high = base_params(); p_high["demand"]["ai_debt_premium"] = 0.70
        r_low = MarketModel(p_low).run(); r_high = MarketModel(p_high).run()
        assert r_high.breakeven[-1].debt_level > r_low.breakeven[-1].debt_level

    def test_higher_g_tools_reduces_employment(self):
        from market_model.core.model import MarketModel
        p_low = base_params(); p_low["labor"]["g_tools"] = 0.03
        p_low["market"]["consumer_capture_rate"] = {s: 0.0 for s in ["consumer","smb","enterprise","regulated"]}
        p_high = copy.deepcopy(p_low); p_high["labor"]["g_tools"] = 0.50
        r_low = MarketModel(p_low).run(); r_high = MarketModel(p_high).run()
        assert r_high.employment_index[10] < r_low.employment_index[10]

    def test_metr_scenario_holds_jevons(self):
        from market_model.core.scenario_runner import run_scenario
        result = run_scenario("metr_generalizes")
        assert result.breakeven[-1].jevons_holds

    def test_employment_index_positive(self):
        from market_model.core.model import MarketModel
        result = MarketModel(base_params()).run()
        for yr, idx in result.employment_index.items():
            assert idx > 0


# ── Firm Model Tests ─────────────────────────────────────────────────────────

class TestFirmModel:
    def _market(self):
        from market_model.core.model import MarketModel
        return MarketModel(base_params()).run(), base_params()

    def test_harvest_fork_for_cost_center(self):
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        p = FirmProfile(software_is_core_product=False, competitive_intensity="low",
                        capital_efficiency_pressure="high", backlog_months=2.0,
                        industry="government")
        assert FirmModel(p, market, params).classify_fork().primary == "HARVEST"

    def test_expand_fork_for_high_growth(self):
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        p = FirmProfile(will_pass_savings_to_customers=True, competitive_intensity="high",
                        backlog_months=18.0, revenue_growth_rate=0.50, industry="consumer_tech")
        assert FirmModel(p, market, params).classify_fork().primary == "EXPAND"

    def test_improve_fork_for_high_debt_regulated(self):
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        p = FirmProfile(technical_debt_pct=65.0, industry="healthcare",
                        has_legacy_modernization=True, current_market_penetration=0.45)
        assert FirmModel(p, market, params).classify_fork().primary == "IMPROVE"

    def test_fork_weights_sum_to_one(self):
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        for profile in [
            FirmProfile(software_is_core_product=False, competitive_intensity="low"),
            FirmProfile(will_pass_savings_to_customers=True, competitive_intensity="high"),
            FirmProfile(technical_debt_pct=60.0, industry="healthcare"),
            FirmProfile(),
        ]:
            fork = FirmModel(profile, market, params).classify_fork()
            total = fork.harvest + fork.reinvest + fork.expand + fork.improve
            assert abs(total - 1.0) < 0.01

    def test_revenue_saturates_over_time(self):
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        p_high_pen = FirmProfile(revenue_growth_rate=0.40, current_market_penetration=0.60,
                                  long_run_growth_rate=0.06)
        p_low_pen = FirmProfile(revenue_growth_rate=0.40, current_market_penetration=0.05,
                                 long_run_growth_rate=0.06)
        fm_high = FirmModel(p_high_pen, market, params)
        fm_low = FirmModel(p_low_pen, market, params)
        assert fm_high._saturating_growth_rate(5) < fm_low._saturating_growth_rate(5)

    def test_absorption_cap_prevents_runaway(self):
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        p = FirmProfile(will_pass_savings_to_customers=True, competitive_intensity="high",
                        backlog_months=24.0, revenue_growth_rate=2.0,
                        current_market_penetration=0.001, industry="consumer_tech")
        results = FirmModel(p, market, params).run()
        for i in range(1, len(results)):
            yr_growth = results[i].headcount_index / max(0.01, results[i-1].headcount_index) - 1
            assert yr_growth <= FirmModel.MAX_ANNUAL_HC_GROWTH + 0.05

    def test_improve_firm_reduces_debt_fastest(self):
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        improve = FirmProfile(technical_debt_pct=60.0, industry="healthcare",
                              has_legacy_modernization=True, current_market_penetration=0.50)
        expand = FirmProfile(technical_debt_pct=60.0, will_pass_savings_to_customers=True,
                             competitive_intensity="high", backlog_months=20.0)
        r_imp = FirmModel(improve, market, params).run()
        r_exp = FirmModel(expand, market, params).run()
        assert r_imp[-1].debt_level < r_exp[-1].debt_level

    def test_all_profiles_run(self):
        import os
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        for fname in os.listdir("firm_model/profiles"):
            if fname.endswith(".yaml"):
                with open(f"firm_model/profiles/{fname}") as f:
                    data = yaml.safe_load(f)
                results = FirmModel(FirmProfile(**data), market, params).run()
                assert len(results) == 10

    def test_headcount_always_positive(self):
        from firm_model.core.firm_model import FirmModel, FirmProfile
        market, params = self._market()
        for profile in [FirmProfile(current_headcount=50), FirmProfile(current_headcount=500)]:
            for r in FirmModel(profile, market, params).run():
                assert r.headcount_absolute > 0
