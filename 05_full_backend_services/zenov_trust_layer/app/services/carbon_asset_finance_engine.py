from __future__ import annotations

from statistics import mean
from typing import Any

from .mobility_solar_carbon_engine import get_carbon_factor_config


RATING_THRESHOLDS = [
    (95, "AAA"),
    (90, "AA"),
    (85, "A"),
    (75, "BBB"),
    (65, "BB"),
    (55, "B"),
    (0, "CCC"),
]

RATING_PREMIUMS = {
    "AAA": 0.15,
    "AA": 0.10,
    "A": 0.06,
    "BBB": 0.00,
    "BB": -0.08,
    "B": -0.15,
    "CCC": -0.30,
}


def _clamp_score(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(100.0, number))


def _rating_from_score(score: float) -> str:
    for threshold, rating in RATING_THRESHOLDS:
        if score >= threshold:
            return rating
    return "CCC"


def _verification_score(status: str) -> float:
    return {
        "VERIFIED": 100,
        "CONDITIONALLY_VERIFIED": 82,
        "UNDER_REVIEW": 70,
        "PENDING": 60,
        "REJECTED": 20,
    }.get(str(status or "").upper(), 60)


def calculate_asset_rating(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    trust_score = _clamp_score(payload.get("trust_score"), 98)
    audit_score = _clamp_score(payload.get("audit_score"), 96)
    calibration_score = _clamp_score(payload.get("calibration_score"), 94)
    data_quality_score = _clamp_score(payload.get("data_quality_score"), 95)
    verification_status = str(payload.get("verification_status", "VERIFIED")).upper()
    project_history_score = _clamp_score(payload.get("project_history_score"), 90)
    verification_numeric = _verification_score(verification_status)

    score = (
        trust_score * 0.30
        + audit_score * 0.20
        + calibration_score * 0.15
        + data_quality_score * 0.15
        + verification_numeric * 0.10
        + project_history_score * 0.10
    )
    rating = _rating_from_score(score)
    return {
        "asset_id": payload.get("asset_id", "AST-ZNV-MOB-2026-000001"),
        "rating": rating,
        "score": round(score, 3),
        "weights": {
            "trust_score": 0.30,
            "audit_score": 0.20,
            "calibration_score": 0.15,
            "data_quality_score": 0.15,
            "verification_status": 0.10,
            "project_history": 0.10,
        },
        "components": {
            "trust_score": trust_score,
            "audit_score": audit_score,
            "calibration_score": calibration_score,
            "data_quality_score": data_quality_score,
            "verification_status": verification_status,
            "verification_score": verification_numeric,
            "project_history_score": project_history_score,
        },
    }


def calculate_carbon_risk(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    calibration_score = _clamp_score(payload.get("calibration_score"), 94)
    sensor_reliability_score = _clamp_score(payload.get("sensor_reliability_score"), 95)
    verification_status = str(payload.get("verification_status", "VERIFIED")).upper()
    data_integrity_score = _clamp_score(payload.get("data_integrity_score"), payload.get("trust_score", 98))
    regulation_score = _clamp_score(payload.get("regulation_score"), 88)

    risk_factors = {
        "calibration_risk": 100 - calibration_score,
        "sensor_risk": 100 - sensor_reliability_score,
        "verification_risk": 100 - _verification_score(verification_status),
        "regulation_risk": 100 - regulation_score,
        "data_integrity_risk": 100 - data_integrity_score,
    }
    risk_score = (
        risk_factors["calibration_risk"] * 0.20
        + risk_factors["sensor_risk"] * 0.20
        + risk_factors["verification_risk"] * 0.20
        + risk_factors["regulation_risk"] * 0.20
        + risk_factors["data_integrity_risk"] * 0.20
    )
    if risk_score <= 20:
        status = "LOW_RISK"
    elif risk_score <= 40:
        status = "MODERATE_RISK"
    else:
        status = "HIGH_RISK"
    return {
        "risk_score": round(risk_score, 3),
        "risk_status": status,
        "risk_factors": {key: round(value, 3) for key, value in risk_factors.items()},
    }


def calculate_asset_pricing(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    config = get_carbon_factor_config()
    rating_result = calculate_asset_rating(payload)
    risk_result = calculate_carbon_risk(payload)
    quantity_tco2e = float(payload.get("quantity_tco2e", payload.get("issued_quantity_tco2e", 10)))
    market_price = float(payload.get("carbon_market_price", config["global"]["carbon_price"]["value"]))
    rating = rating_result["rating"]
    premium = RATING_PREMIUMS.get(rating, 0)
    risk_discount = max(0.0, min(0.50, risk_result["risk_score"] / 200))
    base_value = quantity_tco2e * market_price
    fair_value = base_value * (1 + premium) * (1 - risk_discount)
    return {
        "asset_id": rating_result["asset_id"],
        "quantity_tco2e": quantity_tco2e,
        "market_price_krw_per_tco2e": market_price,
        "rating": rating,
        "rating_premium": premium,
        "risk_discount": round(risk_discount, 4),
        "base_value_krw": round(base_value, 3),
        "fair_value_krw": round(fair_value, 3),
        "currency": config.get("currency", "KRW"),
    }


def calculate_finance_readiness(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    rating_result = calculate_asset_rating(payload)
    risk_result = calculate_carbon_risk(payload)
    verification_status = rating_result["components"]["verification_status"]
    score = rating_result["score"] - (risk_result["risk_score"] * 0.5)
    if rating_result["rating"] in {"AAA", "AA", "A"} and risk_result["risk_score"] <= 20 and verification_status == "VERIFIED":
        status = "INVESTABLE"
    elif score >= 75 and verification_status in {"VERIFIED", "CONDITIONALLY_VERIFIED"}:
        status = "READY"
    else:
        status = "NOT_READY"
    return {
        "finance_readiness": status,
        "finance_score": round(score, 3),
        "required_evidence": [
            "asset_rating",
            "risk_score",
            "trust_score",
            "verification_status",
            "methodology_version",
        ],
    }


def build_portfolio_finance_summary(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    sample_assets = payload.get("assets") or [
        {
            "asset_id": "AST-ZNV-MOB-2026-000001",
            "quantity_tco2e": 10,
            "trust_score": 98,
            "audit_score": 96,
            "calibration_score": 94,
            "data_quality_score": 95,
            "verification_status": "VERIFIED",
            "project_history_score": 90,
        },
        {
            "asset_id": "AST-ZNV-SOLAR-2026-000002",
            "quantity_tco2e": 25,
            "trust_score": 94,
            "audit_score": 92,
            "calibration_score": 91,
            "data_quality_score": 93,
            "verification_status": "VERIFIED",
            "project_history_score": 88,
        },
        {
            "asset_id": "AST-ZNV-BUS-2026-000003",
            "quantity_tco2e": 16,
            "trust_score": 88,
            "audit_score": 86,
            "calibration_score": 84,
            "data_quality_score": 87,
            "verification_status": "CONDITIONALLY_VERIFIED",
            "project_history_score": 78,
        },
    ]
    priced_assets = []
    for asset in sample_assets:
        rating = calculate_asset_rating(asset)
        risk = calculate_carbon_risk(asset)
        pricing = calculate_asset_pricing(asset)
        finance = calculate_finance_readiness(asset)
        priced_assets.append({**asset, **rating, **risk, **pricing, **finance})

    total_co2e = sum(float(asset["quantity_tco2e"]) for asset in priced_assets)
    total_value = sum(float(asset["fair_value_krw"]) for asset in priced_assets)
    monthly_growth_tco2e = float(payload.get("monthly_growth_tco2e", total_co2e * 0.08))
    forecast = {
        "30d": {
            "expected_co2e": round(total_co2e + monthly_growth_tco2e, 3),
            "expected_value_krw": round(total_value * 1.08, 3),
        },
        "90d": {
            "expected_co2e": round(total_co2e + monthly_growth_tco2e * 3, 3),
            "expected_value_krw": round(total_value * 1.24, 3),
        },
        "180d": {
            "expected_co2e": round(total_co2e + monthly_growth_tco2e * 6, 3),
            "expected_value_krw": round(total_value * 1.52, 3),
        },
        "1y": {
            "expected_co2e": round(total_co2e + monthly_growth_tco2e * 12, 3),
            "expected_value_krw": round(total_value * 2.05, 3),
        },
    }
    opportunity_score = min(100, round(55 + len(priced_assets) * 7 + total_co2e / 10, 3))
    return {
        "platform": "ZENOV_CARBON_ASSET_FINANCE_PLATFORM",
        "project_count": len({asset.get("project_id", "CPJ-ZNV-DEMO") for asset in priced_assets}),
        "asset_count": len(priced_assets),
        "total_co2e": round(total_co2e, 3),
        "total_fair_value_krw": round(total_value, 3),
        "average_trust_score": round(mean(asset["components"]["trust_score"] for asset in priced_assets), 3),
        "average_rating_score": round(mean(asset["score"] for asset in priced_assets), 3),
        "average_risk_score": round(mean(asset["risk_score"] for asset in priced_assets), 3),
        "average_rating": _rating_from_score(mean(asset["score"] for asset in priced_assets)),
        "finance_readiness": calculate_finance_readiness(
            {
                "trust_score": mean(asset["components"]["trust_score"] for asset in priced_assets),
                "audit_score": mean(asset["components"]["audit_score"] for asset in priced_assets),
                "calibration_score": mean(asset["components"]["calibration_score"] for asset in priced_assets),
                "data_quality_score": mean(asset["components"]["data_quality_score"] for asset in priced_assets),
                "verification_status": "VERIFIED",
                "project_history_score": mean(asset["components"]["project_history_score"] for asset in priced_assets),
                "sensor_reliability_score": 93,
                "regulation_score": 88,
            }
        )["finance_readiness"],
        "forecast": forecast,
        "opportunity": {
            "scenario": "EV Taxi 100 -> 300",
            "opportunity_score": opportunity_score,
            "expected_roi_status": "HIGH_POTENTIAL" if opportunity_score >= 80 else "WATCH",
        },
        "assets": priced_assets,
        "marketplace_readiness": {
            "market_status": "PREPARATION_ONLY",
            "offer": "DISABLED",
            "bid": "DISABLED",
            "settlement": "SIMULATION_ONLY",
        },
    }
