from datetime import datetime
from typing import Any, Optional

from ..api_models import AuditEvent, RejectLog, StoredSensorPacket, TrustPacket
from ..storage import (
    audit_events,
    carbon_asset_candidate_by_mrv_id,
    carbon_asset_candidates,
    carbon_value_results,
    mrv_by_packet_id,
    mrv_results,
    mrv_verification_records,
    reject_logs,
    save_audit,
    save_carbon_value_memory,
    save_mrv_memory,
    save_packet,
    save_reject,
    save_trust_packet_memory,
    taxi_daily_operations,
    taxi_mrv_by_packet_id,
    taxi_mrv_results,
    value_by_mrv_id,
    verification_by_packet_id,
    trust_packets,
)
from .influx import write_sensor_reading
from .evidence_crud import get_evidence_by_packet
from .models import AuditLogModel, CarbonValueResultModel, GlobalIDModel, MRVResultModel, RejectLogModel, TrustPacketModel
from .postgres import session_scope


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def save_global_id_record(zenov_id: str, entity_type: str, region: str, domain: str, metadata: Optional[dict[str, Any]] = None) -> bool:
    with session_scope() as session:
        if session is None:
            return False
        session.merge(
            GlobalIDModel(
                zenov_id=zenov_id,
                entity_type=entity_type,
                region=region,
                domain=domain,
                metadata_json=metadata or {},
            )
        )
        return True


def save_trust_packet_record(packet: TrustPacket) -> bool:
    with session_scope() as session:
        if session is None:
            save_trust_packet_memory(packet)
            return False
        session.merge(
            TrustPacketModel(
                packet_id=packet.packet_id,
                source_id=packet.source_id,
                site_id=packet.site_id,
                asset_id=packet.asset_id,
                sensor_id=packet.sensor_id,
                timestamp=_parse_timestamp(packet.timestamp),
                sequence_no=packet.sequence_no,
                payload_hash=packet.payload_hash,
                signature=packet.signature,
                validation_status=packet.validation_status,
                raw_packet=packet.model_dump(),
            )
        )
        return True


def save_audit_record(event: AuditEvent) -> bool:
    with session_scope() as session:
        if session is None:
            return False
        session.add(
            AuditLogModel(
                packet_id=event.packet_id,
                event_type=event.event_type,
                event_status="INFO",
                evidence_id=event.detail.get("evidence_id"),
                mrv_id=event.detail.get("mrv_id"),
                value_id=event.detail.get("value_id"),
                asset_id=event.detail.get("asset_id"),
                message=event.event_type,
                actor="system",
                detail=event.detail,
                created_at=event.event_at,
            )
        )
        return True


def save_reject_record(reject: RejectLog) -> bool:
    with session_scope() as session:
        if session is None:
            save_reject(reject)
            return False
        for reason in reject.reason:
            session.add(
                RejectLogModel(
                    packet_id=reject.packet_id,
                    source_id=reject.source_id,
                    reason_code=reason.split(":", 1)[0],
                    reason_message=reason,
                    raw_packet=reject.raw_packet,
                    validator_version=reject.validator_version,
                    rejected_at=reject.rejected_at,
                )
            )
        return True


def save_mrv_result_record(mrv_result: dict[str, Any]) -> bool:
    with session_scope() as session:
        if session is None:
            save_mrv_memory(mrv_result)
            return False
        session.merge(
            MRVResultModel(
                mrv_id=mrv_result["mrv_id"],
                packet_id=mrv_result["packet_id"],
                evidence_id=mrv_result.get("evidence_id"),
                source_id=mrv_result["source_id"],
                co2e_kg=mrv_result["co2e_kg"],
                co2e_ton=mrv_result["co2e_ton"],
                methodology_version=mrv_result["methodology_version"],
                emission_factor_version=mrv_result["emission_factor_version"],
                calculation_hash=mrv_result["calculation_hash"],
                status=mrv_result.get("status", "SUCCESS"),
            )
        )
        return True


