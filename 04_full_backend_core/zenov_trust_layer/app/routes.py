import csv
import random
from io import StringIO
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from .global_id import create_global_id
from .api_models import CarbonFactorCalculationRequest, DemoGenerateRequest, GlobalIDRequest, GlobalIDResponse, NavigationCarbonPredictionRequest, PilotPortalCalculationRequest, RawSensorData, TaxiBulkCsvImportRequest, TaxiCsvImportRequest, TrustPacket
from .database.crud import (
    get_audit_records,
    get_dashboard_kpi,
    get_dashboard_summary as build_dashboard_summary,
    get_full_trace_detail,
    get_reject_records,
    get_trace_detail,
    get_traceability_by_mrv,
    get_traceability_by_packet,
    persist_audit_memory_to_db,
    save_global_id_record,
    save_trust_packet_record,
)
from .database.influx import influx_status
from .database.postgres import postgres_status
from .trust import create_trust_packet
from .validation_service import validate_packet
from .services import mrv_integration
from .services.carbon_value_engine import CarbonValueError
from .services.carbon_asset_finance_engine import (
    build_portfolio_finance_summary,
    calculate_asset_pricing,
    calculate_asset_rating,
    calculate_carbon_risk,
    calculate_finance_readiness,
)
from .services.economic_decision_engine import build_economic_decision_summary
from .services.mobility_solar_carbon_engine import (
    MobilitySolarCarbonError,
    calculate_mobility_solar_carbon,
    get_carbon_factor_config,
)
from .services.navigation_carbon_mrv_engine import predict_navigation_carbon_reduction
from .services.bulk_csv_import_service import BulkImportError, bulk_import_taxi_csv, get_import_job, get_latest_import_job
from .services.taxi_csv_import_service import import_taxi_daily_csv

router = APIRouter(prefix="/api/v1")


def _demo_raw_sensor_data(source_suffix: str) -> RawSensorData:
    unique = uuid4().hex[:8].upper()
    source_id = f"SENSOR-KR-DEMO-{source_suffix}-{unique}"
    return RawSensorData(
        source_id=source_id,
        site_id="SITE-KR-DEMO-001",
        asset_id="AST-KR-DEMO-001",
        sensor_id=source_id,
        timestamp="2026-06-19T10:00:00+09:00",
        sequence_no=1,
        payload={
            "ch4_ppm": 145,
            "co2_ppm": 850,
            "temperature_c": 27.5,
            "humidity_pct": 55,
            "flow_m3h": 12,
            "power_kwh": 4.2,
        },
    )


def _simulated_factory_sensor_data(source_suffix: str, sequence_no: int, calibration_status: str) -> RawSensorData:
    unique = uuid4().hex[:8].upper()
    source_id = f"SENSOR-KR-SIM-{source_suffix}-{unique}"
    return RawSensorData(
        source_id=source_id,
        site_id="SITE-KR-DEMO-FACTORY-001",
        asset_id="AST-KR-DEMO-FACTORY-001",
        sensor_id=source_id,
        timestamp="2026-06-19T10:00:00+09:00",
        sequence_no=sequence_no,
        payload={
            "ch4_ppm": round(random.uniform(50, 300), 3),
            "co2_ppm": round(random.uniform(400, 1500), 3),
            "temperature_c": round(random.uniform(20, 35), 2),
            "humidity_pct": round(random.uniform(30, 90), 2),
            "power_kwh": round(random.uniform(1, 50), 3),
            "flow_m3h": round(random.uniform(5, 30), 3),
            "equipment_status": "ONLINE" if calibration_status in {"VALID", "WARNING"} else "BLOCKED",
            "calibration_status": calibration_status,
        },
    )


def _ingest_packet(packet: TrustPacket):
    validation_result = validate_packet(packet)
    result = mrv_integration.process_mrv_traceability_chain(packet, validation_result)
    persist_audit_memory_to_db(packet.packet_id)
    return result


def _pilot_portal_csv(request: PilotPortalCalculationRequest) -> str:
    row = {
        "vehicle_id": request.vehicle_id,
        "operation_date": request.operation_date,
        "distance_km": request.distance_km,
        "passenger_count": request.passenger_count,
        "daily_revenue": request.daily_revenue,
        "driver_id": request.driver_id,
        "energy_consumed_kwh": request.energy_consumed_kwh or "",
        "partner_code": request.partner_code,
        "partner_login_code": request.partner_login_code or "",
        "referral_code": request.referral_code or "",
        "company_name": request.company_name or "",
    }
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(row.keys()))
    writer.writeheader()
    writer.writerow(row)
    return buffer.getvalue()


