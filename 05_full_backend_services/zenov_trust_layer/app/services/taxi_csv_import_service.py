import csv
from datetime import datetime, timezone
from io import StringIO
from typing import Any, Optional
from uuid import uuid4

from ..api_models import RawSensorData
from ..audit import record_audit
from ..crypto import canonical_json, sha256_hex
from ..trust import create_trust_packet
from ..validation_service import validate_packet
from .evidence_service import create_evidence
from zenov_mobility.app.database.taxi_mrv_crud import save_carbon_asset_candidate, save_green_point, save_mrv_verification, save_taxi_import_log, save_taxi_mrv_result, save_taxi_operation
from zenov_mobility.app.services.carbon_asset_candidate_service import create_carbon_asset_candidate
from zenov_mobility.app.services.reward_service import issue_green_points
from zenov_mobility.app.services.taxi_mrv_service import calculate_taxi_mrv, load_carbon_factor_config
from zenov_mobility.app.services.verification_score_service import calculate_verification_score


FIELD_ALIASES = {
    "vehicle_id": ["vehicle_id", "차량번호", "car_no", "차량"],
    "operation_date": ["operation_date", "운행일", "date", "영업일"],
    "distance_km": ["distance_km", "daily_distance_km", "일일주행거리", "주행거리", "운행거리"],
    "passenger_count": ["passenger_count", "승객수", "탑승건수", "passengers"],
    "daily_revenue": ["daily_revenue", "일일매출", "매출", "revenue"],
    "driver_id": ["driver_id", "기사번호", "기사ID", "driver"],
    "energy_consumed_kwh": ["energy_consumed_kwh", "전기사용량", "충전량", "kwh"],
}


def _new_id(prefix: str) -> str:
    issued_at = datetime.utcnow().strftime("%Y%m%d")
    return f"{prefix}-KR-{issued_at}-{uuid4().hex[:8].upper()}"


def _pick(row: dict[str, str], field: str, default: Any = None) -> Any:
    for alias in FIELD_ALIASES[field]:
        if alias in row and str(row[alias]).strip() != "":
            return str(row[alias]).strip()
    return default


def _float(value: Any, field: str) -> float:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"INVALID_NUMBER:{field}") from exc


def _int(value: Any, field: str) -> int:
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"INVALID_NUMBER:{field}") from exc


def _operation_date(value: str) -> str:
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError("INVALID_DATE:operation_date")


def _energy_kwh(distance_km: float) -> float:
    config = load_carbon_factor_config()
    efficiency = config["vehicle_efficiency"]["ev_taxi"]["value"]
    return distance_km / float(efficiency)


def _point_amount(reduction_kgco2e: float) -> int:
    config = load_carbon_factor_config()
    point_per_kg = float(config["reward_rules"]["green_point"]["value"])
    return max(0, int(round(reduction_kgco2e * point_per_kg)))


def _validate_required(row: dict[str, str]) -> None:
    missing = [
        field
        for field in ("vehicle_id", "operation_date", "distance_km", "passenger_count", "daily_revenue", "driver_id")
        if _pick(row, field) is None
    ]
    if missing:
        raise ValueError(f"REQUIRED_FIELD_MISSING:{','.join(missing)}")


