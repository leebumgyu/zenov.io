from __future__ import annotations

from typing import Any


def build_economic_decision_summary(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    electricity_peak_price = float(payload.get("electricity_peak_price_krw_per_kwh", 210))
    electricity_solar_window_price = float(payload.get("solar_window_price_krw_per_kwh", 120))
    charging_kwh = float(payload.get("daily_charging_kwh", 1800))
    solar_generation_kwh = float(payload.get("solar_generation_kwh", 2400))
    ess_available_kwh = float(payload.get("ess_available_kwh", 900))
    fleet_size = int(payload.get("fleet_size", 143))
    target_fleet_size = int(payload.get("target_fleet_size", 300))
    empty_rate = float(payload.get("empty_rate", 0.31))
    charging_cost_krw = float(payload.get("charging_cost_krw", 378000))
    carbon_value_krw = float(payload.get("annual_carbon_value_krw", 15000000))
    investment_krw = float(payload.get("investment_krw", 100000000))
    operating_cost_krw = float(payload.get("annual_operating_cost_krw", 25000000))

    energy_saving_krw = max(0.0, electricity_peak_price - electricity_solar_window_price) * min(charging_kwh, solar_generation_kwh)
    energy_saving_pct = (energy_saving_krw / max(1.0, charging_kwh * electricity_peak_price)) * 100

    mobility_efficiency_gain_pct = max(0.0, min(25.0, empty_rate * 40))
    mobility_profit_uplift_krw = (charging_cost_krw * 0.08) + carbon_value_krw / 12

    net_carbon_cashflow = carbon_value_krw - operating_cost_krw
    carbon_yield_pct = (carbon_value_krw / max(1.0, investment_krw)) * 100
    payback_years = investment_krw / max(1.0, carbon_value_krw)

    expansion_ratio = target_fleet_size / max(1, fleet_size)
    expected_co2e_ton = round(350 * (expansion_ratio - 1), 3)
    expected_value_krw = round(carbon_value_krw * expansion_ratio, 3)
    opportunity_score = min(100.0, round(55 + (expansion_ratio * 12) + energy_saving_pct + (1 - empty_rate) * 10, 3))

    city_total_reduction_tco2e = round(expected_co2e_ton + fleet_size * 0.85, 3)
    city_total_value_krw = round(expected_value_krw + energy_saving_krw * 365, 3)
    city_roi_pct = round(((city_total_value_krw - investment_krw) / max(1.0, investment_krw)) * 100, 3)

    recommended_actions = [
        {
            "action_id": "ACT-ENERGY-1400-1600",
            "domain": "ENERGY",
            "recommendation": "14:00~16:00 EV charging window",
            "reason": "solar_generation_peak",
            "expected_saving_pct": round(energy_saving_pct, 3),
        },
        {
            "action_id": "ACT-ESS-SOLAR-CHARGE",
            "domain": "ENERGY",
            "recommendation": "Charge ESS during solar surplus",
            "reason": "solar_generation_above_charging_demand",
            "expected_saving_krw": round(energy_saving_krw, 3),
        },
        {
            "action_id": "ACT-FLEET-EV-TAXI-EXPANSION",
            "domain": "MOBILITY",
            "recommendation": f"Expand EV Taxi fleet from {fleet_size} to {target_fleet_size}",
            "reason": "carbon_value_and_operating_scale",
            "expected_co2e_ton": expected_co2e_ton,
            "expected_value_krw": expected_value_krw,
        },
    ]

    return {
        "platform": "ZENOV_ENERGY_MOBILITY_ECONOMIC_OS",
        "energy_economics": {
            "optimal_charge_window": "14:00~16:00",
            "optimal_discharge_window": "18:00~21:00",
            "estimated_daily_saving_krw": round(energy_saving_krw, 3),
            "estimated_saving_pct": round(energy_saving_pct, 3),
            "solar_generation_kwh": solar_generation_kwh,
            "ess_available_kwh": ess_available_kwh,
        },
        "mobility_economics": {
            "fleet_size": fleet_size,
            "target_fleet_size": target_fleet_size,
            "empty_rate": empty_rate,
            "estimated_monthly_profit_uplift_krw": round(mobility_profit_uplift_krw, 3),
            "efficiency_gain_pct": round(mobility_efficiency_gain_pct, 3),
        },
        "carbon_yield": {
            "investment_krw": investment_krw,
            "annual_carbon_value_krw": carbon_value_krw,
            "annual_operating_cost_krw": operating_cost_krw,
            "carbon_yield_pct": round(carbon_yield_pct, 3),
            "net_carbon_cashflow_krw": round(net_carbon_cashflow, 3),
            "payback_years": round(payback_years, 3),
        },
        "opportunity": {
            "opportunity_score": opportunity_score,
            "expected_co2e_ton": expected_co2e_ton,
            "expected_value_krw": expected_value_krw,
            "scenario": f"EV Taxi {fleet_size} -> {target_fleet_size}",
        },
        "digital_twin": {
            "taxi": f"{fleet_size} -> {target_fleet_size}",
            "solar": "1MW -> 5MW",
            "ess": "0MWh -> 2MWh",
            "expected_reduction_tco2e": round(expected_co2e_ton + 420, 3),
            "expected_roi_pct": round(max(city_roi_pct, carbon_yield_pct), 3),
        },
        "city_scale": {
            "city_total_reduction_tco2e": city_total_reduction_tco2e,
            "city_total_value_krw": city_total_value_krw,
            "city_roi_pct": city_roi_pct,
        },
        "recommended_actions": recommended_actions,
    }