def _compact_pilot_bridge_result(request: PilotPortalCalculationRequest, import_result: dict):
    row = next((item for item in import_result.get("rows", []) if item.get("row_status") == "SUCCESS"), None)
    if not row:
        failed = import_result.get("failed_rows", [{}])[0] if import_result.get("failed_rows") else {}
        return {
            "status": "FAILED",
            "source": "PILOT_PORTAL_BRIDGE",
            "reason_code": row.get("reason_code") if row else failed.get("reason_code", "IMPORT_FAILED"),
            "import_job_id": import_result.get("import_job_id"),
            "summary": {
                "total_rows": import_result.get("total_rows", 0),
                "success_count": import_result.get("success_count", 0),
                "failed_count": import_result.get("failed_count", 0),
                "duplicate_count": import_result.get("duplicate_count", 0),
            },
            "import_result": import_result,
        }

    snap = row.get("result_snapshot", {})
    packet_id = row.get("packet_id")
    return {
        "status": "SUCCESS",
        "source": "PILOT_PORTAL_BRIDGE",
        "source_files": [
            "source-files/pilot-portal.tsx",
            "source-files/partner-login-page.tsx",
            "source-files/files-slug-page.tsx",
        ],
        "partner": {
            "partner_code": request.partner_code,
            "partner_login_code": request.partner_login_code,
            "referral_code": request.referral_code,
            "company_id": request.company_id,
            "company_name": request.company_name,
        },
        "input": {
            "vehicle_id": request.vehicle_id,
            "driver_id": request.driver_id,
            "operation_date": request.operation_date,
            "distance_km": request.distance_km,
            "passenger_count": request.passenger_count,
            "daily_revenue": request.daily_revenue,
            "energy_consumed_kwh": request.energy_consumed_kwh,
        },
        "import_job_id": import_result.get("import_job_id"),
        "report_id": import_result.get("report_id"),
        "packet_id": packet_id,
        "evidence_id": row.get("evidence_id"),
        "mrv_id": row.get("mrv_id"),
        "verification_id": row.get("verification_id"),
        "asset_id": row.get("asset_id"),
        "trace_url": f"/api/v1/trace/full/{packet_id}" if packet_id else None,
        "mrv_result": {
            "baseline_co2e_kg": snap.get("baseline_co2e"),
            "actual_co2e_kg": snap.get("ev_co2e"),
            "reduction_kgco2e": snap.get("reduction_co2e"),
            "reduction_tco2e": snap.get("issued_quantity_tco2e"),
            "methodology_id": snap.get("methodology_id"),
            "methodology_version": snap.get("methodology_version"),
            "calculation_hash": snap.get("calculation_hash"),
        },
        "verification": {
            "verification_score": snap.get("verification_score"),
            "verification_status": snap.get("verification_status"),
        },
        "asset": {
            "asset_id": row.get("asset_id"),
            "serial_number": snap.get("serial_number"),
            "candidate_status": snap.get("candidate_status"),
            "registry_status": snap.get("registry_status"),
            "estimated_value_krw": snap.get("estimated_value_krw"),
            "estimated_value_usd": snap.get("estimated_value_usd"),
            "credit_unit": snap.get("credit_unit"),
        },
        "reward": {
            "green_point": snap.get("green_point"),
            "wallet_id": snap.get("wallet_id"),
            "wallet_transaction_id": snap.get("wallet_transaction_id"),
        },
        "summary": {
            "total_rows": import_result.get("total_rows", 0),
            "success_count": import_result.get("success_count", 0),
            "failed_count": import_result.get("failed_count", 0),
            "duplicate_count": import_result.get("duplicate_count", 0),
            "evidence_count": import_result.get("evidence_count", 0),
            "mrv_count": import_result.get("mrv_count", 0),
            "verification_pass_count": import_result.get("verification_pass_count", 0),
            "asset_candidate_count": import_result.get("asset_candidate_count", 0),
        },
    }


@router.post("/global-id")
def build_global_id(request: GlobalIDRequest) -> GlobalIDResponse:
    global_id = create_global_id(
        object_type=request.object_type,
        region=request.region,
        domain=request.domain,
    )
    save_global_id_record(
        zenov_id=global_id,
        entity_type=request.object_type,
        region=request.region,
        domain=request.domain,
    )
    return GlobalIDResponse(global_id=global_id)


@router.post("/trust/packet")
def build_trust_packet(raw_data: RawSensorData) -> TrustPacket:
    packet = create_trust_packet(raw_data)
    save_trust_packet_record(packet)
    persist_audit_memory_to_db(packet.packet_id)
    return packet