def import_taxi_daily_csv(csv_text: str, company_id: str = "ANSAN_TRANS", baseline_type: str = "lpg_taxi", import_batch_name: Optional[str] = None) -> dict[str, Any]:
    import_batch_id = _new_id("IMP")
    reader = csv.DictReader(StringIO(csv_text.strip()))
    if not reader.fieldnames:
        raise ValueError("CSV_HEADER_MISSING")

    rows = list(reader)
    successes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    total_reduction = 0.0
    total_points = 0
    total_candidate_quantity = 0.0
    total_candidate_value_krw = 0.0
    candidates: list[dict[str, Any]] = []

    record_audit(import_batch_id, "CSV_IMPORTED", {"row_count": len(rows), "company_id": company_id, "import_batch_name": import_batch_name})

    for row_number, row in enumerate(rows, start=1):
        try:
            _validate_required(row)
            vehicle_id = _pick(row, "vehicle_id")
            driver_id = _pick(row, "driver_id")
            operation_date = _operation_date(_pick(row, "operation_date"))
            distance_km = _float(_pick(row, "distance_km"), "distance_km")
            passenger_count = _int(_pick(row, "passenger_count"), "passenger_count")
            daily_revenue = _float(_pick(row, "daily_revenue"), "daily_revenue")
            provided_energy = _pick(row, "energy_consumed_kwh")
            energy_consumed_kwh = _float(provided_energy, "energy_consumed_kwh") if provided_energy is not None else _energy_kwh(distance_km)
            if distance_km <= 0:
                raise ValueError("INVALID_DISTANCE:distance_km must be positive")
            if passenger_count < 0 or daily_revenue < 0 or energy_consumed_kwh < 0:
                raise ValueError("NEGATIVE_VALUE_NOT_ALLOWED")

            payload = {
                "source_type": "EV_TAXI",
                "import_batch_id": import_batch_id,
                "row_number": row_number,
                "company_id": company_id,
                "baseline_type": baseline_type,
                "vehicle_id": vehicle_id,
                "driver_id": driver_id,
                "operation_date": operation_date,
                "distance_km": distance_km,
                "passenger_count": passenger_count,
                "daily_revenue": daily_revenue,
                "energy_consumed_kwh": energy_consumed_kwh,
            }
            raw = RawSensorData(
                source_id=f"TAXI-DAILY-{company_id}-{vehicle_id}-{import_batch_id}",
                site_id=f"SITE-KR-TAXI-{company_id}",
                asset_id=f"VEH-KR-TAXI-{vehicle_id}",
                sensor_id=f"METER-TMONEY-{vehicle_id}",
                timestamp=f"{operation_date}T23:59:59+09:00",
                sequence_no=row_number,
                payload=payload,
            )
            packet = create_trust_packet(raw)
            record_audit(packet.packet_id, "PACKET_CREATED", {"import_batch_id": import_batch_id, "vehicle_id": vehicle_id})
            record_audit(packet.packet_id, "HASH_GENERATED", {"payload_hash": packet.payload_hash})
            record_audit(packet.packet_id, "SIGNATURE_CREATED", {"signature_mode": "HMAC_SHA256"})
            validation = validate_packet(packet)
            if validation.validation_status != "VALIDATED":
                raise ValueError(f"PACKET_VALIDATION_FAILED:{','.join(validation.reasons)}")

            evidence_bundle = create_evidence(packet)
            evidence_id = evidence_bundle.evidence.evidence_id
            record_audit(packet.packet_id, "EVIDENCE_SEALED", {"evidence_id": evidence_id, "trust_score": evidence_bundle.evidence.trust_score})

            carbon = calculate_taxi_mrv(payload)
            reduction_kgco2e = float(carbon["reduction_co2e"])
            points = int(carbon["green_point"])
            mrv_id = carbon["mrv_id"]
            value_id = f"VALUE-TAXI-{uuid4().hex[:10].upper()}"
            mrv_record = {
                "mrv_id": mrv_id,
                "packet_id": packet.packet_id,
                "evidence_id": evidence_id,
                "vehicle_id": vehicle_id,
                "operation_date": operation_date,
                "distance_km": distance_km,
                "energy_consumed_kwh": energy_consumed_kwh,
                "baseline_co2e_kg": carbon["baseline_co2e"],
                "ev_co2e_kg": carbon["ev_co2e"],
                "reduction_co2e_kg": reduction_kgco2e,
                "calculation_hash": carbon["calculation_hash"],
                "methodology_id": carbon["methodology_id"],
                "methodology_version": carbon["methodology_version"],
                "factor_config_id": carbon["factor_config_id"],
                "factor_config_version": carbon["factor_config_version"],
            }
            verification = calculate_verification_score(
                packet=packet.model_dump(),
                evidence={
                    **evidence_bundle.evidence.model_dump(),
                    "integrity_report": evidence_bundle.integrity_report.model_dump(),
                },
                mrv=mrv_record,
            )
            factor_config = load_carbon_factor_config()
            carbon_value_config = factor_config["carbon_value"]
            estimated_price_krw = float(carbon_value_config["estimated_price_krw_per_tco2e"]["value"])
            usd_exchange_rate = float(carbon_value_config["usd_exchange_rate"]["value"])
            estimated_value_krw = max(0.0, reduction_kgco2e / 1000 * estimated_price_krw)
            candidate = create_carbon_asset_candidate(
                packet=packet.model_dump(),
                evidence=evidence_bundle.evidence.model_dump(),
                mrv=mrv_record,
                verification=verification,
                estimated_value_krw=estimated_value_krw,
                usd_exchange_rate=usd_exchange_rate,
                owner_entity=company_id,
                sequence=len(candidates) + 1,
            )
            operation_id = _new_id("TAXIOP")
            operation = {
                "operation_id": operation_id,
                "import_batch_id": import_batch_id,
                "company_id": company_id,
                "vehicle_id": vehicle_id,
                "driver_id": driver_id,
                "operation_date": operation_date,
                "distance_km": distance_km,
                "passenger_count": passenger_count,
                "daily_revenue": daily_revenue,
                "energy_consumed_kwh": energy_consumed_kwh,
                "packet_id": packet.packet_id,
                "evidence_id": evidence_id,
                "mrv_id": mrv_id,
                "value_id": value_id,
                "baseline_co2e_kg": carbon["baseline_co2e"],
                "ev_co2e_kg": carbon["ev_co2e"],
                "reduction_co2e_kg": reduction_kgco2e,
                "green_point": points,
                "factor_config_id": carbon["factor_config_id"],
                "factor_config_version": carbon["factor_config_version"],
                "methodology_id": carbon["methodology_id"],
                "methodology_version": carbon["methodology_version"],
                "calculation_hash": carbon["calculation_hash"],
                "verification_id": verification["verification_id"],
                "verification_status": verification["verification_status"],
                "verification_score": verification["verification_score"],
                "completeness_score": verification["completeness_score"],
                "integrity_score": verification["integrity_score"],
                "source_reliability_score": verification["source_reliability_score"],
                "methodology_score": verification["methodology_score"],
                "anomaly_flag": verification["anomaly_flag"],
                "anomaly_reason": verification["anomaly_reason"],
                "candidate_id": candidate["candidate_id"] if candidate else None,
                "serial_number": candidate["serial_number"] if candidate else None,
                "candidate_status": candidate["candidate_status"] if candidate else None,
                "registry_status": candidate["registry_status"] if candidate else None,
                "validation_status": "VALIDATED",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            ledger_entry = {
                "ledger_id": _new_id("GPT"),
                "vehicle_id": vehicle_id,
                "driver_id": driver_id,
                "operation_date": operation_date,
                "packet_id": packet.packet_id,
                "evidence_id": evidence_id,
                "mrv_id": mrv_id,
                "point_amount": points,
                "reason": "CARBON_REDUCTION",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            save_taxi_operation(operation)
            save_taxi_mrv_result(mrv_record)
            save_mrv_verification(verification)
            wallet_transaction = None
            if candidate:
                save_carbon_asset_candidate(candidate)
                candidates.append(candidate)
                total_candidate_quantity += float(candidate["issued_quantity_tco2e"])
                total_candidate_value_krw += float(candidate["estimated_value_krw"])
                wallet_transaction = issue_green_points(
                    driver_id=driver_id,
                    owner_entity=company_id,
                    vehicle_id=vehicle_id,
                    packet=packet.model_dump(),
                    evidence=evidence_bundle.evidence.model_dump(),
                    mrv=mrv_record,
                    verification=verification,
                    asset_candidate=candidate,
                )
                ledger_entry["point_amount"] = wallet_transaction["point_amount"]
                ledger_entry["wallet_id"] = wallet_transaction["wallet_id"]
                ledger_entry["wallet_transaction_id"] = wallet_transaction["transaction_id"]
                ledger_entry["asset_id"] = candidate["candidate_id"]
                save_green_point(ledger_entry)
                record_audit(
                    packet.packet_id,
                    "CARBON_ASSET_CANDIDATE_CREATED",
                    {
                        "candidate_id": candidate["candidate_id"],
                        "serial_number": candidate["serial_number"],
                        "mrv_id": mrv_id,
                        "evidence_id": evidence_id,
                        "registry_status": candidate["registry_status"],
                    },
                )
                record_audit(
                    packet.packet_id,
                    "WALLET_POINT_ISSUED",
                    {
                        "wallet_id": wallet_transaction["wallet_id"],
                        "wallet_transaction_id": wallet_transaction["transaction_id"],
                        "driver_id": driver_id,
                        "asset_id": candidate["candidate_id"],
                        "point_amount": wallet_transaction["point_amount"],
                    },
                )
            record_audit(packet.packet_id, "MRV_VERIFICATION_SCORED", {"evidence_id": evidence_id, "mrv_id": mrv_id, "verification_id": verification["verification_id"], "verification_score": verification["verification_score"], "verification_status": verification["verification_status"]})
            record_audit(
                packet.packet_id,
                "TAXI_MRV_CALCULATED",
                {
                    "evidence_id": evidence_id,
                    "mrv_id": mrv_id,
                    "reduction_kgco2e": reduction_kgco2e,
                    "methodology_id": carbon["methodology_id"],
                    "methodology_version": carbon["methodology_version"],
                    "calculation_hash": carbon["calculation_hash"],
                },
            )
            if wallet_transaction:
                record_audit(packet.packet_id, "POINT_ISSUED", {"evidence_id": evidence_id, "mrv_id": mrv_id, "asset_id": candidate["candidate_id"], "point_amount": wallet_transaction["point_amount"]})
            save_taxi_import_log(
                {
                    "import_log_id": _new_id("TLOG"),
                    "import_batch_id": import_batch_id,
                    "row_number": row_number,
                    "vehicle_id": vehicle_id,
                    "status": "SUCCESS",
                    "reason": None,
                    "raw_row": row,
                    "packet_id": packet.packet_id,
                    "evidence_id": evidence_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            total_reduction += reduction_kgco2e
            total_points += int(wallet_transaction["point_amount"]) if wallet_transaction else 0
            successes.append(
                {
                    "row_number": row_number,
                    "vehicle_id": vehicle_id,
                    "operation_date": operation_date,
                    "packet_id": packet.packet_id,
                    "evidence_id": evidence_id,
                    "hash": packet.payload_hash,
                    "signature": packet.signature,
                    "mrv_id": mrv_id,
                    "value_id": value_id,
                    "distance_km": distance_km,
                    "passenger_count": passenger_count,
                    "baseline_co2e": carbon["baseline_co2e"],
                    "ev_co2e": carbon["ev_co2e"],
                    "reduction_co2e": reduction_kgco2e,
                    "green_point": points,
                    "methodology_id": carbon["methodology_id"],
                    "methodology_version": carbon["methodology_version"],
                    "calculation_hash": carbon["calculation_hash"],
                    "verification_id": verification["verification_id"],
                    "verification_score": verification["verification_score"],
                    "verification_status": verification["verification_status"],
                    "completeness_score": verification["completeness_score"],
                    "integrity_score": verification["integrity_score"],
                    "source_reliability_score": verification["source_reliability_score"],
                    "methodology_score": verification["methodology_score"],
                    "anomaly_flag": verification["anomaly_flag"],
                    "anomaly_reason": verification["anomaly_reason"],
                    "candidate_id": candidate["candidate_id"] if candidate else None,
                    "serial_number": candidate["serial_number"] if candidate else None,
                    "candidate_status": candidate["candidate_status"] if candidate else None,
                    "registry_status": candidate["registry_status"] if candidate else None,
                    "issued_quantity_tco2e": candidate["issued_quantity_tco2e"] if candidate else 0,
                    "estimated_value_krw": candidate["estimated_value_krw"] if candidate else 0,
                    "estimated_value_usd": candidate["estimated_value_usd"] if candidate else 0,
                    "credit_unit": candidate["credit_unit"] if candidate else "tCO2e",
                    "wallet_id": wallet_transaction["wallet_id"] if wallet_transaction else None,
                    "wallet_transaction_id": wallet_transaction["transaction_id"] if wallet_transaction else None,
                    "wallet_point_amount": wallet_transaction["point_amount"] if wallet_transaction else 0,
                }
            )
        except ValueError as exc:
            vehicle_id = _pick(row, "vehicle_id", "")
            failure = {
                "row_number": row_number,
                "vehicle_id": vehicle_id,
                "status": "FAILED",
                "reason": str(exc),
                "raw_row": row,
            }
            save_taxi_import_log(
                {
                    "import_log_id": _new_id("TLOG"),
                    "import_batch_id": import_batch_id,
                    **failure,
                    "packet_id": None,
                    "evidence_id": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            failures.append(failure)

    summary_material = {
        "import_batch_id": import_batch_id,
        "success_count": len(successes),
        "failure_count": len(failures),
        "total_reduction_kgco2e": total_reduction,
        "total_green_point": total_points,
        "verified_count": sum(1 for item in successes if item.get("verification_status") == "VERIFIED"),
        "conditionally_verified_count": sum(1 for item in successes if item.get("verification_status") == "CONDITIONALLY_VERIFIED"),
        "rejected_count": sum(1 for item in successes if item.get("verification_status") == "REJECTED"),
        "asset_candidate_count": len(candidates),
        "issued_quantity_tco2e": total_candidate_quantity,
        "estimated_value_krw": total_candidate_value_krw,
    }
    return {
        **summary_material,
        "total_rows": len(rows),
        "summary_hash": sha256_hex(canonical_json(summary_material)),
        "legal_disclaimer": "Carbon Asset Candidate is not a Carbon Credit. It is a verified MRV data package that may later become a carbon asset or credit after external verification, certification, and registry review.",
        "candidates": candidates,
        "successes": successes,
        "failures": failures,
    }