def save_carbon_value_result_record(value_result: dict[str, Any]) -> bool:
    with session_scope() as session:
        if session is None:
            save_carbon_value_memory(value_result)
            return False
        session.merge(
            CarbonValueResultModel(
                value_id=value_result["value_id"],
                mrv_id=value_result["mrv_id"],
                packet_id=value_result["packet_id"],
                carbon_price_per_ton=value_result["carbon_price_per_ton"],
                currency=value_result["currency"],
                price_source=value_result["price_source"],
                price_date=_parse_timestamp(str(value_result["price_date"]) + "T00:00:00+00:00") if len(str(value_result["price_date"])) == 10 else _parse_timestamp(str(value_result["price_date"])),
                estimated_value=value_result["estimated_value"],
                value_engine_version=value_result["value_engine_version"],
                status=value_result.get("status", "SUCCESS"),
            )
        )
        return True


def save_sensor_reading_record(packet: TrustPacket, mrv_result: Optional[dict[str, Any]] = None, value_result: Optional[dict[str, Any]] = None) -> bool:
    return write_sensor_reading(packet, mrv_result=mrv_result, value_result=value_result)


def get_audit_records(packet_id: str) -> list[dict[str, Any]]:
    with session_scope() as session:
        if session is None:
            return [event.model_dump() for event in audit_events.get(packet_id, [])]
        rows = (
            session.query(AuditLogModel)
            .filter(AuditLogModel.packet_id == packet_id)
            .order_by(AuditLogModel.created_at.asc())
            .all()
        )
        return [
            {
                "audit_id": row.audit_id,
                "packet_id": row.packet_id,
                "event_type": row.event_type,
                "event_status": row.event_status,
                "evidence_id": row.evidence_id,
                "mrv_id": row.mrv_id,
                "value_id": row.value_id,
                "asset_id": row.asset_id,
                "message": row.message,
                "actor": row.actor,
                "detail": row.detail,
                "created_at": row.created_at,
            }
            for row in rows
        ]


def get_reject_records() -> list[dict[str, Any]]:
    with session_scope() as session:
        if session is None:
            return [reject.model_dump() for reject in reject_logs]
        rows = session.query(RejectLogModel).order_by(RejectLogModel.rejected_at.desc()).all()
        return [
            {
                "reject_id": row.reject_id,
                "packet_id": row.packet_id,
                "source_id": row.source_id,
                "reason_code": row.reason_code,
                "reason_message": row.reason_message,
                "raw_packet": row.raw_packet,
                "validator_version": row.validator_version,
                "rejected_at": row.rejected_at,
            }
            for row in rows
        ]


def persist_audit_memory_to_db(packet_id: str) -> int:
    events = list(audit_events.get(packet_id, []))
    written = 0
    for event in events:
        if save_audit_record(event):
            written += 1
    return written


def get_dashboard_kpi() -> dict[str, Any]:
    with session_scope() as session:
        if session is not None:
            mrv_rows = session.query(MRVResultModel).all()
            value_rows = session.query(CarbonValueResultModel).all()
            total_co2e_ton = sum(row.co2e_ton for row in mrv_rows)
            estimated_value = sum(row.estimated_value for row in value_rows)
            latest_mrv = mrv_rows[-1] if mrv_rows else None
            latest_value = value_rows[-1] if value_rows else None
            return {
                "source": "postgres",
                "mrv_result_count": len(mrv_rows),
                "carbon_value_result_count": len(value_rows),
                "realtime_co2e_kg": latest_mrv.co2e_kg if latest_mrv else 0,
                "cumulative_co2e_ton": total_co2e_ton,
                "estimated_carbon_value": estimated_value,
                "currency": latest_value.currency if latest_value else "KRW",
                "mrv_engine_version": latest_mrv.methodology_version if latest_mrv else None,
                "carbon_price_source": latest_value.price_source if latest_value else None,
            }

    latest_mrv = next(reversed(mrv_results.values()), None) if mrv_results else None
    latest_value = next(reversed(carbon_value_results.values()), None) if carbon_value_results else None
    return {
        "source": "memory_fallback",
        "mrv_result_count": len(mrv_results),
        "carbon_value_result_count": len(carbon_value_results),
        "realtime_co2e_kg": latest_mrv["co2e_kg"] if latest_mrv else 0,
        "cumulative_co2e_ton": sum(result["co2e_ton"] for result in mrv_results.values()),
        "estimated_carbon_value": sum(result["estimated_value"] for result in carbon_value_results.values()),
        "currency": latest_value["currency"] if latest_value else "KRW",
        "trust_status": "VALIDATED" if latest_mrv else "NO_DATA",
        "mrv_engine_version": latest_mrv["methodology_version"] if latest_mrv else None,
        "carbon_price_source": latest_value["price_source"] if latest_value else None,
    }


