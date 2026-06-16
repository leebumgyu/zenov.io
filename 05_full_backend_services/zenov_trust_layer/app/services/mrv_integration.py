from ..api_models import IngestTraceabilityResponse, TrustPacket, ValidationResult
from ..audit import record_audit
from ..database.crud import (
    save_carbon_value_result_record,
    save_mrv_result_record,
    save_sensor_reading_record,
)
from .carbon_value_engine import CarbonValueError, calculate_carbon_value
from .evidence_service import create_evidence, verify_evidence
from .mrv_engine import MRVCalculationError, calculate_mrv


def process_mrv_traceability_chain(packet: TrustPacket, validation_result: ValidationResult) -> IngestTraceabilityResponse:
    if validation_result.validation_status != "VALIDATED":
        record_audit(packet.packet_id, "TRACEABILITY_CHAIN_BROKEN", {"reason": "NO_TRUST_NO_MRV"})
        return IngestTraceabilityResponse(
            status="FAILED",
            packet_id=packet.packet_id,
            reason="NO_TRUST_NO_MRV",
            traceability_status="BROKEN",
        )

    evidence_bundle = create_evidence(packet)
    evidence_verification = verify_evidence(evidence_bundle)
    evidence_id = evidence_bundle.evidence.evidence_id
    integrity_report_id = evidence_bundle.integrity_report.integrity_report_id
    record_audit(
        packet.packet_id,
        "EVIDENCE_CREATED",
        {
            "evidence_id": evidence_id,
            "trust_score": evidence_bundle.evidence.trust_score,
            "evidence_hash": evidence_bundle.evidence.evidence_hash,
            "signature_hash": evidence_bundle.evidence.signature_hash,
        },
    )
    record_audit(
        packet.packet_id,
        "INTEGRITY_REPORT_CREATED",
        {
            "evidence_id": evidence_id,
            "integrity_report_id": integrity_report_id,
            "verified": evidence_verification["verified"],
            "status": evidence_verification["status"],
        },
    )
    if not evidence_verification["verified"]:
        record_audit(packet.packet_id, "EVIDENCE_VERIFICATION_FAILED", {"evidence_id": evidence_id})
        record_audit(packet.packet_id, "TRACEABILITY_CHAIN_BROKEN", {"reason": "EVIDENCE_VERIFICATION_FAILED", "evidence_id": evidence_id})
        return IngestTraceabilityResponse(
            status="FAILED",
            packet_id=packet.packet_id,
            evidence_id=evidence_id,
            reason="EVIDENCE_VERIFICATION_FAILED",
            traceability_status="BROKEN",
        )

    record_audit(packet.packet_id, "EVIDENCE_VERIFIED", {"evidence_id": evidence_id, "trust_score": evidence_bundle.evidence.trust_score})
    record_audit(packet.packet_id, "MRV_CALCULATION_STARTED", {})
    try:
        mrv_result = calculate_mrv(packet.payload, packet_id=packet.packet_id, source_id=packet.source_id)
        mrv_result["evidence_id"] = evidence_id
        mrv_result["status"] = "SUCCESS"
        save_mrv_result_record(mrv_result)
        record_audit(
            packet.packet_id,
            "MRV_CALCULATION_SUCCESS",
            {
                "mrv_id": mrv_result["mrv_id"],
                "evidence_id": evidence_id,
                "co2e_kg": mrv_result["co2e_kg"],
                "methodology_version": mrv_result["methodology_version"],
                "emission_factor_version": mrv_result["emission_factor_version"],
            },
        )
    except MRVCalculationError as exc:
        record_audit(packet.packet_id, "MRV_CALCULATION_FAILED", {"error": str(exc)})
        record_audit(packet.packet_id, "TRACEABILITY_CHAIN_BROKEN", {"reason": "MRV_CALCULATION_FAILED", "evidence_id": evidence_id})
        return IngestTraceabilityResponse(
            status="FAILED",
            packet_id=packet.packet_id,
            evidence_id=evidence_id,
            reason="MRV_CALCULATION_FAILED",
            traceability_status="BROKEN",
        )

    record_audit(packet.packet_id, "CARBON_VALUE_STARTED", {"evidence_id": evidence_id, "mrv_id": mrv_result["mrv_id"]})
    try:
        value_result = calculate_carbon_value(mrv_result)
        value_result["status"] = "SUCCESS"
        save_carbon_value_result_record(value_result)
        record_audit(
            packet.packet_id,
            "CARBON_VALUE_CALCULATED",
            {
                "mrv_id": mrv_result["mrv_id"],
                "evidence_id": evidence_id,
                "value_id": value_result["value_id"],
                "estimated_value": value_result["estimated_value"],
                "currency": value_result["currency"],
                "price_source": value_result["price_source"],
                "price_date": value_result["price_date"],
            },
        )
    except CarbonValueError as exc:
        record_audit(packet.packet_id, "CARBON_VALUE_FAILED", {"evidence_id": evidence_id, "mrv_id": mrv_result["mrv_id"], "error": str(exc)})
        record_audit(packet.packet_id, "TRACEABILITY_CHAIN_BROKEN", {"evidence_id": evidence_id, "mrv_id": mrv_result["mrv_id"], "reason": "CARBON_VALUE_FAILED"})
        return IngestTraceabilityResponse(
            status="PARTIAL_SUCCESS",
            packet_id=packet.packet_id,
            evidence_id=evidence_id,
            mrv_id=mrv_result["mrv_id"],
            value_id=None,
            reason="CARBON_VALUE_FAILED",
            traceability_status="MRV_ONLY",
            co2e_kg=mrv_result["co2e_kg"],
            co2e_ton=mrv_result["co2e_ton"],
            methodology_version=mrv_result["methodology_version"],
        )

    save_sensor_reading_record(packet, mrv_result=mrv_result, value_result=value_result)
    record_audit(packet.packet_id, "DB_WRITE_SUCCESS", {"evidence_id": evidence_id, "mrv_id": mrv_result["mrv_id"], "value_id": value_result["value_id"]})
    record_audit(
        packet.packet_id,
        "TRACEABILITY_CHAIN_COMPLETED",
        {
            "evidence_id": evidence_id,
            "mrv_id": mrv_result["mrv_id"],
            "value_id": value_result["value_id"],
        },
    )

    return IngestTraceabilityResponse(
        status="SUCCESS",
        packet_id=packet.packet_id,
        evidence_id=evidence_id,
        mrv_id=mrv_result["mrv_id"],
        value_id=value_result["value_id"],
        traceability_status="COMPLETE",
        co2e_kg=mrv_result["co2e_kg"],
        co2e_ton=mrv_result["co2e_ton"],
        estimated_value=value_result["estimated_value"],
        currency=value_result["currency"],
        methodology_version=mrv_result["methodology_version"],
        value_engine_version=value_result["value_engine_version"],
    )