@router.post("/sensor/ingest")
def ingest_sensor_packet(packet: TrustPacket):
    return _ingest_packet(packet)


@router.get("/audit/{packet_id}")
def get_audit_trail(packet_id: str):
    events = get_audit_records(packet_id)
    if not events:
        raise HTTPException(status_code=404, detail="Audit trail not found")
    return {"packet_id": packet_id, "events": events}


@router.get("/rejects")
def get_reject_logs():
    items = get_reject_records()
    return {"count": len(items), "items": items}


@router.get("/db/status")
def get_db_status():
    return {
        "postgres": postgres_status(),
        "influxdb": influx_status(),
    }


@router.get("/dashboard/kpi")
def get_dashboard_kpi_view():
    return get_dashboard_kpi()


@router.get("/carbon-factor/config")
def get_carbon_factor_config_view():
    return get_carbon_factor_config()


@router.post("/carbon-factor/calculate")
def calculate_carbon_factor_view(request: CarbonFactorCalculationRequest):
    request_data = request.model_dump() if hasattr(request, "model_dump") else request.dict()
    payload = {
        "source_type": request.source_type,
        **request.payload,
        **{
            key: value
            for key, value in request_data.items()
            if key not in {"source_type", "payload"}
        },
    }
    try:
        return calculate_mobility_solar_carbon(payload)
    except MobilitySolarCarbonError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/navigation-carbon/predict")
def predict_navigation_carbon_view(request: NavigationCarbonPredictionRequest):
    payload = request.model_dump() if hasattr(request, "model_dump") else request.dict()
    try:
        return predict_navigation_carbon_reduction(payload)
    except MobilitySolarCarbonError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/pilot-portal/calculate")
def calculate_pilot_portal_view(request: PilotPortalCalculationRequest):
    execution_company_id = request.company_id or request.partner_code
    if request.force_demo_unique:
        execution_company_id = f"{execution_company_id}_PILOT_{uuid4().hex[:6].upper()}"
    try:
        import_result = bulk_import_taxi_csv(
            csv_text=_pilot_portal_csv(request),
            company_id=execution_company_id,
            job_name=f"pilot-portal-{request.partner_code}-{request.vehicle_id}-{request.operation_date}",
            source_filename=request.source_filename,
            baseline_type=request.baseline_type,
            generate_report=request.generate_report,
            reporting_year=request.reporting_year,
        )
    except BulkImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _compact_pilot_bridge_result(request, import_result)


@router.get("/carbon-finance/summary")
def get_carbon_finance_summary_view():
    return build_portfolio_finance_summary()


@router.post("/carbon-finance/rate")
def rate_carbon_asset_view(payload: dict):
    return {
        "rating": calculate_asset_rating(payload),
        "risk": calculate_carbon_risk(payload),
        "pricing": calculate_asset_pricing(payload),
        "finance": calculate_finance_readiness(payload),
    }


@router.get("/economic-decision/summary")
def get_economic_decision_summary_view():
    return build_economic_decision_summary()


@router.post("/economic-decision/simulate")
def simulate_economic_decision_view(payload: dict):
    return build_economic_decision_summary(payload)