def get_traceability_by_packet(packet_id: str) -> dict[str, Any]:
    with session_scope() as session:
        if session is not None:
            mrv_row = session.query(MRVResultModel).filter(MRVResultModel.packet_id == packet_id).first()
            value_row = None
            if mrv_row:
                value_row = session.query(CarbonValueResultModel).filter(CarbonValueResultModel.mrv_id == mrv_row.mrv_id).first()
            audit_rows = (
                session.query(AuditLogModel)
                .filter(AuditLogModel.packet_id == packet_id)
                .order_by(AuditLogModel.created_at.asc())
                .all()
            )
            return {
                "packet_id": packet_id,
                "evidence_id": mrv_row.evidence_id if mrv_row else None,
                "mrv_id": mrv_row.mrv_id if mrv_row else None,
                "value_id": value_row.value_id if value_row else None,
                "traceability_status": "COMPLETE" if mrv_row and value_row and audit_rows else "BROKEN",
                "audit_events": [row.event_type for row in audit_rows],
            }

    mrv_id = mrv_by_packet_id.get(packet_id)
    value_id = value_by_mrv_id.get(mrv_id) if mrv_id else None
    evidence = get_evidence_by_packet(packet_id)
    audit_rows = audit_events.get(packet_id, [])
    return {
        "packet_id": packet_id,
        "evidence_id": evidence.get("evidence_id") if evidence else None,
        "mrv_id": mrv_id,
        "value_id": value_id,
        "traceability_status": "COMPLETE" if packet_id and mrv_id and value_id and audit_rows else "BROKEN",
        "audit_events": [event.event_type for event in audit_rows],
    }


def get_traceability_by_mrv(mrv_id: str) -> dict[str, Any]:
    with session_scope() as session:
        if session is not None:
            mrv_row = session.query(MRVResultModel).filter(MRVResultModel.mrv_id == mrv_id).first()
            value_row = session.query(CarbonValueResultModel).filter(CarbonValueResultModel.mrv_id == mrv_id).first() if mrv_row else None
            audit_rows = (
                session.query(AuditLogModel)
                .filter(AuditLogModel.packet_id == mrv_row.packet_id)
                .order_by(AuditLogModel.created_at.asc())
                .all()
            ) if mrv_row else []
            return {
                "packet_id": mrv_row.packet_id if mrv_row else None,
                "evidence_id": mrv_row.evidence_id if mrv_row else None,
                "mrv_id": mrv_id,
                "value_id": value_row.value_id if value_row else None,
                "traceability_status": "COMPLETE" if mrv_row and value_row and audit_rows else "BROKEN",
                "audit_events": [row.event_type for row in audit_rows],
            }

    mrv_result = mrv_results.get(mrv_id)
    packet_id = mrv_result["packet_id"] if mrv_result else None
    evidence = get_evidence_by_packet(packet_id) if packet_id else None
    value_id = value_by_mrv_id.get(mrv_id)
    audit_rows = audit_events.get(packet_id, []) if packet_id else []
    return {
        "packet_id": packet_id,
        "evidence_id": evidence.get("evidence_id") if evidence else None,
        "mrv_id": mrv_id,
        "value_id": value_id,
        "traceability_status": "COMPLETE" if packet_id and mrv_id and value_id and audit_rows else "BROKEN",
        "audit_events": [event.event_type for event in audit_rows],
    }


def _model_to_dict(row: Any) -> dict[str, Any]:
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def get_trace_detail(packet_id: str) -> dict[str, Any]:
    with session_scope() as session:
        if session is not None:
            trust_row = session.query(TrustPacketModel).filter(TrustPacketModel.packet_id == packet_id).first()
            mrv_row = session.query(MRVResultModel).filter(MRVResultModel.packet_id == packet_id).first()
            evidence_row = get_evidence_by_packet(packet_id)
            value_row = None
            if mrv_row:
                value_row = (
                    session.query(CarbonValueResultModel)
                    .filter(CarbonValueResultModel.mrv_id == mrv_row.mrv_id)
                    .first()
                )
            reject_rows = session.query(RejectLogModel).filter(RejectLogModel.packet_id == packet_id).all()
            audit_rows = (
                session.query(AuditLogModel)
                .filter(AuditLogModel.packet_id == packet_id)
                .order_by(AuditLogModel.created_at.asc())
                .all()
            )
            if reject_rows:
                traceability_status = "REJECTED"
            elif trust_row and mrv_row and value_row and audit_rows:
                traceability_status = "COMPLETE"
            elif trust_row and mrv_row and not value_row:
                traceability_status = "MRV_ONLY"
            else:
                traceability_status = "BROKEN"
            return {
                "packet_id": packet_id,
                "trust_packet": trust_row.raw_packet if trust_row else None,
                "evidence": evidence_row,
                "mrv": _model_to_dict(mrv_row) if mrv_row else None,
                "carbon_value": _model_to_dict(value_row) if value_row else None,
                "audit_events": [_model_to_dict(row) for row in audit_rows],
                "reject_log": [_model_to_dict(row) for row in reject_rows],
                "traceability_status": traceability_status,
            }

    trust_packet = trust_packets.get(packet_id)
    evidence_row = get_evidence_by_packet(packet_id)
    mrv_id = mrv_by_packet_id.get(packet_id)
    mrv_result = mrv_results.get(mrv_id) if mrv_id else None
    value_id = value_by_mrv_id.get(mrv_id) if mrv_id else None
    value_result = carbon_value_results.get(value_id) if value_id else None
    packet_rejects = [reject.model_dump() for reject in reject_logs if reject.packet_id == packet_id]
    packet_audits = [event.model_dump() for event in audit_events.get(packet_id, [])]
    if packet_rejects:
        traceability_status = "REJECTED"
    elif trust_packet and mrv_result and value_result and packet_audits:
        traceability_status = "COMPLETE"
    elif trust_packet and mrv_result and not value_result:
        traceability_status = "MRV_ONLY"
    else:
        traceability_status = "BROKEN"
    return {
        "packet_id": packet_id,
        "trust_packet": trust_packet.model_dump() if trust_packet else None,
        "evidence": evidence_row,
        "mrv": mrv_result,
        "carbon_value": value_result,
        "audit_events": packet_audits,
        "reject_log": packet_rejects,
        "traceability_status": traceability_status,
    }