@router.post("/taxi/csv/import")
def import_taxi_csv_view(request: TaxiCsvImportRequest):
    try:
        return import_taxi_daily_csv(
            csv_text=request.csv_text,
            company_id=request.company_id,
            baseline_type=request.baseline_type,
            import_batch_name=request.import_batch_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/taxi/csv/bulk-import")
def bulk_import_taxi_csv_view(request: TaxiBulkCsvImportRequest):
    try:
        return bulk_import_taxi_csv(
            csv_text=request.csv_text,
            company_id=request.company_id,
            job_name=request.job_name,
            source_filename=request.source_filename,
            baseline_type=request.baseline_type,
            generate_report=request.generate_report,
            reporting_year=request.reporting_year,
        )
    except BulkImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/import-jobs/latest")
def get_latest_import_job_view(company_id: str = "ANSAN_TRANS"):
    job = get_latest_import_job(company_id)
    if not job:
        raise HTTPException(status_code=404, detail="Latest import job not found")
    return job


@router.get("/import-jobs/{import_job_id}")
def get_import_job_view(import_job_id: str):
    job = get_import_job(import_job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    return job


@router.get("/dashboard/summary")
def get_dashboard_summary_view():
    return build_dashboard_summary()


@router.get("/trace/{packet_id}")
def get_trace_dashboard(packet_id: str):
    trace = get_trace_detail(packet_id)
    if not any([trace.get("trust_packet"), trace.get("mrv"), trace.get("carbon_value"), trace.get("audit_events"), trace.get("reject_log")]):
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


@router.get("/trace/full/{packet_id}")
def get_full_trace_dashboard(packet_id: str):
    trace = get_full_trace_detail(packet_id)
    if trace.get("traceability_status") == "BROKEN" and not trace.get("trust_packet"):
        raise HTTPException(status_code=404, detail="Full trace not found")
    return trace


@router.get("/traceability/packet/{packet_id}")
def get_traceability_chain_by_packet(packet_id: str):
    chain = get_traceability_by_packet(packet_id)
    if not chain.get("packet_id"):
        raise HTTPException(status_code=404, detail="Traceability chain not found")
    return chain


@router.get("/traceability/mrv/{mrv_id}")
def get_traceability_chain_by_mrv(mrv_id: str):
    chain = get_traceability_by_mrv(mrv_id)
    if not chain.get("packet_id"):
        raise HTTPException(status_code=404, detail="Traceability chain not found")
    return chain


@router.post("/demo/hash-mismatch")
def demo_hash_mismatch():
    packet = create_trust_packet(_demo_raw_sensor_data("HASH"))
    save_trust_packet_record(packet)
    packet.payload["ch4_ppm"] = float(packet.payload["ch4_ppm"]) + 1
    result = _ingest_packet(packet)
    return {
        "demo": "HASH_RECALCULATION_FAILED",
        "result": result,
        "trace": get_trace_detail(packet.packet_id),
    }


@router.post("/demo/signature-invalid")
def demo_signature_invalid():
    packet = create_trust_packet(_demo_raw_sensor_data("SIGNATURE"))
    save_trust_packet_record(packet)
    packet.signature = f"INVALID-{packet.signature}"
    result = _ingest_packet(packet)
    return {
        "demo": "SIGNATURE_INVALID",
        "result": result,
        "trace": get_trace_detail(packet.packet_id),
    }


@router.post("/demo/carbon-value-failed")
def demo_carbon_value_failed():
    packet = create_trust_packet(_demo_raw_sensor_data("VALUE"))
    save_trust_packet_record(packet)
    original_calculator = mrv_integration.calculate_carbon_value
    try:
        def fail_carbon_value(*args, **kwargs):
            raise CarbonValueError("DEMO_CARBON_VALUE_FAILED")

        mrv_integration.calculate_carbon_value = fail_carbon_value
        result = _ingest_packet(packet)
    finally:
        mrv_integration.calculate_carbon_value = original_calculator
    return {
        "demo": "CARBON_VALUE_FAILED",
        "result": result,
        "trace": get_trace_detail(packet.packet_id),
    }


@router.post("/demo/generate")
def demo_generate(request: DemoGenerateRequest):
    packets = []
    traces = []
    results = []
    original_calculator = mrv_integration.calculate_carbon_value
    try:
        if request.mode == "CARBON_VALUE_FAILED":
            def fail_carbon_value(*args, **kwargs):
                raise CarbonValueError("DEMO_CARBON_VALUE_FAILED")

            mrv_integration.calculate_carbon_value = fail_carbon_value

        for index in range(request.packet_count):
            calibration_status = request.calibration_status
            if request.mode == "SENSOR_EXPIRED":
                calibration_status = "EXPIRED"
            raw_data = _simulated_factory_sensor_data(
                source_suffix=request.mode,
                sequence_no=index + 1,
                calibration_status=calibration_status,
            )
            packet = create_trust_packet(raw_data)
            save_trust_packet_record(packet)

            if request.mode == "HASH_MISMATCH":
                packet.payload["ch4_ppm"] = float(packet.payload["ch4_ppm"]) + 1
            elif request.mode == "SIGNATURE_INVALID":
                packet.signature = f"INVALID-{packet.signature}"

            result = _ingest_packet(packet)
            trace = get_trace_detail(packet.packet_id)
            packets.append(
                {
                    "packet_id": packet.packet_id,
                    "source_id": packet.source_id,
                    "timestamp": packet.timestamp,
                    "payload": packet.payload,
                    "hash": packet.payload_hash,
                    "signature": packet.signature,
                }
            )
            results.append(result)
            traces.append(trace)
    finally:
        mrv_integration.calculate_carbon_value = original_calculator

    summary = build_dashboard_summary()
    primary_result = results[0] if results else None
    primary_trace = traces[0] if traces else None
    return {
        "mode": request.mode,
        "calibration_status": request.calibration_status,
        "packet_count": request.packet_count,
        "packet": packets[0] if len(packets) == 1 else None,
        "packets": packets,
        "result": primary_result,
        "trace": primary_trace,
        "summary": summary,
    }