def get_full_trace_detail(packet_id: str) -> dict[str, Any]:
    trace = get_trace_detail(packet_id)
    trust_packet = trace.get("trust_packet")
    payload = trust_packet.get("payload", {}) if isinstance(trust_packet, dict) else {}

    taxi_operation = next(
        (operation for operation in taxi_daily_operations.values() if operation.get("packet_id") == packet_id),
        None,
    )
    taxi_mrv_id = taxi_mrv_by_packet_id.get(packet_id)
    taxi_mrv = taxi_mrv_results.get(taxi_mrv_id) if taxi_mrv_id else None
    verification_id = verification_by_packet_id.get(packet_id)
    verification = mrv_verification_records.get(verification_id) if verification_id else None
    candidate_id = carbon_asset_candidate_by_mrv_id.get(taxi_mrv_id) if taxi_mrv_id else None
    candidate = carbon_asset_candidates.get(candidate_id) if candidate_id else None

    if taxi_mrv:
        mrv = taxi_mrv
        mrv_id = taxi_mrv.get("mrv_id")
        carbon_value = {
            "value_id": taxi_operation.get("value_id") if taxi_operation else None,
            "estimated_value_krw": candidate.get("estimated_value_krw") if candidate else 0,
            "estimated_value_usd": candidate.get("estimated_value_usd") if candidate else 0,
            "currency": "KRW",
            "source": "taxi_mrv_candidate_estimate",
            "status": "ESTIMATED" if candidate else "NOT_CREATED",
        }
        asset = candidate
    else:
        mrv = trace.get("mrv")
        mrv_id = mrv.get("mrv_id") if isinstance(mrv, dict) else None
        carbon_value = trace.get("carbon_value")
        value_id = value_by_mrv_id.get(mrv_id) if mrv_id else None
        candidate_id = carbon_asset_candidate_by_mrv_id.get(mrv_id) if mrv_id else None
        asset = carbon_asset_candidates.get(candidate_id) if candidate_id else None
        if carbon_value and not carbon_value.get("value_id"):
            carbon_value["value_id"] = value_id

    value_id = None
    if isinstance(carbon_value, dict):
        value_id = carbon_value.get("value_id")
    asset_id = asset.get("candidate_id") if asset else None
    registry_status = asset.get("registry_status") if asset else "NOT_READY"
    registry_ready = bool(asset and asset.get("candidate_status") in {"CANDIDATE", "UNDER_REVIEW", "ELIGIBLE_FOR_REGISTRY"})
    registry_id = asset.get("registry_id") if asset else None

    if trace.get("reject_log"):
        status = "REJECTED"
    elif trust_packet and trace.get("evidence") and mrv and verification and asset:
        status = "REGISTRY_READY"
    elif trust_packet and trace.get("evidence") and mrv and verification:
        status = "VERIFIED_NO_ASSET"
    elif trust_packet and trace.get("evidence") and mrv:
        status = "MRV_ONLY"
    elif trust_packet and trace.get("evidence"):
        status = "EVIDENCE_ONLY"
    elif trust_packet:
        status = "PACKET_ONLY"
    else:
        status = "BROKEN"

    demo_steps = [
        {
            "step": 1,
            "title": "Taxi Data",
            "status": "READY" if trust_packet else "MISSING",
            "vehicle_id": payload.get("vehicle_id") or (taxi_operation or {}).get("vehicle_id"),
            "distance_km": payload.get("distance_km") or (taxi_operation or {}).get("distance_km"),
            "daily_revenue": payload.get("daily_revenue") or (taxi_operation or {}).get("daily_revenue"),
            "driver_id": payload.get("driver_id") or (taxi_operation or {}).get("driver_id"),
        },
        {
            "step": 2,
            "title": "Evidence",
            "status": "VERIFIED" if trace.get("evidence") else "BLOCKED",
            "packet_id": packet_id,
            "evidence_id": (trace.get("evidence") or {}).get("evidence_id"),
            "hash": (trust_packet or {}).get("payload_hash") if isinstance(trust_packet, dict) else None,
            "signature": (trust_packet or {}).get("signature") if isinstance(trust_packet, dict) else None,
        },
        {
            "step": 3,
            "title": "MRV",
            "status": "MRV_SUCCESS" if mrv else "BLOCKED",
            "mrv_id": mrv_id,
            "distance_km": (mrv or {}).get("distance_km"),
            "reduction_kgco2e": (mrv or {}).get("reduction_co2e_kg") or (mrv or {}).get("co2e_kg"),
        },
        {
            "step": 4,
            "title": "Verification",
            "status": (verification or {}).get("verification_status", "PENDING"),
            "verification_id": (verification or {}).get("verification_id"),
            "verification_score": (verification or {}).get("verification_score"),
        },
        {
            "step": 5,
            "title": "Asset Candidate",
            "status": (asset or {}).get("candidate_status", "NOT_CREATED"),
            "asset_id": asset_id,
            "serial_number": (asset or {}).get("serial_number"),
            "reduction": (asset or {}).get("issued_quantity_tco2e"),
            "estimated_value_krw": (asset or {}).get("estimated_value_krw"),
        },
        {
            "step": 6,
            "title": "Registry",
            "status": "READY" if registry_ready else registry_status,
            "registry_id": registry_id,
            "registry_status": registry_status,
            "snapshot_stored": bool(asset),
        },
    ]

    return {
        "packet_id": packet_id,
        "evidence_id": (trace.get("evidence") or {}).get("evidence_id"),
        "mrv_id": mrv_id,
        "verification_id": (verification or {}).get("verification_id"),
        "value_id": value_id,
        "asset_id": asset_id,
        "registry_id": registry_id,
        "traceability_status": status,
        "trust_packet": trust_packet,
        "evidence": trace.get("evidence"),
        "mrv": mrv,
        "verification": verification,
        "carbon_value": carbon_value,
        "asset_candidate": asset,
        "registry": {
            "registry_status": registry_status,
            "registry_id": registry_id,
            "ready_for_registry": registry_ready,
            "snapshot_stored": bool(asset),
            "next_status": "SUBMITTED_TO_REGISTRY" if registry_ready else None,
        },
        "audit_events": trace.get("audit_events", []),
        "reject_log": trace.get("reject_log", []),
        "demo_steps": demo_steps,
        "demo_message": "Packet -> Evidence -> MRV -> Verification -> Asset Candidate -> Registry Ready",
    }


def get_dashboard_summary() -> dict[str, Any]:
    with session_scope() as session:
        if session is not None:
            packet_rows = session.query(TrustPacketModel).all()
            mrv_rows = session.query(MRVResultModel).all()
            value_rows = session.query(CarbonValueResultModel).all()
            reject_count = session.query(RejectLogModel).count()
            latest_packet = packet_rows[-1] if packet_rows else None
            return {
                "source": "postgres",
                "total_packets": len(packet_rows),
                "verified_packets": sum(1 for row in packet_rows if row.validation_status == "VALIDATED"),
                "failed_packets": reject_count,
                "total_co2e_ton": sum(row.co2e_ton for row in mrv_rows),
                "estimated_carbon_value": sum(row.estimated_value for row in value_rows if row.status == "SUCCESS"),
                "trust_status": "ACTIVE" if packet_rows else "NO_DATA",
                "latest_packet_id": latest_packet.packet_id if latest_packet else None,
            }

    latest_packet_id = next(reversed(trust_packets.keys()), None) if trust_packets else None
    taxi_reduction_tco2e = sum(
        float(result.get("reduction_co2e_kg", 0) or 0) / 1000
        for result in taxi_mrv_results.values()
    )
    taxi_estimated_value = sum(
        float(candidate.get("estimated_value_krw", 0) or 0)
        for candidate in carbon_asset_candidates.values()
    )
    sensor_reduction_tco2e = sum(result["co2e_ton"] for result in mrv_results.values())
    sensor_estimated_value = sum(
        result["estimated_value"]
        for result in carbon_value_results.values()
        if result.get("status", "SUCCESS") == "SUCCESS"
    )
    return {
        "source": "memory_fallback",
        "total_packets": len(trust_packets),
        "verified_packets": sum(1 for packet in trust_packets.values() if packet.validation_status == "VALIDATED"),
        "failed_packets": len(reject_logs),
        "total_co2e_ton": sensor_reduction_tco2e + taxi_reduction_tco2e,
        "estimated_carbon_value": sensor_estimated_value + taxi_estimated_value,
        "taxi_mrv_count": len(taxi_mrv_results),
        "asset_candidate_count": len(carbon_asset_candidates),
        "sensor_mrv_count": len(mrv_results),
        "trust_status": "ACTIVE" if trust_packets else "NO_DATA",
        "latest_packet_id": latest_packet_id,
    }
