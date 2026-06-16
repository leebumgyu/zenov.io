from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from ..storage import (
    partner_api_keys,
    partner_data_mappings,
    partner_health_logs,
    partner_integrations,
    partners,
    save_partner_api_key_memory,
    save_partner_health_log_memory,
    save_partner_integration_memory,
    save_partner_mapping_memory,
    save_partner_memory,
)
from .postgres import is_postgres_configured, session_scope, text
from ..services.mobility_solar_carbon_engine import (
    calculate_ev_taxi_solar_reduction,
    calculate_project_revenue,
    get_carbon_factor_config,
)


PARTNER_PIPELINE_STORE = (
    Path(__file__).resolve().parents[3]
    / "outputs"
    / "zenov-mobility-data-platform"
    / "data"
    / "partner_pipeline_store.json"
)


ALLOWED_PIPELINE_STATUSES = [
    "NEW",
    "QUESTIONNAIRE_SUBMITTED",
    "UNDER_REVIEW",
    "MEETING_SCHEDULED",
    "MEETING_READY",
    "PROPOSAL_IN_PROGRESS",
    "PROPOSAL_READY",
    "PROPOSAL_SENT",
    "PROPOSAL_VIEWED",
    "FEEDBACK_RECEIVED",
    "CONTRACT_IN_PROGRESS",
    "CONTRACT_REVIEW",
    "CONTRACT_READY",
    "ONBOARDING_READY",
    "DATA_ONBOARDING",
    "DATA_CONNECTED",
    "OPERATING",
]
EXCEPTION_STATUSES = {"HOLD", "REJECTED"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10].upper()}"


def _json(value: Any) -> str:
    return json.dumps(value or {}, ensure_ascii=False)


def _list_json(value: Any) -> str:
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str) and value:
        return json.dumps([item.strip() for item in value.split(",") if item.strip()], ensure_ascii=False)
    return "[]"


def _read_file_store() -> dict[str, Any]:
    if not PARTNER_PIPELINE_STORE.exists():
        return {"partners": {}}
    try:
        return json.loads(PARTNER_PIPELINE_STORE.read_text(encoding="utf-8"))
    except Exception:
        return {"partners": {}}


def _write_file_store(store: dict[str, Any]) -> None:
    PARTNER_PIPELINE_STORE.parent.mkdir(parents=True, exist_ok=True)
    PARTNER_PIPELINE_STORE.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def _save_file_partner(partner: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("partners", {})
    store["partners"][partner["partner_id"]] = partner
    store["updated_at"] = _now()
    _write_file_store(store)
    return partner


def _get_file_partner(partner_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("partners", {}).get(partner_id)


def _list_file_partners() -> list[dict[str, Any]]:
    return list(_read_file_store().get("partners", {}).values())


def _save_file_action_command(command: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("action_commands", {})
    store["action_commands"][command["action_id"]] = command
    store["updated_at"] = _now()
    _write_file_store(store)
    return command


def _list_file_action_commands() -> list[dict[str, Any]]:
    return list(_read_file_store().get("action_commands", {}).values())


def _get_file_action_command(action_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("action_commands", {}).get(action_id)


def _save_file_business_project(project: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("business_projects", {})
    store["business_projects"][project["project_id"]] = project
    store["updated_at"] = _now()
    _write_file_store(store)
    return project


def _list_file_business_projects() -> list[dict[str, Any]]:
    return list(_read_file_store().get("business_projects", {}).values())


def _get_file_business_project(project_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("business_projects", {}).get(project_id)


def _save_file_program(program: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("programs", {})
    store["programs"][program["program_id"]] = program
    store["updated_at"] = _now()
    _write_file_store(store)
    return program


def _list_file_programs() -> list[dict[str, Any]]:
    return list(_read_file_store().get("programs", {}).values())


def _get_file_program(program_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("programs", {}).get(program_id)


def _save_file_credit_readiness(readiness: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("credit_readiness", {})
    store["credit_readiness"][readiness["project_id"]] = readiness
    store["updated_at"] = _now()
    _write_file_store(store)
    return readiness


def _list_file_credit_readiness() -> list[dict[str, Any]]:
    return list(_read_file_store().get("credit_readiness", {}).values())


def _get_file_credit_readiness(project_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("credit_readiness", {}).get(project_id)


def _save_file_carbon_economy(economy: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("carbon_economy", {})
    store["carbon_economy"][economy["project_id"]] = economy
    store["updated_at"] = _now()
    _write_file_store(store)
    return economy


def _list_file_carbon_economy() -> list[dict[str, Any]]:
    return list(_read_file_store().get("carbon_economy", {}).values())


def _get_file_carbon_economy(project_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("carbon_economy", {}).get(project_id)


def _save_file_transformation(transformation: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("transformations", {})
    store["transformations"][transformation["partner_id"]] = transformation
    store["updated_at"] = _now()
    _write_file_store(store)
    return transformation


def _list_file_transformations() -> list[dict[str, Any]]:
    return list(_read_file_store().get("transformations", {}).values())


def _get_file_transformation(partner_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("transformations", {}).get(partner_id)


def _save_file_transformation_report(report: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("transformation_reports", {})
    store["transformation_reports"][report["partner_id"]] = report
    store["updated_at"] = _now()
    _write_file_store(store)
    return report


def _get_file_transformation_report(partner_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("transformation_reports", {}).get(partner_id)


def _save_file_golden_template(certification: dict[str, Any]) -> dict[str, Any]:
    store = _read_file_store()
    store.setdefault("golden_templates", {})
    store["golden_templates"][certification["partner_id"]] = certification
    store["updated_at"] = _now()
    _write_file_store(store)
    return certification


def _get_file_golden_template(partner_id: str) -> Optional[dict[str, Any]]:
    return _read_file_store().get("golden_templates", {}).get(partner_id)


def _list_file_golden_templates() -> list[dict[str, Any]]:
    return list(_read_file_store().get("golden_templates", {}).values())


def validate_partner_pipeline(payload: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    mobility = payload.get("mobility") or {}
    energy = payload.get("energy") or {}
    company_name = str(payload.get("company_name") or "").strip()
    business_type = str(payload.get("business_type") or "").strip()
    contact_email = str(payload.get("contact_email") or "").strip()
    if not company_name:
        errors.append({"field": "company_name", "reason_code": "COMPANY_NAME_REQUIRED", "message": "company_name is required."})
    if not business_type:
        errors.append({"field": "business_type", "reason_code": "BUSINESS_TYPE_REQUIRED", "message": "business_type is required."})
    if contact_email and ("@" not in contact_email or "." not in contact_email.split("@")[-1]):
        errors.append({"field": "contact_email", "reason_code": "INVALID_EMAIL", "message": "contact_email format is invalid."})
    numeric_fields = [
        ("taxi_count", mobility.get("taxi_count")),
        ("ev_taxi_count", mobility.get("ev_taxi_count")),
        ("bus_count", mobility.get("bus_count")),
        ("ev_bus_count", mobility.get("ev_bus_count")),
        ("solar_capacity_kw", energy.get("solar_capacity_kw")),
        ("charger_count", energy.get("charger_count")),
    ]
    for field, value in numeric_fields:
        if value is not None and float(value or 0) < 0:
            errors.append({"field": field, "reason_code": "NEGATIVE_VALUE", "message": f"{field} cannot be negative."})
    if float(mobility.get("ev_taxi_count") or 0) > float(mobility.get("taxi_count") or 0):
        errors.append({"field": "ev_taxi_count", "reason_code": "EV_TAXI_GT_TAXI", "message": "ev_taxi_count must be <= taxi_count."})
    if float(mobility.get("ev_bus_count") or 0) > float(mobility.get("bus_count") or 0):
        errors.append({"field": "ev_bus_count", "reason_code": "EV_BUS_GT_BUS", "message": "ev_bus_count must be <= bus_count."})
    return errors


def assert_status_transition(old_status: str | None, new_status: str) -> None:
    if new_status in EXCEPTION_STATUSES:
        return
    if not old_status or old_status == new_status:
        return
    if old_status in EXCEPTION_STATUSES:
        raise ValueError("INVALID_STATUS_TRANSITION")
    try:
        old_index = ALLOWED_PIPELINE_STATUSES.index(old_status)
        new_index = ALLOWED_PIPELINE_STATUSES.index(new_status)
    except ValueError as exc:
        raise ValueError("INVALID_STATUS") from exc
    if new_index < old_index:
        raise ValueError("INVALID_STATUS_TRANSITION")


def save_partner(partner: dict[str, Any]) -> dict[str, Any]:
    save_partner_memory(partner)
    return partner


def get_partner(partner_id: str) -> Optional[dict[str, Any]]:
    return partners.get(partner_id)


def list_partners() -> list[dict[str, Any]]:
    return list(partners.values())


def save_partner_api_key(api_key: dict[str, Any]) -> dict[str, Any]:
    save_partner_api_key_memory(api_key)
    return api_key


def get_partner_api_keys(partner_id: str) -> list[dict[str, Any]]:
    return [key for key in partner_api_keys.values() if key.get("partner_id") == partner_id]


def save_partner_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    save_partner_mapping_memory(mapping)
    return mapping


def get_partner_mappings(partner_id: str) -> list[dict[str, Any]]:
    return [mapping for mapping in partner_data_mappings.values() if mapping.get("partner_id") == partner_id]


def find_partner_mapping(partner_id: str, source_type: str) -> Optional[dict[str, Any]]:
    for mapping in partner_data_mappings.values():
        if mapping.get("partner_id") == partner_id and mapping.get("source_type") == source_type:
            return mapping
    return None


def save_partner_integration(integration: dict[str, Any]) -> dict[str, Any]:
    save_partner_integration_memory(integration)
    return integration


def get_partner_integrations(partner_id: str) -> list[dict[str, Any]]:
    return [
        integration
        for integration in partner_integrations.values()
        if integration.get("partner_id") == partner_id
    ]


def save_health_log(log: dict[str, Any]) -> dict[str, Any]:
    save_partner_health_log_memory(log)
    return log


def get_partner_health_logs(partner_id: str) -> list[dict[str, Any]]:
    return [log for log in partner_health_logs if log.get("partner_id") == partner_id]


def _memory_pipeline_partner(payload: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    partner_id = payload.get("partner_id") or _id("PTR")
    previous = partners.get(partner_id, {})
    status = payload.get("status") or "NEW"
    assert_status_transition(previous.get("status"), status)
    item = {**previous, **payload, "partner_id": partner_id, "updated_at": _now()}
    item.setdefault("created_at", previous.get("created_at") or _now())
    item.setdefault("audit_logs", [])
    item["audit_logs"].append({
        "log_id": _id("PAL"),
        "partner_id": partner_id,
        "event_type": "PARTNER_PIPELINE_SAVED",
        "old_value": previous.get("status", "-"),
        "new_value": status,
        "changed_by": actor,
        "created_at": _now(),
    })
    save_partner_memory(item)
    _save_file_partner(item)
    return item


def save_partner_pipeline(payload: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    errors = validate_partner_pipeline(payload)
    if errors:
        _save_pipeline_audit_memory(payload.get("partner_id") or "UNKNOWN", "VALIDATION_FAILED", "-", json.dumps(errors, ensure_ascii=False), actor)
        raise ValueError(json.dumps({"reason_code": "VALIDATION_FAILED", "errors": errors}, ensure_ascii=False))
    if not is_postgres_configured():
        return _memory_pipeline_partner(payload, actor)
    partner_id = payload.get("partner_id") or _id("PTR")
    with session_scope() as session:
        previous = session.execute(
            text("SELECT status FROM partners WHERE partner_id = :partner_id"),
            {"partner_id": partner_id},
        ).mappings().first()
        old_status = previous["status"] if previous else None
        new_status = payload.get("status") or old_status or "NEW"
        assert_status_transition(old_status, new_status)
        session.execute(
            text(
                """
                INSERT INTO partners (
                  partner_id, partner_name, partner_type, source_system, data_format, lifecycle_status,
                  company_name, business_type, contact_name, contact_phone, contact_email, region,
                  status, owner_id, created_at, updated_at
                )
                VALUES (
                  :partner_id, :partner_name, :partner_type, 'PARTNER_PIPELINE', 'WEB_FORM', 'ACTIVE',
                  :company_name, :business_type, :contact_name, :contact_phone, :contact_email, :region,
                  :status, :owner_id, NOW(), NOW()
                )
                ON CONFLICT (partner_id) DO UPDATE SET
                  partner_name = EXCLUDED.partner_name,
                  partner_type = EXCLUDED.partner_type,
                  company_name = EXCLUDED.company_name,
                  business_type = EXCLUDED.business_type,
                  contact_name = EXCLUDED.contact_name,
                  contact_phone = EXCLUDED.contact_phone,
                  contact_email = EXCLUDED.contact_email,
                  region = EXCLUDED.region,
                  status = EXCLUDED.status,
                  owner_id = EXCLUDED.owner_id,
                  lifecycle_status = 'ACTIVE',
                  updated_at = NOW()
                """
            ),
            {
                "partner_id": partner_id,
                "partner_name": payload.get("company_name") or partner_id,
                "partner_type": payload.get("business_type") or "TAXI_COMPANY",
                "company_name": payload.get("company_name"),
                "business_type": payload.get("business_type"),
                "contact_name": payload.get("contact_name"),
                "contact_phone": payload.get("contact_phone"),
                "contact_email": payload.get("contact_email"),
                "region": payload.get("region"),
                "status": new_status,
                "owner_id": (payload.get("owner") or {}).get("owner_name") or actor,
            },
        )
        questionnaire = {
            "questionnaire_id": payload.get("questionnaire_id") or _id("QNR"),
            "partner_id": partner_id,
            "mobility_json": _json(payload.get("mobility")),
            "energy_json": _json(payload.get("energy")),
            "carbon_json": _json(payload.get("carbon_esg")),
            "documents_json": _json(payload.get("documents")),
        }
        session.execute(
            text(
                """
                INSERT INTO questionnaires (questionnaire_id, partner_id, mobility_json, energy_json, carbon_json, documents_json, submitted_at)
                VALUES (:questionnaire_id, :partner_id, CAST(:mobility_json AS JSONB), CAST(:energy_json AS JSONB), CAST(:carbon_json AS JSONB), CAST(:documents_json AS JSONB), NOW())
                """
            ),
            questionnaire,
        )
        action = payload.get("next_action") or {}
        if action.get("action_title"):
            session.execute(
                text(
                    """
                    INSERT INTO partner_actions (action_id, partner_id, action_title, action_status, owner_id, due_date, memo, created_at, updated_at)
                    VALUES (:action_id, :partner_id, :action_title, :action_status, :owner_id, CAST(NULLIF(:due_date, '') AS DATE), :memo, NOW(), NOW())
                    ON CONFLICT (action_id) DO UPDATE SET
                      action_title = EXCLUDED.action_title,
                      action_status = EXCLUDED.action_status,
                      owner_id = EXCLUDED.owner_id,
                      due_date = EXCLUDED.due_date,
                      memo = EXCLUDED.memo,
                      updated_at = NOW()
                    """
                ),
                {
                    "action_id": action.get("action_id") or _id("ACT"),
                    "partner_id": partner_id,
                    "action_title": action.get("action_title"),
                    "action_status": action.get("action_status") or "TODO",
                    "owner_id": action.get("owner") or actor,
                    "due_date": action.get("due_date") or "",
                    "memo": action.get("memo"),
                },
            )
        meeting = payload.get("meeting") or {}
        if meeting.get("meeting_date") or meeting.get("meeting_status"):
            session.execute(
                text(
                    """
                    INSERT INTO meetings (meeting_id, partner_id, meeting_date, meeting_type, location, attendees_json, meeting_status, memo, created_at)
                    VALUES (:meeting_id, :partner_id, CAST(NULLIF(:meeting_date, '') AS DATE), :meeting_type, :location, CAST(:attendees_json AS JSONB), :meeting_status, :memo, NOW())
                    ON CONFLICT (meeting_id) DO NOTHING
                    """
                ),
                {
                    "meeting_id": meeting.get("meeting_id") or _id("MTG"),
                    "partner_id": partner_id,
                    "meeting_date": meeting.get("meeting_date") or "",
                    "meeting_type": meeting.get("meeting_type"),
                    "location": meeting.get("meeting_location") or meeting.get("location"),
                    "attendees_json": _list_json(meeting.get("attendees")),
                    "meeting_status": meeting.get("meeting_status") or "REQUESTED",
                    "memo": meeting.get("meeting_memo") or meeting.get("memo"),
                },
            )
        proposal = payload.get("proposal") or {}
        if proposal.get("proposal_id") or proposal.get("proposal_status"):
            session.execute(
                text(
                    """
                    INSERT INTO proposals (proposal_id, partner_id, proposal_type, proposal_status, proposal_file_url, sent_date, feedback, created_at, updated_at)
                    VALUES (:proposal_id, :partner_id, :proposal_type, :proposal_status, :proposal_file_url, CAST(NULLIF(:sent_date, '') AS DATE), :feedback, NOW(), NOW())
                    ON CONFLICT (proposal_id) DO UPDATE SET
                      proposal_type = EXCLUDED.proposal_type,
                      proposal_status = EXCLUDED.proposal_status,
                      proposal_file_url = EXCLUDED.proposal_file_url,
                      sent_date = EXCLUDED.sent_date,
                      feedback = EXCLUDED.feedback,
                      updated_at = NOW()
                    """
                ),
                {
                    "proposal_id": proposal.get("proposal_id") or _id("PRP"),
                    "partner_id": partner_id,
                    "proposal_type": proposal.get("proposal_type"),
                    "proposal_status": proposal.get("proposal_status") or "NOT_STARTED",
                    "proposal_file_url": proposal.get("proposal_file") or proposal.get("proposal_file_url"),
                    "sent_date": proposal.get("sent_date") or "",
                    "feedback": proposal.get("feedback"),
                },
            )
        execution = payload.get("sales_execution") or {}
        send_log = execution.get("send_log") or {}
        view_tracking = execution.get("view_tracking") or {}
        feedback_log = execution.get("feedback_log") or {}
        if execution:
            session.execute(
                text(
                    """
                    INSERT INTO sales_execution (execution_id, partner_id, send_status, view_status, feedback_type, conversion_score, followup_status, execution_json, created_at, updated_at)
                    VALUES (:execution_id, :partner_id, :send_status, :view_status, :feedback_type, :conversion_score, :followup_status, CAST(:execution_json AS JSONB), NOW(), NOW())
                    ON CONFLICT (execution_id) DO UPDATE SET
                      send_status = EXCLUDED.send_status,
                      view_status = EXCLUDED.view_status,
                      feedback_type = EXCLUDED.feedback_type,
                      conversion_score = EXCLUDED.conversion_score,
                      followup_status = EXCLUDED.followup_status,
                      execution_json = EXCLUDED.execution_json,
                      updated_at = NOW()
                    """
                ),
                {
                    "execution_id": execution.get("execution_id") or f"EXEC-{partner_id}",
                    "partner_id": partner_id,
                    "send_status": send_log.get("send_status") or "DRAFT",
                    "view_status": view_tracking.get("view_status") or "NOT_OPENED",
                    "feedback_type": feedback_log.get("feedback_type"),
                    "conversion_score": execution.get("conversion_score") or 0,
                    "followup_status": "TODO" if execution.get("follow_up_actions") else "NONE",
                    "execution_json": _json(execution),
                },
            )
        success = payload.get("partner_success") or {}
        monthly = success.get("monthly_performance") or {}
        health = success.get("customer_health") or {}
        expansion = success.get("expansion_opportunity") or {}
        renewal = success.get("renewal_status") or {}
        report = success.get("monthly_report") or {}
        if success:
            session.execute(
                text(
                    """
                    INSERT INTO partner_success (
                      success_id, partner_id, report_month, data_connected_days, packets_collected, valid_packets,
                      rejected_packets, estimated_co2e, estimated_carbon_value, health_score, health_status,
                      expansion_value, renewal_probability, report_status, success_json, created_at, updated_at
                    )
                    VALUES (
                      :success_id, :partner_id, :report_month, :data_connected_days, :packets_collected, :valid_packets,
                      :rejected_packets, :estimated_co2e, :estimated_carbon_value, :health_score, :health_status,
                      :expansion_value, :renewal_probability, :report_status, CAST(:success_json AS JSONB), NOW(), NOW()
                    )
                    ON CONFLICT (partner_id, report_month) DO UPDATE SET
                      data_connected_days = EXCLUDED.data_connected_days,
                      packets_collected = EXCLUDED.packets_collected,
                      valid_packets = EXCLUDED.valid_packets,
                      rejected_packets = EXCLUDED.rejected_packets,
                      estimated_co2e = EXCLUDED.estimated_co2e,
                      estimated_carbon_value = EXCLUDED.estimated_carbon_value,
                      health_score = EXCLUDED.health_score,
                      health_status = EXCLUDED.health_status,
                      expansion_value = EXCLUDED.expansion_value,
                      renewal_probability = EXCLUDED.renewal_probability,
                      report_status = EXCLUDED.report_status,
                      success_json = EXCLUDED.success_json,
                      updated_at = NOW()
                    """
                ),
                {
                    "success_id": _id("PSC"),
                    "partner_id": partner_id,
                    "report_month": monthly.get("report_month") or datetime.utcnow().strftime("%Y-%m"),
                    "data_connected_days": monthly.get("data_connected_days") or 0,
                    "packets_collected": monthly.get("packets_collected") or 0,
                    "valid_packets": monthly.get("valid_packets") or 0,
                    "rejected_packets": monthly.get("rejected_packets") or 0,
                    "estimated_co2e": monthly.get("estimated_co2e") or 0,
                    "estimated_carbon_value": monthly.get("estimated_carbon_value") or 0,
                    "health_score": health.get("health_score") or 0,
                    "health_status": health.get("health_status") or "WATCH",
                    "expansion_value": expansion.get("estimated_additional_value") or 0,
                    "renewal_probability": renewal.get("renewal_probability") or 0,
                    "report_status": report.get("report_status") or "NOT_CREATED",
                    "success_json": _json(success),
                },
            )
        if old_status != new_status:
            session.execute(
                text(
                    """
                    INSERT INTO partner_status_history (history_id, partner_id, old_status, new_status, changed_by, changed_at)
                    VALUES (:history_id, :partner_id, :old_status, :new_status, :changed_by, NOW())
                    """
                ),
                {
                    "history_id": _id("PSH"),
                    "partner_id": partner_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "changed_by": actor,
                },
            )
        session.execute(
            text(
                """
                INSERT INTO partner_pipeline_audit_logs (log_id, partner_id, event_type, old_value, new_value, changed_by, created_at)
                VALUES (:log_id, :partner_id, 'PARTNER_PIPELINE_SAVED', :old_value, :new_value, :changed_by, NOW())
                """
            ),
            {
                "log_id": _id("PAL"),
                "partner_id": partner_id,
                "old_value": old_status or "-",
                "new_value": new_status,
                "changed_by": actor,
            },
        )
    return get_partner_pipeline(partner_id) or {**payload, "partner_id": partner_id}


def _save_pipeline_audit_memory(partner_id: str, event_type: str, old_value: str, new_value: str, actor: str) -> None:
    item = partners.get(partner_id, {"partner_id": partner_id})
    item.setdefault("audit_logs", [])
    item["audit_logs"].append({
        "log_id": _id("PAL"),
        "partner_id": partner_id,
        "event_type": event_type,
        "old_value": old_value,
        "new_value": new_value,
        "changed_by": actor,
        "created_at": _now(),
    })
    save_partner_memory(item)


def _row_to_partner(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "partner_id": row["partner_id"],
        "company_name": row.get("company_name") or row.get("partner_name"),
        "business_type": row.get("business_type") or row.get("partner_type"),
        "contact_name": row.get("contact_name"),
        "contact_phone": row.get("contact_phone"),
        "contact_email": row.get("contact_email"),
        "region": row.get("region"),
        "status": row.get("status") or row.get("lifecycle_status") or "NEW",
        "created_at": str(row.get("created_at")) if row.get("created_at") else None,
        "updated_at": str(row.get("updated_at")) if row.get("updated_at") else None,
    }


def get_partner_pipeline(partner_id: str) -> Optional[dict[str, Any]]:
    if not is_postgres_configured():
        return partners.get(partner_id) or _get_file_partner(partner_id)
    with session_scope() as session:
        row = session.execute(
            text("SELECT * FROM partners WHERE partner_id = :partner_id"),
            {"partner_id": partner_id},
        ).mappings().first()
        if not row:
            return None
        partner = _row_to_partner(dict(row))
        q = session.execute(
            text("SELECT * FROM questionnaires WHERE partner_id = :partner_id ORDER BY submitted_at DESC LIMIT 1"),
            {"partner_id": partner_id},
        ).mappings().first()
        if q:
            partner["mobility"] = q["mobility_json"]
            partner["energy"] = q["energy_json"]
            partner["carbon_esg"] = q["carbon_json"]
            partner["documents"] = q["documents_json"]
        action = session.execute(
            text("SELECT * FROM partner_actions WHERE partner_id = :partner_id ORDER BY updated_at DESC LIMIT 1"),
            {"partner_id": partner_id},
        ).mappings().first()
        if action:
            partner["next_action"] = dict(action)
        meeting = session.execute(
            text("SELECT * FROM meetings WHERE partner_id = :partner_id ORDER BY created_at DESC LIMIT 1"),
            {"partner_id": partner_id},
        ).mappings().first()
        if meeting:
            partner["meeting"] = dict(meeting)
        proposal = session.execute(
            text("SELECT * FROM proposals WHERE partner_id = :partner_id ORDER BY updated_at DESC LIMIT 1"),
            {"partner_id": partner_id},
        ).mappings().first()
        if proposal:
            partner["proposal"] = dict(proposal)
        execution = session.execute(
            text("SELECT * FROM sales_execution WHERE partner_id = :partner_id ORDER BY updated_at DESC LIMIT 1"),
            {"partner_id": partner_id},
        ).mappings().first()
        if execution:
            partner["sales_execution"] = execution["execution_json"]
        success = session.execute(
            text("SELECT * FROM partner_success WHERE partner_id = :partner_id ORDER BY report_month DESC LIMIT 1"),
            {"partner_id": partner_id},
        ).mappings().first()
        if success:
            partner["partner_success"] = success["success_json"]
        audits = session.execute(
            text("SELECT * FROM partner_pipeline_audit_logs WHERE partner_id = :partner_id ORDER BY created_at DESC LIMIT 50"),
            {"partner_id": partner_id},
        ).mappings().all()
        partner["audit_logs"] = [dict(item) for item in audits]
        return partner


def list_partner_pipeline() -> list[dict[str, Any]]:
    if not is_postgres_configured():
        combined = {item["partner_id"]: item for item in _list_file_partners() if item.get("partner_id")}
        combined.update({key: value for key, value in partners.items() if value.get("partner_id")})
        return list(combined.values())
    with session_scope() as session:
        rows = session.execute(text("SELECT partner_id FROM partners ORDER BY updated_at DESC NULLS LAST, created_at DESC")).mappings().all()
    return [item for item in (get_partner_pipeline(row["partner_id"]) for row in rows) if item]


def update_partner_pipeline(partner_id: str, patch: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    current = get_partner_pipeline(partner_id)
    if not current:
        raise ValueError("PARTNER_NOT_FOUND")
    merged = {**current, **patch, "partner_id": partner_id}
    for key in ("mobility", "energy", "carbon_esg", "documents", "owner", "next_action", "meeting", "proposal", "sales_execution", "partner_success"):
        if key in current or key in patch:
            merged[key] = {**(current.get(key) or {}), **(patch.get(key) or {})}
    return save_partner_pipeline(merged, actor)


def save_partner_questionnaire(partner_id: str, questionnaire: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    return update_partner_pipeline(
        partner_id,
        {
            "mobility": questionnaire.get("mobility") or questionnaire.get("mobility_json") or {},
            "energy": questionnaire.get("energy") or questionnaire.get("energy_json") or {},
            "carbon_esg": questionnaire.get("carbon_esg") or questionnaire.get("carbon_json") or {},
            "documents": questionnaire.get("documents") or questionnaire.get("documents_json") or {},
            "status": "QUESTIONNAIRE_SUBMITTED",
        },
        actor,
    )


def dashboard_partner_summary() -> dict[str, Any]:
    items = list_partner_pipeline()
    def status_count(status: str) -> int:
        return sum(1 for item in items if item.get("status") == status)
    def sum_nested(section: str, field: str) -> float:
        return sum(float((item.get(section) or {}).get(field) or 0) for item in items)
    success_items = [item.get("partner_success") or {} for item in items]
    monthly_created = sum(1 for item in success_items if (item.get("monthly_report") or {}).get("report_status") in {"CREATED", "SENT", "REVIEWED"})
    reports_sent = sum(1 for item in success_items if (item.get("monthly_report") or {}).get("report_status") in {"SENT", "REVIEWED"})
    health_scores = [float((item.get("customer_health") or {}).get("health_score") or 0) for item in success_items if (item.get("customer_health") or {}).get("health_score")]
    expansion_value = sum(float((item.get("expansion_opportunity") or {}).get("estimated_additional_value") or 0) for item in success_items)
    return {
        "storage_mode": "postgres" if is_postgres_configured() else "server_file_fallback",
        "partner_summary": {
            "total_partners": len(items),
            "new_partners": status_count("NEW"),
            "questionnaire_submitted": status_count("QUESTIONNAIRE_SUBMITTED"),
            "under_review": status_count("UNDER_REVIEW"),
            "meeting_scheduled": status_count("MEETING_SCHEDULED"),
            "proposal_in_progress": status_count("PROPOSAL_READY") + status_count("PROPOSAL_SENT") + status_count("PROPOSAL_VIEWED") + status_count("FEEDBACK_RECEIVED"),
            "contract_in_progress": status_count("CONTRACT_REVIEW") + status_count("CONTRACT_READY"),
            "operating_partners": status_count("OPERATING"),
        },
        "mobility_summary": {
            "total_taxi_count": sum_nested("mobility", "taxi_count"),
            "total_ev_taxi_count": sum_nested("mobility", "ev_taxi_count"),
            "total_bus_count": sum_nested("mobility", "bus_count"),
            "total_ev_bus_count": sum_nested("mobility", "ev_bus_count"),
        },
        "energy_summary": {
            "total_solar_capacity_kw": sum_nested("energy", "solar_capacity_kw"),
            "total_ess_capacity_kwh": sum_nested("energy", "ess_capacity_kwh"),
            "total_charger_count": sum_nested("energy", "charger_count"),
            "total_fast_charger_count": sum_nested("energy", "fast_charger_count"),
            "total_slow_charger_count": sum_nested("energy", "slow_charger_count"),
        },
        "partner_success": {
            "monthly_reports_created": monthly_created,
            "reports_sent": reports_sent,
            "average_customer_health_score": round(sum(health_scores) / len(health_scores), 2) if health_scores else 0,
            "at_risk_partners": sum(1 for item in success_items if (item.get("customer_health") or {}).get("health_status") in {"AT_RISK", "CHURN_RISK"}),
            "expansion_opportunities": sum(1 for item in success_items if (item.get("expansion_opportunity") or {}).get("recommendations")),
            "estimated_expansion_value": expansion_value,
        },
        "partners": items,
    }


def _clamp_score(value: float) -> int:
    return max(0, min(100, round(value or 0)))


def _nested_number(item: dict[str, Any], section: str, field: str) -> float:
    return float((item.get(section) or {}).get(field) or 0)


def _partner_opportunity(item: dict[str, Any]) -> dict[str, Any]:
    taxi_gap = max(0, _nested_number(item, "mobility", "taxi_count") - _nested_number(item, "mobility", "ev_taxi_count"))
    bus_gap = max(0, _nested_number(item, "mobility", "bus_count") - _nested_number(item, "mobility", "ev_bus_count"))
    motorcycle_gap = max(0, _nested_number(item, "mobility", "motorcycle_count") - _nested_number(item, "mobility", "ev_motorcycle_count"))
    logistics_gap = max(0, _nested_number(item, "mobility", "logistics_vehicle_count") - _nested_number(item, "mobility", "ev_logistics_vehicle_count"))
    charger_count = _nested_number(item, "energy", "charger_count")
    solar_capacity = _nested_number(item, "energy", "solar_capacity_kw")
    solar_installed = str((item.get("energy") or {}).get("solar_installed") or "").upper()
    solar_missing = solar_installed == "NO" or (solar_installed == "REVIEW" and solar_capacity == 0)
    carbon = item.get("carbon_esg") or {}
    mrv_interest = str(carbon.get("mrv_interest") or "").upper()
    credit_interest = str(carbon.get("carbon_credit_interest") or "").upper()
    mrv_candidate = mrv_interest in {"HIGH", "MEDIUM", "YES"} or credit_interest in {"HIGH", "MEDIUM", "YES"}
    estimated_co2e = float((item.get("opportunity") or {}).get("estimated_co2e_ton") or 0)
    if not estimated_co2e:
        estimated_co2e = round((taxi_gap * 3.2 + bus_gap * 18 + motorcycle_gap * 0.4 + logistics_gap * 8 + solar_capacity * 0.45) * 10) / 10
    estimated_value = float((item.get("opportunity") or {}).get("estimated_carbon_value_krw") or estimated_co2e * 17000)
    expected_project = (item.get("opportunity") or {}).get("expected_project") or carbon.get("expected_project_type") or (
        "EV_TAXI_MRV" if taxi_gap > 0 else "SOLAR_MRV" if solar_missing else "CARBON_MRV"
    )
    return {
        "taxi_gap": taxi_gap,
        "bus_gap": bus_gap,
        "motorcycle_gap": motorcycle_gap,
        "logistics_gap": logistics_gap,
        "ev_opportunity": taxi_gap + bus_gap + motorcycle_gap + logistics_gap,
        "charger_count": charger_count,
        "solar_capacity_kw": solar_capacity,
        "solar_missing": solar_missing,
        "mrv_candidate": mrv_candidate,
        "estimated_co2e": estimated_co2e,
        "estimated_value": estimated_value,
        "expected_project": expected_project,
    }


def partner_market_intelligence_summary() -> dict[str, Any]:
    items = list_partner_pipeline()
    intelligence_items = []
    for item in items:
        opportunity = _partner_opportunity(item)
        fleet_scale = (
            _nested_number(item, "mobility", "taxi_count")
            + _nested_number(item, "mobility", "bus_count") * 4
            + _nested_number(item, "mobility", "logistics_vehicle_count") * 2
            + _nested_number(item, "mobility", "motorcycle_count") * 0.2
        )
        carbon = item.get("carbon_esg") or {}
        mrv_interest = str(carbon.get("mrv_interest") or "").upper()
        credit_interest = str(carbon.get("carbon_credit_interest") or "").upper()
        interest_factor = (1 if mrv_interest in {"HIGH", "YES"} else 0.6 if mrv_interest == "MEDIUM" else 0) + (
            1 if credit_interest in {"HIGH", "YES"} else 0.6 if credit_interest == "MEDIUM" else 0
        )
        carbon_potential_score = _clamp_score(
            min(35, opportunity["estimated_co2e"] / 12)
            + min(25, opportunity["ev_opportunity"] / 5)
            + (15 if opportunity["solar_missing"] else min(15, opportunity["solar_capacity_kw"] / 50))
            + min(10, opportunity["charger_count"])
            + round(interest_factor * 7.5)
        )
        revenue_potential = round(
            3000000
            + opportunity["ev_opportunity"] * 250000
            + opportunity["charger_count"] * 120000
            + opportunity["solar_capacity_kw"] * 15000
            + opportunity["estimated_value"] * 0.08
        )
        revenue_potential_score = _clamp_score(revenue_potential / 500000)
        account_score = _clamp_score(
            min(30, fleet_scale / 5)
            + min(25, opportunity["ev_opportunity"] / 5)
            + min(20, opportunity["estimated_value"] / 1000000)
            + (15 if opportunity["mrv_candidate"] else 0)
            + (5 if opportunity["charger_count"] > 0 else 0)
            + (5 if opportunity["solar_missing"] else 0)
        )
        region_priority = 5 if str(item.get("region") or "").strip() in {"안산", "수원", "서울", "부산", "대구"} else 0
        opportunity_score = _clamp_score(account_score * 0.35 + carbon_potential_score * 0.35 + revenue_potential_score * 0.2 + region_priority)
        recommended_project = opportunity["expected_project"]
        if opportunity["ev_opportunity"] >= 100 and opportunity["solar_missing"] and opportunity["charger_count"] > 0:
            recommended_project = "EV_SOLAR_COMBINED"
        elif opportunity["ev_opportunity"] >= 50:
            recommended_project = "EV_TAXI_MRV"
        elif opportunity["solar_missing"]:
            recommended_project = "SOLAR_MRV"
        next_actions = []
        if opportunity_score >= 85:
            next_actions.append("대표 미팅 우선 배정")
        if opportunity["ev_opportunity"] >= 100:
            next_actions.append("EV Taxi Project 제안")
        if opportunity["solar_missing"] and opportunity["charger_count"] > 0:
            next_actions.append("Solar + Charger Project 제안")
        if opportunity["mrv_candidate"]:
            next_actions.append("MRV 프로젝트 제안")
        intelligence_items.append(
            {
                "partner_id": item.get("partner_id"),
                "company_name": item.get("company_name") or item.get("partner_id"),
                "region": item.get("region") or "-",
                "business_type": item.get("business_type") or "-",
                "opportunity_score": opportunity_score,
                "carbon_potential_score": carbon_potential_score,
                "account_score": account_score,
                "revenue_potential_krw": revenue_potential,
                "arr_potential_krw": round(revenue_potential * 0.35),
                "expansion_revenue_krw": round(revenue_potential * 0.45),
                "estimated_co2e_ton": opportunity["estimated_co2e"],
                "estimated_carbon_value_krw": opportunity["estimated_value"],
                "recommended_project": recommended_project,
                "next_action": next_actions[0] if next_actions else "기초 데이터 보완 후 재평가",
            }
        )
    top_accounts = sorted(
        intelligence_items,
        key=lambda row: (row["opportunity_score"], row["revenue_potential_krw"]),
        reverse=True,
    )[:10]
    return {
        "storage_mode": "postgres" if is_postgres_configured() else "server_file_fallback",
        "top_opportunities": top_accounts,
        "top_carbon_potential": sorted(intelligence_items, key=lambda row: row["carbon_potential_score"], reverse=True)[:10],
        "top_revenue_potential": sorted(intelligence_items, key=lambda row: row["revenue_potential_krw"], reverse=True)[:10],
        "top_priority_accounts": top_accounts,
    }


def _action_due_date(days: int = 3) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()


def _action_materials_for(command: dict[str, Any]) -> list[str]:
    materials = ["Zenov 소개자료", "예상 Carbon Value 리포트", "ROI 요약표"]
    project = command.get("recommended_project") or ""
    if "EV_TAXI" in project or command.get("ev_conversion_opportunity", 0) >= 50:
        materials.append("EV Taxi Carbon MRV 제안서")
    if "SOLAR" in project or command.get("solar_charging_project"):
        materials.append("Solar + EV Charging Carbon Project 제안서")
    return materials


def _build_action_command(item: dict[str, Any]) -> dict[str, Any]:
    action_title = item["next_action"]
    if item["opportunity_score"] >= 85:
        action_title = f"{item['company_name']} 대표 미팅 우선 배정"
    elif item.get("recommended_project") == "EV_SOLAR_COMBINED":
        action_title = f"{item['company_name']} Solar + EV Charging Carbon Project 제안"
    elif item.get("recommended_project") == "EV_TAXI_MRV":
        action_title = f"{item['company_name']} EV Taxi Carbon MRV 제안"
    command_seed = {
        **item,
        "ev_conversion_opportunity": round(item.get("estimated_co2e_ton", 0) / 3.2) if item.get("estimated_co2e_ton") else 0,
        "solar_charging_project": item.get("recommended_project") == "EV_SOLAR_COMBINED",
    }
    reason = (
        f"{item['company_name']}은 Opportunity Score {item['opportunity_score']}점, "
        f"Carbon Potential {item['carbon_potential_score']}점으로 우선 검토 대상입니다. "
        f"예상 감축량은 {round(item['estimated_co2e_ton'])}tCO2e, "
        f"예상 매출 잠재력은 {int(item['revenue_potential_krw']):,} KRW입니다."
    )
    priority = "HIGH" if item["opportunity_score"] >= 85 or item["revenue_potential_krw"] >= 30000000 else "MEDIUM"
    return {
        "action_id": f"CMD-{item['partner_id']}-{item['recommended_project']}".replace(" ", "-"),
        "partner_id": item["partner_id"],
        "partner_name": item["company_name"],
        "action_title": action_title,
        "action_reason": reason,
        "owner": "Ben",
        "due_date": _action_due_date(3),
        "required_materials": _action_materials_for(command_seed),
        "expected_outcome": ["대표 미팅 확정", "실데이터 제공 가능성 확인", "제안서 발송 승인"],
        "success_metric": ["미팅 일정 확정", "차량 데이터 제공 여부 확인", "충전기 데이터 제공 여부 확인"],
        "action_status": "TODO",
        "priority": priority,
        "opportunity_score": item["opportunity_score"],
        "carbon_potential_score": item["carbon_potential_score"],
        "revenue_potential_krw": item["revenue_potential_krw"],
        "recommended_project": item["recommended_project"],
        "created_at": _now(),
        "updated_at": _now(),
    }


def generate_action_commands(actor: str = "system") -> dict[str, Any]:
    summary = partner_market_intelligence_summary()
    generated = []
    for item in summary["top_priority_accounts"]:
        if item["opportunity_score"] < 70 and item["revenue_potential_krw"] < 30000000:
            continue
        command = _build_action_command(item)
        existing = get_action_command(command["action_id"])
        if existing:
            command["action_status"] = existing.get("action_status", "TODO")
            command["created_at"] = existing.get("created_at", command["created_at"])
        _save_file_action_command(command)
        partner = get_partner_pipeline(command["partner_id"])
        if partner:
            timeline = list(partner.get("timeline") or [])
            audit_logs = list(partner.get("audit_logs") or [])
            timeline.append({"event_type": "ACTION_COMMAND_CREATED", "message": command["action_title"], "status": "OK", "created_at": _now()})
            audit_logs.append({
                "log_id": _id("PAL"),
                "partner_id": command["partner_id"],
                "event_type": "ACTION_COMMAND_ASSIGNED",
                "old_value": "-",
                "new_value": command["action_id"],
                "changed_by": actor,
                "created_at": _now(),
            })
            update_partner_pipeline(command["partner_id"], {"timeline": timeline, "audit_logs": audit_logs}, actor=actor)
        generated.append(command)
    return {"generated_count": len(generated), "action_commands": generated}


def list_action_commands() -> list[dict[str, Any]]:
    return sorted(_list_file_action_commands(), key=lambda item: (item.get("action_status") == "DONE", item.get("due_date") or "", -int(item.get("opportunity_score") or 0)))


def get_action_command(action_id: str) -> Optional[dict[str, Any]]:
    return _get_file_action_command(action_id)


def update_action_command_status(action_id: str, status: str, actor: str = "system") -> dict[str, Any]:
    command = get_action_command(action_id)
    if not command:
        raise ValueError("ACTION_COMMAND_NOT_FOUND")
    if status not in {"TODO", "IN_PROGRESS", "DONE", "BLOCKED"}:
        raise ValueError("INVALID_ACTION_STATUS")
    old_status = command.get("action_status", "TODO")
    command["action_status"] = status
    command["updated_at"] = _now()
    _save_file_action_command(command)
    partner = get_partner_pipeline(command["partner_id"])
    if partner:
        event_type = "ACTION_COMMAND_COMPLETED" if status == "DONE" else "ACTION_COMMAND_ASSIGNED"
        timeline = list(partner.get("timeline") or [])
        audit_logs = list(partner.get("audit_logs") or [])
        timeline.append({"event_type": event_type, "message": f"{command['action_title']} / {status}", "status": "OK", "created_at": _now()})
        audit_logs.append({
            "log_id": _id("PAL"),
            "partner_id": command["partner_id"],
            "event_type": event_type,
            "old_value": old_status,
            "new_value": status,
            "changed_by": actor,
            "created_at": _now(),
        })
        update_partner_pipeline(command["partner_id"], {"timeline": timeline, "audit_logs": audit_logs}, actor=actor)
    return command


def action_command_summary() -> dict[str, Any]:
    commands = list_action_commands()
    today = datetime.now(timezone.utc).date()
    def due_date(command: dict[str, Any]):
        try:
            return datetime.fromisoformat(str(command.get("due_date"))).date()
        except Exception:
            return today
    open_commands = [item for item in commands if item.get("action_status") != "DONE"]
    completed = [item for item in commands if item.get("action_status") == "DONE"]
    due_this_week = [item for item in open_commands if due_date(item) <= today + timedelta(days=7)]
    overdue = [item for item in open_commands if due_date(item) < today]
    high_priority = [item for item in open_commands if item.get("priority") == "HIGH"]
    return {
        "total_action_commands": len(commands),
        "high_priority_actions": len(high_priority),
        "due_this_week": len(due_this_week),
        "overdue_actions": len(overdue),
        "completed_actions": len(completed),
        "action_completion_rate": round((len(completed) / len(commands)) * 100, 1) if commands else 0,
        "commands": commands,
    }


PROJECT_PIPELINE_STATUSES = {"IDEA", "QUALIFIED", "PROPOSAL", "CONTRACT", "IMPLEMENTATION", "OPERATING", "EXPANSION"}


def _project_id(partner_id: str, project_type: str) -> str:
    return f"PRJ-{partner_id}-{project_type}".replace(" ", "-").replace("_CARBON_MRV", "")


def _project_revenue(expected_value: float, opportunity_score: int, scale_factor: float = 1.0) -> dict[str, float]:
    revenue = calculate_project_revenue()
    setup_revenue = round(revenue["setup_fee"] * scale_factor)
    monthly_revenue = round(revenue["monthly_service_revenue"] * scale_factor)
    return {
        "setup_revenue_krw": setup_revenue,
        "monthly_revenue_krw": monthly_revenue,
        "arr_krw": monthly_revenue * 12,
        "project_revenue_krw": round(setup_revenue + monthly_revenue * int(revenue["contract_months"])),
        "contract_months": int(revenue["contract_months"]),
        "expansion_revenue_krw": round(setup_revenue * 0.45),
    }


def _ev_taxi_project_calculation(ev_conversion_count: float, partner_id: str) -> dict[str, Any]:
    config = get_carbon_factor_config()
    assumptions = ((config.get("project_assumptions") or {}).get("ev_taxi") or {})
    distance_per_vehicle = float((assumptions.get("annual_distance_km_per_vehicle") or {}).get("value") or 20000)
    charging_per_vehicle = float((assumptions.get("annual_charging_kwh_per_vehicle") or {}).get("value") or 3600)
    solar_per_vehicle = float((assumptions.get("annual_solar_self_consumption_kwh_per_vehicle") or {}).get("value") or 0)
    return calculate_ev_taxi_solar_reduction(
        {
            "vehicle_id": f"{partner_id}-EV-TAXI-POOL",
            "distance_km": max(0, ev_conversion_count) * distance_per_vehicle,
            "charging_kwh": max(0, ev_conversion_count) * charging_per_vehicle,
            "solar_self_consumption_kwh": max(0, ev_conversion_count) * solar_per_vehicle,
            "solar_generation_kwh": max(0, ev_conversion_count) * solar_per_vehicle,
        },
        config,
    )


def _business_project_candidates(partner: dict[str, Any]) -> list[dict[str, Any]]:
    opportunity = _partner_opportunity(partner)
    mobility = partner.get("mobility") or {}
    energy = partner.get("energy") or {}
    business_type = str(partner.get("business_type") or "").upper()
    partner_id = partner.get("partner_id") or _id("PTR")
    partner_name = partner.get("company_name") or partner_id
    owner = (partner.get("owner") or {}).get("owner_name") or "Ben"
    projects: list[dict[str, Any]] = []
    base_score = _clamp_score(min(95, opportunity["estimated_value"] / 300000 + opportunity["ev_opportunity"] / 3 + (10 if opportunity["mrv_candidate"] else 0)))

    def add(project_type: str, name: str, expected_co2e: float, score_bonus: int = 0, scale_factor: float = 1.0, calculation: Optional[dict[str, Any]] = None) -> None:
        expected_co2e = round(max(0, expected_co2e), 3)
        expected_value = round(expected_co2e * 15000)
        score = _clamp_score(base_score + score_bonus)
        revenue = _project_revenue(expected_value, score, scale_factor)
        project_id = _project_id(partner_id, project_type)
        existing = _get_file_business_project(project_id) or {}
        status = existing.get("status") or ("QUALIFIED" if score >= 70 else "IDEA")
        timeline = existing.get("timeline") or []
        if not timeline:
            timeline = [
                {"event_type": "PROJECT_CREATED", "message": f"{name} 자동 생성", "created_at": _now()},
                {"event_type": "PROJECT_QUALIFIED" if status == "QUALIFIED" else "PROJECT_IDEA", "message": f"Opportunity Score {score}", "created_at": _now()},
            ]
        projects.append({
            "project_id": project_id,
            "partner_id": partner_id,
            "partner_name": partner_name,
            "project_name": name,
            "project_type": project_type,
            "status": status,
            "owner": owner,
            "opportunity_score": score,
            "opportunity_level": "HIGH" if score >= 85 else "MEDIUM" if score >= 70 else "LOW",
            "expected_co2e_ton": expected_co2e,
            "expected_value_krw": expected_value,
            "calculation": calculation or {},
            **revenue,
            "timeline": timeline,
            "created_at": existing.get("created_at") or _now(),
            "updated_at": _now(),
        })

    taxi_count = _nested_number(partner, "mobility", "taxi_count")
    bus_count = _nested_number(partner, "mobility", "bus_count")
    charger_count = _nested_number(partner, "energy", "charger_count")
    solar_capacity = _nested_number(partner, "energy", "solar_capacity_kw")
    solar_installed = str(energy.get("solar_installed") or "").upper()

    if taxi_count > 0:
        calculation = _ev_taxi_project_calculation(opportunity["taxi_gap"], partner_id)
        add(
            "EV_TAXI_CARBON_MRV",
            f"{partner_name} EV Taxi Carbon MRV",
            calculation["total_reduction_tco2e"],
            8,
            1.0,
            calculation,
        )
    if bus_count > 0:
        add("EV_BUS_CARBON_MRV", f"{partner_name} EV Bus Carbon MRV", max(opportunity["bus_gap"], bus_count) * 18, 6, 1.35)
    if solar_installed == "YES" or solar_capacity > 0:
        add("SOLAR_CARBON_MRV", f"{partner_name} Solar Carbon MRV", max(solar_capacity, 100) * 0.45, 4, 0.8)
    if charger_count > 0 and solar_installed != "YES":
        proposed_solar_kw = max(solar_capacity, 600)
        annual_generation_kwh = proposed_solar_kw * 1200
        expected_solar_reduction_tco2e = annual_generation_kwh * 0.45 / 1000
        add(
            "SOLAR_EV_CHARGING",
            f"{partner_name} 태양광 설치 {int(proposed_solar_kw)}kW",
            expected_solar_reduction_tco2e,
            7,
            1.1,
            {
                "solar_capacity_kw": proposed_solar_kw,
                "annual_generation_kwh": annual_generation_kwh,
                "grid_emission_factor": 0.45,
                "formula": "solar_capacity_kw * 1200kWh_per_kW_year * 0.45kgCO2e_per_kWh / 1000",
            },
        )
    if business_type == "FACTORY":
        add("FACTORY_CARBON_MRV", f"{partner_name} Factory Carbon MRV", 250, 3, 1.2)
    return projects


def generate_business_projects(partner_id: Optional[str] = None, actor: str = "system") -> dict[str, Any]:
    source_partners = [get_partner_pipeline(partner_id)] if partner_id else list_partner_pipeline()
    generated = []
    for partner in [item for item in source_partners if item]:
        for project in _business_project_candidates(partner):
            existing = _get_file_business_project(project["project_id"])
            if existing:
                project["status"] = existing.get("status", project["status"])
                project["timeline"] = existing.get("timeline", project["timeline"])
                project["created_at"] = existing.get("created_at", project["created_at"])
            _save_file_business_project(project)
            partner_timeline = list(partner.get("timeline") or [])
            if not any(item.get("event_type") == "PROJECT_CREATED" and item.get("project_id") == project["project_id"] for item in partner_timeline):
                partner_timeline.append({
                    "event_type": "PROJECT_CREATED",
                    "project_id": project["project_id"],
                    "message": project["project_name"],
                    "status": project["status"],
                    "created_at": _now(),
                })
                try:
                    update_partner_pipeline(partner["partner_id"], {"timeline": partner_timeline}, actor=actor)
                except Exception:
                    pass
            generated.append(project)
    return {"generated_count": len(generated), "projects": generated}


def list_business_projects() -> list[dict[str, Any]]:
    return sorted(
        _list_file_business_projects(),
        key=lambda item: (
            item.get("status") == "OPERATING",
            item.get("opportunity_score", 0),
            item.get("arr_krw", 0),
        ),
        reverse=True,
    )


def get_business_project(project_id: str) -> Optional[dict[str, Any]]:
    return _get_file_business_project(project_id)


def update_business_project_status(project_id: str, status: str, actor: str = "system") -> dict[str, Any]:
    if status not in PROJECT_PIPELINE_STATUSES:
        raise ValueError("INVALID_PROJECT_STATUS")
    project = get_business_project(project_id)
    if not project:
        raise ValueError("PROJECT_NOT_FOUND")
    old_status = project.get("status")
    project["status"] = status
    project["updated_at"] = _now()
    project.setdefault("timeline", []).append({
        "event_type": f"PROJECT_{status}",
        "message": f"{old_status} -> {status}",
        "changed_by": actor,
        "created_at": _now(),
    })
    _save_file_business_project(project)
    return project


def business_project_summary() -> dict[str, Any]:
    projects = list_business_projects()
    def count(status: str) -> int:
        return sum(1 for item in projects if item.get("status") == status)
    active_statuses = {"QUALIFIED", "PROPOSAL", "CONTRACT", "IMPLEMENTATION", "OPERATING", "EXPANSION"}
    return {
        "storage_mode": "postgres" if is_postgres_configured() else "server_file_fallback",
        "total_projects": len(projects),
        "active_projects": sum(1 for item in projects if item.get("status") in active_statuses),
        "projects_in_proposal": count("PROPOSAL"),
        "projects_in_contract": count("CONTRACT"),
        "operating_projects": count("OPERATING"),
        "expansion_projects": count("EXPANSION"),
        "total_co2e_ton": round(sum(float(item.get("expected_co2e_ton") or 0) for item in projects), 3),
        "total_carbon_value_krw": round(sum(float(item.get("expected_value_krw") or 0) for item in projects)),
        "total_setup_revenue_krw": round(sum(float(item.get("setup_revenue_krw") or 0) for item in projects)),
        "total_monthly_revenue_krw": round(sum(float(item.get("monthly_revenue_krw") or 0) for item in projects)),
        "total_arr_krw": round(sum(float(item.get("arr_krw") or 0) for item in projects)),
        "total_expansion_revenue_krw": round(sum(float(item.get("expansion_revenue_krw") or 0) for item in projects)),
        "projects": projects,
    }


PROGRAM_PIPELINE_STATUSES = {"IDEA", "QUALIFIED", "FUNDED", "IMPLEMENTATION", "OPERATING", "EXPANSION"}


def _program_slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in str(value or "GLOBAL").upper()).strip("-") or "GLOBAL"


def _program_type_for_project(project: dict[str, Any]) -> str:
    project_type = str(project.get("project_type") or "")
    if "EV_TAXI" in project_type or "EV_BUS" in project_type or "CHARGING" in project_type:
        return "EV_MOBILITY_PROGRAM"
    if "SOLAR" in project_type:
        return "SOLAR_CARBON_PROGRAM"
    if "FACTORY" in project_type:
        return "FACTORY_CARBON_PROGRAM"
    return "REGIONAL_CARBON_PROGRAM"


def _program_name(region: str, program_type: str) -> str:
    label = {
        "EV_MOBILITY_PROGRAM": "EV Mobility Program",
        "SOLAR_CARBON_PROGRAM": "Solar Carbon Program",
        "FACTORY_CARBON_PROGRAM": "Factory Carbon Program",
        "SMART_CITY_CARBON_PROGRAM": "Smart City Carbon Program",
        "REGIONAL_CARBON_PROGRAM": "Regional Carbon Program",
    }.get(program_type, "Carbon Program")
    return f"{region or 'Global'} {label}"


def _program_id(region: str, program_type: str) -> str:
    return f"PRG-{_program_slug(region)}-{_program_slug(program_type)}"


def _program_from_projects(program_id: str, region: str, program_type: str, projects: list[dict[str, Any]], actor: str) -> dict[str, Any]:
    existing = _get_file_program(program_id) or {}
    total_co2e = round(sum(float(item.get("expected_co2e_ton") or 0) for item in projects), 3)
    total_value = round(sum(float(item.get("expected_value_krw") or 0) for item in projects))
    setup_revenue = round(sum(float(item.get("setup_revenue_krw") or 0) for item in projects))
    monthly_revenue = round(sum(float(item.get("monthly_revenue_krw") or 0) for item in projects))
    arr = round(sum(float(item.get("arr_krw") or 0) for item in projects))
    expansion_revenue = round(sum(float(item.get("expansion_revenue_krw") or 0) for item in projects))
    partner_ids = sorted({str(item.get("partner_id")) for item in projects if item.get("partner_id")})
    project_links = []
    for project in projects:
        contribution = round((float(project.get("expected_co2e_ton") or 0) / total_co2e) * 100, 1) if total_co2e else 0
        project_links.append({
            "program_id": program_id,
            "project_id": project["project_id"],
            "project_name": project.get("project_name"),
            "contribution_score": contribution,
            "status": project.get("status"),
        })
    project_statuses = {item.get("status") for item in projects}
    if "OPERATING" in project_statuses:
        status = "OPERATING"
    elif "IMPLEMENTATION" in project_statuses:
        status = "IMPLEMENTATION"
    elif "CONTRACT" in project_statuses:
        status = "FUNDED"
    elif "PROPOSAL" in project_statuses:
        status = "QUALIFIED"
    else:
        status = existing.get("status") or "QUALIFIED"
    progress_map = {"IDEA": 10, "QUALIFIED": 35, "FUNDED": 55, "IMPLEMENTATION": 70, "OPERATING": 90, "EXPANSION": 100}
    avg_score = round(sum(float(item.get("opportunity_score") or 0) for item in projects) / len(projects), 1) if projects else 0
    risk = "LOW" if avg_score >= 85 else "MEDIUM" if avg_score >= 70 else "HIGH"
    timeline = existing.get("timeline") or [{
        "event_type": "PROGRAM_CREATED",
        "message": _program_name(region, program_type),
        "changed_by": actor,
        "created_at": _now(),
    }]
    return {
        "program_id": program_id,
        "program_name": existing.get("program_name") or _program_name(region, program_type),
        "program_type": program_type,
        "owner": existing.get("owner") or "Ben",
        "region": region or "Global",
        "status": status,
        "project_links": project_links,
        "project_count": len(projects),
        "partner_count": len(partner_ids),
        "partner_ids": partner_ids,
        "progress_pct": progress_map.get(status, 0),
        "risk": risk,
        "total_co2e_ton": total_co2e,
        "total_carbon_value_krw": total_value,
        "setup_revenue_krw": setup_revenue,
        "monthly_revenue_krw": monthly_revenue,
        "arr_krw": arr,
        "expansion_revenue_krw": expansion_revenue,
        "government_view": {
            "participating_companies": len(partner_ids),
            "conversion_vehicle_count": round(total_co2e / 3.2) if program_type == "EV_MOBILITY_PROGRAM" else 0,
            "reduction_tco2e": total_co2e,
            "carbon_value_krw": total_value,
        },
        "investor_view": {
            "program_value_krw": total_value,
            "revenue_krw": setup_revenue,
            "arr_krw": arr,
            "roi_pct": round((arr / setup_revenue) * 100, 1) if setup_revenue else 0,
            "risk": risk,
        },
        "execution": {
            "open_tasks": sum(1 for item in projects if item.get("status") in {"IDEA", "QUALIFIED", "PROPOSAL"}),
            "blocked_tasks": 0,
            "completion_pct": progress_map.get(status, 0),
            "at_risk_projects": sum(1 for item in projects if item.get("opportunity_level") == "LOW"),
        },
        "timeline": timeline,
        "created_at": existing.get("created_at") or _now(),
        "updated_at": _now(),
    }


def generate_programs(actor: str = "system") -> dict[str, Any]:
    generate_business_projects(actor=actor)
    projects = list_business_projects()
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for project in projects:
        partner = get_partner_pipeline(project.get("partner_id") or "") or {}
        region = partner.get("region") or project.get("region") or "Global"
        program_type = _program_type_for_project(project)
        grouped.setdefault((region, program_type), []).append(project)
    programs = []
    for (region, program_type), items in grouped.items():
        program_id = _program_id(region, program_type)
        program = _program_from_projects(program_id, region, program_type, items, actor)
        _save_file_program(program)
        programs.append(program)
    return {"generated_count": len(programs), "programs": sorted(programs, key=lambda item: item.get("arr_krw", 0), reverse=True)}


def create_program(payload: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    program_type = payload.get("program_type") or "REGIONAL_CARBON_PROGRAM"
    region = payload.get("region") or "Global"
    program_id = payload.get("program_id") or _program_id(region, program_type)
    existing = _get_file_program(program_id) or {}
    program = {
        **existing,
        "program_id": program_id,
        "program_name": payload.get("program_name") or existing.get("program_name") or _program_name(region, program_type),
        "program_type": program_type,
        "owner": payload.get("owner") or existing.get("owner") or "Ben",
        "region": region,
        "status": payload.get("status") or existing.get("status") or "IDEA",
        "project_links": existing.get("project_links") or [],
        "timeline": existing.get("timeline") or [],
        "created_at": existing.get("created_at") or _now(),
        "updated_at": _now(),
    }
    program.setdefault("timeline", []).append({
        "event_type": "PROGRAM_CREATED",
        "message": program["program_name"],
        "changed_by": actor,
        "created_at": _now(),
    })
    return _save_file_program(program)


def list_programs() -> list[dict[str, Any]]:
    return sorted(_list_file_programs(), key=lambda item: (item.get("status") == "OPERATING", item.get("arr_krw", 0)), reverse=True)


def get_program(program_id: str) -> Optional[dict[str, Any]]:
    return _get_file_program(program_id)


def link_project_to_program(program_id: str, project_id: str, contribution_score: Optional[float] = None, actor: str = "system") -> dict[str, Any]:
    program = get_program(program_id)
    project = get_business_project(project_id)
    if not program:
        raise ValueError("PROGRAM_NOT_FOUND")
    if not project:
        raise ValueError("PROJECT_NOT_FOUND")
    links = [item for item in program.get("project_links", []) if item.get("project_id") != project_id]
    links.append({
        "program_id": program_id,
        "project_id": project_id,
        "project_name": project.get("project_name"),
        "contribution_score": contribution_score if contribution_score is not None else 0,
        "status": project.get("status"),
    })
    program["project_links"] = links
    program.setdefault("timeline", []).append({
        "event_type": "PROJECT_LINKED",
        "message": project_id,
        "changed_by": actor,
        "created_at": _now(),
    })
    program["project_count"] = len(links)
    program["updated_at"] = _now()
    return _save_file_program(program)


def program_summary() -> dict[str, Any]:
    programs = list_programs()
    def count(status: str) -> int:
        return sum(1 for item in programs if item.get("status") == status)
    return {
        "storage_mode": "postgres" if is_postgres_configured() else "server_file_fallback",
        "total_programs": len(programs),
        "operating_programs": count("OPERATING"),
        "qualified_programs": count("QUALIFIED"),
        "funded_programs": count("FUNDED"),
        "implementation_programs": count("IMPLEMENTATION"),
        "expansion_programs": count("EXPANSION"),
        "project_count": sum(int(item.get("project_count") or 0) for item in programs),
        "partner_count": len({partner for item in programs for partner in item.get("partner_ids", [])}),
        "total_co2e_ton": round(sum(float(item.get("total_co2e_ton") or 0) for item in programs), 3),
        "total_carbon_value_krw": round(sum(float(item.get("total_carbon_value_krw") or 0) for item in programs)),
        "total_revenue_krw": round(sum(float(item.get("setup_revenue_krw") or 0) for item in programs)),
        "total_arr_krw": round(sum(float(item.get("arr_krw") or 0) for item in programs)),
        "total_expansion_value_krw": round(sum(float(item.get("expansion_revenue_krw") or 0) for item in programs)),
        "programs": programs,
    }


def program_dashboard(program_id: str) -> dict[str, Any]:
    program = get_program(program_id)
    if not program:
        raise ValueError("PROGRAM_NOT_FOUND")
    return {
        "program": program,
        "kpi": {
            "total_co2e_ton": program.get("total_co2e_ton", 0),
            "total_carbon_value_krw": program.get("total_carbon_value_krw", 0),
            "total_revenue_krw": program.get("setup_revenue_krw", 0),
            "arr_krw": program.get("arr_krw", 0),
            "expansion_value_krw": program.get("expansion_revenue_krw", 0),
        },
        "government_view": program.get("government_view", {}),
        "investor_view": program.get("investor_view", {}),
        "execution": program.get("execution", {}),
    }


CREDIT_READINESS_STATUSES = {
    "NOT_ELIGIBLE",
    "PRE_ELIGIBLE",
    "ELIGIBLE",
    "READY_FOR_VERIFICATION",
    "READY_FOR_REGISTRY",
}


def _credit_methodology(project: dict[str, Any]) -> dict[str, str]:
    project_type = str(project.get("project_type") or "").upper()
    if "EV_TAXI" in project_type:
        return {
            "methodology_id": "ZENOV-MOBILITY-MRV-001",
            "methodology_name": "EV Taxi baseline replacement methodology",
        }
    if "EV_BUS" in project_type:
        return {
            "methodology_id": "ZENOV-MOBILITY-MRV-002",
            "methodology_name": "EV Bus baseline replacement methodology",
        }
    if "SOLAR_EV" in project_type or "CHARGING" in project_type:
        return {
            "methodology_id": "ZENOV-EV-SOLAR-MRV-001",
            "methodology_name": "Solar charging displacement methodology",
        }
    if "SOLAR" in project_type:
        return {
            "methodology_id": "ZENOV-SOLAR-MRV-001",
            "methodology_name": "Grid displacement solar methodology",
        }
    if "FACTORY" in project_type:
        return {
            "methodology_id": "ZENOV-FACTORY-MRV-001",
            "methodology_name": "Factory energy reduction methodology",
        }
    return {
        "methodology_id": "ZENOV-CARBON-MRV-GENERAL-001",
        "methodology_name": "General carbon reduction screening methodology",
    }


def _credit_grade(score: float) -> str:
    if score >= 95:
        return "AAA"
    if score >= 90:
        return "AA"
    if score >= 85:
        return "A"
    if score >= 75:
        return "BBB"
    if score >= 65:
        return "BB"
    return "B"


def _credit_status(score: float, additionality_status: str, baseline_status: str) -> str:
    if additionality_status == "FAIL" or baseline_status == "FAIL":
        return "NOT_ELIGIBLE"
    if score >= 95:
        return "READY_FOR_REGISTRY"
    if score >= 90:
        return "READY_FOR_VERIFICATION"
    if score >= 80:
        return "ELIGIBLE"
    if score >= 65:
        return "PRE_ELIGIBLE"
    return "NOT_ELIGIBLE"


def _build_verification_package(project: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    package_id = f"VPK-{project['project_id']}"
    return {
        "package_id": package_id,
        "project_id": project["project_id"],
        "status": "READY" if readiness["credit_status"] in {"READY_FOR_VERIFICATION", "READY_FOR_REGISTRY"} else "DRAFT",
        "documents": [
            {
                "document_type": "TRUST_REPORT",
                "status": "READY",
                "summary": "Trust packet, hash, signature, and evidence checks are packaged for verifier review.",
            },
            {
                "document_type": "MRV_REPORT",
                "status": "READY" if project.get("expected_co2e_ton") else "NEEDS_DATA",
                "summary": f"Expected reduction: {project.get('expected_co2e_ton', 0)} tCO2e.",
            },
            {
                "document_type": "VALIDATION_REPORT",
                "status": "READY",
                "summary": "Baseline, additionality, leakage, and permanence screening results are included.",
            },
            {
                "document_type": "METHODOLOGY_REPORT",
                "status": "READY",
                "summary": readiness["methodology_id"],
            },
            {
                "document_type": "AUDIT_REPORT",
                "status": "READY",
                "summary": "Timeline and status events are attached as audit evidence.",
            },
        ],
        "created_at": _now(),
    }


def build_credit_readiness(project: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    project_type = str(project.get("project_type") or "").upper()
    expected_co2e = float(project.get("expected_co2e_ton") or 0)
    opportunity_score = float(project.get("opportunity_score") or 0)
    calculation = project.get("calculation") or {}
    methodology = _credit_methodology(project)

    additionality_status = "PASS"
    additionality_reason = "Project creates reduction beyond the fossil-fuel baseline."
    if project.get("legal_mandate") is True:
        additionality_status = "FAIL"
        additionality_reason = "Reduction appears legally mandated and cannot be treated as additional."
    additionality_score = 100 if additionality_status == "PASS" else 0

    baseline_status = "PASS" if expected_co2e > 0 and methodology.get("methodology_id") else "FAIL"
    baseline_score = 100 if baseline_status == "PASS" else 0
    baseline_reason = "Baseline is mapped to a fossil or grid displacement reference." if baseline_status == "PASS" else "Baseline or expected reduction is missing."

    permanence_score = 92 if "SOLAR" in project_type else 88 if "EV" in project_type else 75
    permanence_status = "PASS" if permanence_score >= 85 else "WARNING"

    leakage_score = 92
    leakage_risk = "LOW"
    leakage_reason = "No displacement risk flag detected."
    if project.get("leakage_flag"):
        leakage_score = 45
        leakage_risk = "HIGH"
        leakage_reason = "Potential emission shift detected."

    trust_score = 96 if calculation else 90
    validation_score = max(80, min(96, opportunity_score + 8))
    readiness_score = round(
        trust_score * 0.20
        + validation_score * 0.20
        + additionality_score * 0.20
        + baseline_score * 0.20
        + leakage_score * 0.10
        + permanence_score * 0.10,
        1,
    )
    credit_status = _credit_status(readiness_score, additionality_status, baseline_status)
    registry_readiness = "READY" if credit_status == "READY_FOR_REGISTRY" else "NOT_READY"
    verification_ready = credit_status in {"READY_FOR_VERIFICATION", "READY_FOR_REGISTRY"}

    readiness = {
        "credit_readiness_id": f"CRD-{project['project_id']}",
        "project_id": project["project_id"],
        "project_name": project.get("project_name"),
        "partner_id": project.get("partner_id"),
        "partner_name": project.get("partner_name"),
        "project_type": project.get("project_type"),
        "expected_co2e_ton": round(expected_co2e, 3),
        "expected_value_krw": round(float(project.get("expected_value_krw") or 0)),
        "methodology_id": methodology["methodology_id"],
        "methodology_name": methodology["methodology_name"],
        "trust_score": trust_score,
        "validation_score": validation_score,
        "additionality_status": additionality_status,
        "additionality_score": additionality_score,
        "additionality_reason": additionality_reason,
        "baseline_status": baseline_status,
        "baseline_score": baseline_score,
        "baseline_reason": baseline_reason,
        "leakage_risk": leakage_risk,
        "leakage_score": leakage_score,
        "leakage_reason": leakage_reason,
        "permanence_status": permanence_status,
        "permanence_score": permanence_score,
        "credit_readiness_score": readiness_score,
        "credit_grade": _credit_grade(readiness_score),
        "credit_status": credit_status,
        "verification_ready": verification_ready,
        "registry_readiness": registry_readiness,
        "registry_ready": registry_readiness == "READY",
        "is_carbon_credit": False,
        "legal_note": "This is a Carbon Credit readiness assessment, not credit issuance.",
        "created_by": actor,
        "updated_at": _now(),
    }
    readiness["verification_package"] = _build_verification_package(project, readiness)
    return readiness


def generate_credit_readiness(project_id: Optional[str] = None, actor: str = "system") -> dict[str, Any]:
    generate_business_projects(actor=actor)
    projects = [get_business_project(project_id)] if project_id else list_business_projects()
    generated = []
    for project in [item for item in projects if item]:
        readiness = build_credit_readiness(project, actor=actor)
        existing = _get_file_credit_readiness(project["project_id"]) or {}
        readiness["created_at"] = existing.get("created_at") or _now()
        _save_file_credit_readiness(readiness)
        project["credit_readiness"] = {
            "credit_readiness_score": readiness["credit_readiness_score"],
            "credit_grade": readiness["credit_grade"],
            "credit_status": readiness["credit_status"],
            "registry_readiness": readiness["registry_readiness"],
        }
        project.setdefault("timeline", [])
        if not any(item.get("event_type") == "CREDIT_READINESS_CREATED" for item in project["timeline"]):
            project["timeline"].append({
                "event_type": "CREDIT_READINESS_CREATED",
                "message": f"{readiness['credit_grade']} / {readiness['credit_status']}",
                "changed_by": actor,
                "created_at": _now(),
            })
        _save_file_business_project(project)
        generated.append(readiness)
    return {"generated_count": len(generated), "credit_readiness": generated}


def list_credit_readiness() -> list[dict[str, Any]]:
    readiness = _list_file_credit_readiness()
    if not readiness:
        generate_credit_readiness(actor="system")
        readiness = _list_file_credit_readiness()
    return sorted(readiness, key=lambda item: (item.get("credit_readiness_score", 0), item.get("expected_value_krw", 0)), reverse=True)


def get_credit_readiness(project_id: str) -> Optional[dict[str, Any]]:
    readiness = _get_file_credit_readiness(project_id)
    if readiness:
        return readiness
    project = get_business_project(project_id)
    if not project:
        return None
    return generate_credit_readiness(project_id=project_id, actor="system")["credit_readiness"][0]


def credit_readiness_summary() -> dict[str, Any]:
    readiness = list_credit_readiness()
    verification_ready = [item for item in readiness if item.get("verification_ready")]
    registry_ready = [item for item in readiness if item.get("registry_ready")]
    credit_ready = [item for item in readiness if item.get("credit_status") == "READY_FOR_REGISTRY"]
    avg_score = round(sum(float(item.get("credit_readiness_score") or 0) for item in readiness) / len(readiness), 1) if readiness else 0
    grade_order = {"AAA": 6, "AA": 5, "A": 4, "BBB": 3, "BB": 2, "B": 1}
    top_grade = "-"
    if readiness:
        top_grade = max((item.get("credit_grade") or "B" for item in readiness), key=lambda grade: grade_order.get(grade, 0))
    return {
        "storage_mode": "postgres" if is_postgres_configured() else "server_file_fallback",
        "total_assessed_projects": len(readiness),
        "carbon_credits_ready": len(credit_ready),
        "verification_ready": len(verification_ready),
        "registry_ready": len(registry_ready),
        "average_readiness_score": avg_score,
        "top_credit_grade": top_grade,
        "credit_readiness": readiness,
    }


def _stakeholder_policy(project: dict[str, Any]) -> list[dict[str, Any]]:
    partner_name = project.get("partner_name") or "Partner"
    project_type = str(project.get("project_type") or "")
    supplier_name = "Charging / Solar Supplier" if "SOLAR" in project_type or "CHARGING" in project_type else "Mobility Data Supplier"
    return [
        {
            "stakeholder_id": f"STK-{project['project_id']}-OWNER",
            "stakeholder_type": "ASSET_OWNER",
            "stakeholder_name": partner_name,
            "role": "Owns the operating asset and receives the primary carbon value benefit.",
            "share_pct": 50,
        },
        {
            "stakeholder_id": f"STK-{project['project_id']}-OPERATOR",
            "stakeholder_type": "OPERATOR",
            "stakeholder_name": "Zenov",
            "role": "Operates Trust, MRV, reporting, and portfolio infrastructure.",
            "share_pct": 20,
        },
        {
            "stakeholder_id": f"STK-{project['project_id']}-SUPPLIER",
            "stakeholder_type": "SUPPLIER",
            "stakeholder_name": supplier_name,
            "role": "Provides charging, solar, gateway, or source data infrastructure.",
            "share_pct": 10,
        },
        {
            "stakeholder_id": f"STK-{project['project_id']}-INVESTOR",
            "stakeholder_type": "INVESTOR",
            "stakeholder_name": "ESG / Carbon Fund",
            "role": "Funds expansion and receives investment-linked upside where applicable.",
            "share_pct": 15,
        },
        {
            "stakeholder_id": f"STK-{project['project_id']}-VERIFIER",
            "stakeholder_type": "VERIFIER",
            "stakeholder_name": "KTL / Verification Body",
            "role": "Reviews evidence package and verification workflow.",
            "share_pct": 3,
        },
        {
            "stakeholder_id": f"STK-{project['project_id']}-GOVERNMENT",
            "stakeholder_type": "GOVERNMENT",
            "stakeholder_name": "Local Government Program",
            "role": "Receives verified reduction evidence for regional carbon outcomes.",
            "share_pct": 2,
        },
    ]


def _value_chain_for_project(project: dict[str, Any]) -> list[dict[str, Any]]:
    project_type = str(project.get("project_type") or "")
    if "SOLAR" in project_type or "CHARGING" in project_type:
        labels = ["Taxi Fleet", "Charging", "Solar", "Trust / MRV", "Carbon Value", "Revenue Distribution"]
    elif "EV_TAXI" in project_type:
        labels = ["Taxi Fleet", "Charging Data", "Trust / MRV", "Carbon Value", "Revenue Distribution"]
    elif "EV_BUS" in project_type:
        labels = ["Bus Fleet", "Charging Data", "Trust / MRV", "Carbon Value", "Revenue Distribution"]
    else:
        labels = ["Source Data", "Trust / MRV", "Carbon Value", "Revenue Distribution"]
    return [
        {
            "step": index + 1,
            "node": label,
            "status": "ACTIVE" if index < len(labels) - 1 else "DISTRIBUTION_READY",
        }
        for index, label in enumerate(labels)
    ]


def build_carbon_economy(project: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    carbon_value = float(project.get("expected_value_krw") or 0)
    project_revenue = float(project.get("project_revenue_krw") or 0)
    arr = float(project.get("arr_krw") or 0)
    setup_revenue = float(project.get("setup_revenue_krw") or 0)
    expected_co2e = float(project.get("expected_co2e_ton") or 0)
    stakeholders = _stakeholder_policy(project)
    distribution = []
    for stakeholder in stakeholders:
        amount = round(carbon_value * float(stakeholder["share_pct"]) / 100)
        distribution.append({
            "stakeholder_id": stakeholder["stakeholder_id"],
            "stakeholder_type": stakeholder["stakeholder_type"],
            "stakeholder_name": stakeholder["stakeholder_name"],
            "share_pct": stakeholder["share_pct"],
            "distributed_value_krw": amount,
        })
    cost_saving = round(expected_co2e * 12000)
    roi_pct = round(((project_revenue + carbon_value + cost_saving) / setup_revenue) * 100, 1) if setup_revenue else 0
    expansion_potential = float(project.get("expansion_revenue_krw") or 0)
    value_score = round(min(100, 35 + carbon_value / 1200000 + project_revenue / 2500000 + len(stakeholders) * 2 + expansion_potential / 3000000), 1)
    economy = {
        "economy_id": f"ECO-{project['project_id']}",
        "project_id": project["project_id"],
        "project_name": project.get("project_name"),
        "partner_id": project.get("partner_id"),
        "partner_name": project.get("partner_name"),
        "project_type": project.get("project_type"),
        "stakeholders": stakeholders,
        "value_chain": _value_chain_for_project(project),
        "benefits": [
            {
                "stakeholder_type": "ASSET_OWNER",
                "benefit_type": "CARBON_VALUE_SHARE",
                "description": "Receives carbon value share and operating insight from verified project data.",
                "estimated_value_krw": round(carbon_value * 0.50),
            },
            {
                "stakeholder_type": "OPERATOR",
                "benefit_type": "SERVICE_REVENUE",
                "description": "Earns setup, MRV, data management, and platform revenue.",
                "estimated_value_krw": round(project_revenue),
            },
            {
                "stakeholder_type": "SUPPLIER",
                "benefit_type": "INFRASTRUCTURE_REVENUE",
                "description": "Captures charging, solar, gateway, or integration expansion opportunity.",
                "estimated_value_krw": round(expansion_potential),
            },
            {
                "stakeholder_type": "GOVERNMENT",
                "benefit_type": "REGIONAL_REDUCTION",
                "description": "Receives measurable reduction evidence for regional ESG and carbon programs.",
                "estimated_value_krw": round(cost_saving),
            },
        ],
        "revenue_distribution": distribution,
        "carbon_economy_map": {
            "title": f"{project.get('partner_name') or 'Partner'} Carbon Economy Map",
            "flow": [item["node"] for item in _value_chain_for_project(project)],
        },
        "economic_impact": {
            "carbon_value_krw": round(carbon_value),
            "service_revenue_krw": round(project_revenue),
            "arr_krw": round(arr),
            "cost_saving_krw": cost_saving,
            "roi_pct": roi_pct,
        },
        "ecosystem_value_score": value_score,
        "total_value_distributed_krw": round(sum(item["distributed_value_krw"] for item in distribution)),
        "stakeholder_count": len(stakeholders),
        "created_by": actor,
        "updated_at": _now(),
    }
    return economy


def generate_carbon_economy(project_id: Optional[str] = None, actor: str = "system") -> dict[str, Any]:
    generate_business_projects(actor=actor)
    projects = [get_business_project(project_id)] if project_id else list_business_projects()
    generated = []
    for project in [item for item in projects if item]:
        economy = build_carbon_economy(project, actor=actor)
        existing = _get_file_carbon_economy(project["project_id"]) or {}
        economy["created_at"] = existing.get("created_at") or _now()
        _save_file_carbon_economy(economy)
        project["carbon_economy"] = {
            "ecosystem_value_score": economy["ecosystem_value_score"],
            "total_value_distributed_krw": economy["total_value_distributed_krw"],
            "stakeholder_count": economy["stakeholder_count"],
        }
        project.setdefault("timeline", [])
        if not any(item.get("event_type") == "CARBON_ECONOMY_CREATED" for item in project["timeline"]):
            project["timeline"].append({
                "event_type": "CARBON_ECONOMY_CREATED",
                "message": f"Value Score {economy['ecosystem_value_score']}",
                "changed_by": actor,
                "created_at": _now(),
            })
        _save_file_business_project(project)
        generated.append(economy)
    return {"generated_count": len(generated), "carbon_economy": generated}


def list_carbon_economy() -> list[dict[str, Any]]:
    economies = _list_file_carbon_economy()
    if not economies:
        generate_carbon_economy(actor="system")
        economies = _list_file_carbon_economy()
    return sorted(economies, key=lambda item: (item.get("ecosystem_value_score", 0), item.get("economic_impact", {}).get("service_revenue_krw", 0)), reverse=True)


def get_carbon_economy(project_id: str) -> Optional[dict[str, Any]]:
    economy = _get_file_carbon_economy(project_id)
    if economy:
        return economy
    project = get_business_project(project_id)
    if not project:
        return None
    return generate_carbon_economy(project_id=project_id, actor="system")["carbon_economy"][0]


def carbon_economy_summary() -> dict[str, Any]:
    economies = list_carbon_economy()
    total_carbon_value = round(sum(float(item.get("economic_impact", {}).get("carbon_value_krw") or 0) for item in economies))
    total_revenue = round(sum(float(item.get("economic_impact", {}).get("service_revenue_krw") or 0) for item in economies))
    total_distributed = round(sum(float(item.get("total_value_distributed_krw") or 0) for item in economies))
    total_stakeholders = sum(int(item.get("stakeholder_count") or 0) for item in economies)
    avg_score = round(sum(float(item.get("ecosystem_value_score") or 0) for item in economies) / len(economies), 1) if economies else 0
    return {
        "storage_mode": "postgres" if is_postgres_configured() else "server_file_fallback",
        "total_projects": len(economies),
        "total_carbon_value_krw": total_carbon_value,
        "total_revenue_krw": total_revenue,
        "total_value_distributed_krw": total_distributed,
        "total_stakeholders": total_stakeholders,
        "average_value_score": avg_score,
        "carbon_economy": economies,
    }


def _transformation_status(score: float) -> str:
    if score >= 90:
        return "EXPANSION"
    if score >= 75:
        return "PRODUCTION"
    if score >= 60:
        return "TRANSFORMATION"
    if score >= 40:
        return "READINESS"
    return "DISCOVERY"


def _partner_projects(partner_id: str) -> list[dict[str, Any]]:
    return [project for project in list_business_projects() if project.get("partner_id") == partner_id]


def build_partner_transformation(partner: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    partner_id = partner.get("partner_id") or _id("PTR")
    mobility = partner.get("mobility") or {}
    energy = partner.get("energy") or {}
    carbon = partner.get("carbon_esg") or {}
    projects = _partner_projects(partner_id)
    taxi_count = float(mobility.get("taxi_count") or 0)
    ev_taxi_count = float(mobility.get("ev_taxi_count") or 0)
    bus_count = float(mobility.get("bus_count") or 0)
    ev_bus_count = float(mobility.get("ev_bus_count") or 0)
    total_fleet = taxi_count + bus_count + float(mobility.get("motorcycle_count") or 0) + float(mobility.get("logistics_vehicle_count") or 0)
    total_ev = ev_taxi_count + ev_bus_count + float(mobility.get("ev_motorcycle_count") or 0) + float(mobility.get("ev_logistics_vehicle_count") or 0)
    ev_ratio = (total_ev / total_fleet * 100) if total_fleet else 0
    charger_count = float(energy.get("charger_count") or 0) + float(energy.get("fast_charger_count") or 0) + float(energy.get("slow_charger_count") or 0)
    solar_capacity = float(energy.get("solar_capacity_kw") or 0)
    ess_capacity = float(energy.get("ess_capacity_kwh") or 0)
    solar_installed = str(energy.get("solar_installed") or "").upper() == "YES" or solar_capacity > 0
    ess_installed = str(energy.get("ess_installed") or "").upper() == "YES" or ess_capacity > 0
    mrv_interest = str(carbon.get("mrv_interest") or "").upper()
    credit_interest = str(carbon.get("carbon_credit_interest") or "").upper()

    mobility_score = min(100, (min(total_fleet, 500) / 500) * 35 + ev_ratio * 0.45 + (20 if charger_count else 0) + (10 if projects else 0))
    energy_score = min(100, (35 if solar_installed else 12 if charger_count else 0) + (25 if ess_installed else 0) + min(charger_count, 50) * 0.8 + min(solar_capacity, 1000) / 30)
    carbon_score = min(100, (30 if mrv_interest in {"HIGH", "YES"} else 15 if mrv_interest == "MEDIUM" else 0) + (25 if credit_interest in {"HIGH", "YES"} else 12 if credit_interest == "MEDIUM" else 0) + (20 if projects else 0) + min(len(projects) * 12, 25))
    transformation_score = round(mobility_score * 0.40 + energy_score * 0.30 + carbon_score * 0.30, 1)
    status = _transformation_status(transformation_score)

    ev_taxi_gap = max(0, taxi_count - ev_taxi_count)
    ev_bus_gap = max(0, bus_count - ev_bus_count)
    recommended_solar_kw = round(max(solar_capacity, 500 if charger_count and not solar_installed else solar_capacity))
    recommended_ess_kwh = round(max(ess_capacity, recommended_solar_kw * 2 if recommended_solar_kw else 0))
    total_co2e = round(sum(float(project.get("expected_co2e_ton") or 0) for project in projects), 3)
    total_value = round(sum(float(project.get("expected_value_krw") or 0) for project in projects))
    total_revenue = round(sum(float(project.get("project_revenue_krw") or 0) for project in projects))
    arr = round(sum(float(project.get("arr_krw") or 0) for project in projects))
    capex = round(ev_taxi_gap * 5000000 + ev_bus_gap * 25000000 + recommended_solar_kw * 1200000 + recommended_ess_kwh * 450000)
    opex = round(max(arr * 0.18, 12000000 if projects else 0))
    five_year_revenue = round(total_revenue + arr * 4)
    five_year_carbon_value = round(total_value * 5)
    payback_years = round(capex / max(arr + total_value, 1), 1) if capex else 0
    roi_5y = round(((five_year_revenue + five_year_carbon_value) / capex) * 100, 1) if capex else 0

    transformation = {
        "transformation_id": f"TRN-{partner_id}",
        "partner_id": partner_id,
        "partner_name": partner.get("company_name") or partner_id,
        "business_type": partner.get("business_type"),
        "transformation_score": transformation_score,
        "carbon_readiness": "HIGH" if transformation_score >= 75 else "MEDIUM" if transformation_score >= 50 else "LOW",
        "growth_stage": status,
        "transformation_status": status,
        "score_breakdown": {
            "mobility_score": round(mobility_score, 1),
            "energy_score": round(energy_score, 1),
            "carbon_score": round(carbon_score, 1),
        },
        "current_state": {
            "taxi_count": taxi_count,
            "ev_taxi_count": ev_taxi_count,
            "bus_count": bus_count,
            "ev_bus_count": ev_bus_count,
            "ev_ratio_pct": round(ev_ratio, 1),
            "solar_capacity_kw": solar_capacity,
            "ess_capacity_kwh": ess_capacity,
            "charger_count": charger_count,
            "project_count": len(projects),
        },
        "target_state": {
            "ev_taxi_conversion": ev_taxi_gap,
            "ev_bus_conversion": ev_bus_gap,
            "solar_capacity_kw": recommended_solar_kw,
            "ess_capacity_kwh": recommended_ess_kwh,
            "carbon_business_role": "Carbon Business Operator",
        },
        "carbon_factory_blueprint": {
            "recommended_ev_taxi_conversion": ev_taxi_gap,
            "recommended_ev_bus_conversion": ev_bus_gap,
            "recommended_solar_kw": recommended_solar_kw,
            "recommended_ess_kwh": recommended_ess_kwh,
            "recommended_projects": [project.get("project_type") for project in projects],
        },
        "business_plan_5y": {
            "expected_reduction_tco2e": round(total_co2e * 5, 3),
            "expected_carbon_value_krw": five_year_carbon_value,
            "expected_revenue_krw": five_year_revenue,
            "roi_pct": roi_5y,
            "investment_plan_krw": capex,
        },
        "growth_roadmap": [
            {"year": 1, "focus": "MRV 구축", "outcome": "Trust data and first MRV project operating"},
            {"year": 2, "focus": "Solar / Charging 구축", "outcome": "Energy-linked carbon production structure"},
            {"year": 3, "focus": "Carbon Asset", "outcome": "Verified carbon asset candidate portfolio"},
            {"year": 4, "focus": "Program 운영", "outcome": "Regional mobility or energy carbon program"},
            {"year": 5, "focus": "Carbon Economy 참여", "outcome": "Revenue distribution and ecosystem expansion"},
        ],
        "organization_builder": [
            {"role": "MRV Manager", "reason": "Owns methodology, data quality, and reporting workflow"},
            {"role": "Data Manager", "reason": "Manages taxi, charger, solar, and evidence data"},
            {"role": "Carbon Operator", "reason": "Turns verified projects into repeatable carbon business operations"},
        ],
        "investment_roadmap": {
            "capex_krw": capex,
            "opex_krw": opex,
            "roi_pct": roi_5y,
            "payback_years": payback_years,
        },
        "revenue_roadmap": {
            "carbon_revenue_5y_krw": five_year_carbon_value,
            "platform_revenue_5y_krw": five_year_revenue,
            "energy_revenue_opportunity_krw": round(recommended_solar_kw * 180000),
        },
        "created_by": actor,
        "updated_at": _now(),
    }
    return transformation


def generate_transformations(partner_id: Optional[str] = None, actor: str = "system") -> dict[str, Any]:
    generate_business_projects(partner_id=partner_id, actor=actor)
    source_partners = [get_partner_pipeline(partner_id)] if partner_id else list_partner_pipeline()
    generated = []
    for partner in [item for item in source_partners if item]:
        transformation = build_partner_transformation(partner, actor=actor)
        existing = _get_file_transformation(transformation["partner_id"]) or {}
        transformation["created_at"] = existing.get("created_at") or _now()
        _save_file_transformation(transformation)
        generated.append(transformation)
    return {"generated_count": len(generated), "transformations": generated}


def list_transformations() -> list[dict[str, Any]]:
    transformations = _list_file_transformations()
    if not transformations:
        generate_transformations(actor="system")
        transformations = _list_file_transformations()
    return sorted(transformations, key=lambda item: (item.get("transformation_score", 0), item.get("business_plan_5y", {}).get("expected_revenue_krw", 0)), reverse=True)


def get_transformation(partner_id: str) -> Optional[dict[str, Any]]:
    transformation = _get_file_transformation(partner_id)
    if transformation:
        return transformation
    partner = get_partner_pipeline(partner_id)
    if not partner:
        return None
    return generate_transformations(partner_id=partner_id, actor="system")["transformations"][0]


def build_transformation_report(partner: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    partner_id = partner.get("partner_id") or _id("PTR")
    transformation = get_transformation(partner_id) or build_partner_transformation(partner, actor=actor)
    projects = _partner_projects(partner_id)
    mobility = partner.get("mobility") or {}
    energy = partner.get("energy") or {}
    current_ev_taxi = float(mobility.get("ev_taxi_count") or 0)
    taxi_count = float(mobility.get("taxi_count") or 0)
    target_state = transformation.get("target_state") or {}
    target_ev_taxi = min(taxi_count, max(current_ev_taxi, float(target_state.get("ev_taxi_conversion") or 0)))
    current_calc = _ev_taxi_project_calculation(current_ev_taxi, partner_id) if current_ev_taxi > 0 else {
        "total_reduction_tco2e": 0,
        "estimated_value": 0,
    }
    after_co2e = round(sum(float(project.get("expected_co2e_ton") or 0) for project in projects), 3)
    after_value = round(sum(float(project.get("expected_value_krw") or 0) for project in projects))
    after_revenue = round(sum(float(project.get("project_revenue_krw") or 0) for project in projects))
    after_arr = round(sum(float(project.get("arr_krw") or 0) for project in projects))
    before_co2e = round(float(current_calc.get("total_reduction_tco2e") or 0), 3)
    before_value = round(float(current_calc.get("estimated_value") or 0))
    before_revenue = 0
    capex = round(float((transformation.get("investment_roadmap") or {}).get("capex_krw") or 0))
    roi_pct = round(((after_revenue + after_value - before_value) / capex) * 100, 1) if capex else 0
    progress = round(min(100, (current_ev_taxi / target_ev_taxi) * 100), 1) if target_ev_taxi else 0
    report = {
        "report_id": f"TRP-{partner_id}",
        "partner_id": partner_id,
        "partner_name": partner.get("company_name") or partner_id,
        "report_type": "BEFORE_AFTER_TRANSFORMATION",
        "validation_stage": "REAL_CUSTOMER_VALIDATION",
        "current_state": {
            "taxi_count": taxi_count,
            "ev_taxi_count": current_ev_taxi,
            "charger_count": float(energy.get("charger_count") or 0),
            "solar_capacity_kw": float(energy.get("solar_capacity_kw") or 0),
        },
        "target_state": {
            "target_ev_taxi_count": target_ev_taxi,
            "additional_ev_taxi_needed": max(0, target_ev_taxi - current_ev_taxi),
            "target_solar_capacity_kw": float(target_state.get("solar_capacity_kw") or 0),
            "target_ess_capacity_kwh": float(target_state.get("ess_capacity_kwh") or 0),
        },
        "before_report": {
            "current_co2e_ton": before_co2e,
            "current_carbon_value_krw": before_value,
            "current_revenue_krw": before_revenue,
        },
        "after_report": {
            "expected_co2e_ton": after_co2e,
            "expected_carbon_value_krw": after_value,
            "expected_revenue_krw": after_revenue,
            "expected_arr_krw": after_arr,
            "expected_roi_pct": roi_pct,
        },
        "impact": {
            "additional_co2e_ton": round(after_co2e - before_co2e, 3),
            "additional_carbon_value_krw": round(after_value - before_value),
            "additional_revenue_krw": after_revenue - before_revenue,
            "transformation_progress_pct": progress,
        },
        "recommended_roadmap": [
            {"period": "1Y", "focus": "MRV 구축 및 실데이터 연결", "target": "안산교통 운행/충전 데이터 기반 첫 Transformation Report"},
            {"period": "3Y", "focus": "EV Taxi 전환 및 Solar 연계", "target": f"EV Taxi {int(target_ev_taxi)}대 목표와 Solar {int(float(target_state.get('solar_capacity_kw') or 0))}kW 구조"},
            {"period": "5Y", "focus": "Carbon Business Operator 전환", "target": "Carbon Asset Portfolio와 Revenue Distribution 운영"},
        ],
        "executive_message": "This report proves the customer value Zenov can create from real partner data.",
        "created_by": actor,
        "created_at": _now(),
    }
    return report


def generate_transformation_report(partner_id: str, actor: str = "system") -> dict[str, Any]:
    partner = get_partner_pipeline(partner_id)
    if not partner:
        raise ValueError("PARTNER_NOT_FOUND")
    generate_business_projects(partner_id=partner_id, actor=actor)
    generate_transformations(partner_id=partner_id, actor=actor)
    report = build_transformation_report(partner, actor=actor)
    return _save_file_transformation_report(report)


def get_transformation_report(partner_id: str) -> Optional[dict[str, Any]]:
    report = _get_file_transformation_report(partner_id)
    if report:
        return report
    partner = get_partner_pipeline(partner_id)
    if not partner:
        return None
    return generate_transformation_report(partner_id, actor="system")


def build_golden_template_certification(partner_id: str, actor: str = "system") -> dict[str, Any]:
    partner = get_partner_pipeline(partner_id)
    if not partner:
        raise ValueError("PARTNER_NOT_FOUND")
    projects = generate_business_projects(partner_id=partner_id, actor=actor)["projects"]
    report = generate_transformation_report(partner_id, actor=actor)
    mobility = partner.get("mobility") or {}
    energy = partner.get("energy") or {}
    carbon = partner.get("carbon_esg") or {}
    taxi_count = float(mobility.get("taxi_count") or 0)
    ev_taxi_count = float(mobility.get("ev_taxi_count") or 0)
    charger_count = float(energy.get("charger_count") or 0)
    solar_capacity = float(energy.get("solar_capacity_kw") or 0)
    data_fields = [
        taxi_count > 0,
        ev_taxi_count >= 0,
        charger_count >= 0,
        "solar_installed" in energy or solar_capacity >= 0,
        bool(projects),
        bool(report.get("after_report")),
    ]
    data_quality = round(sum(1 for item in data_fields if item) / len(data_fields) * 100, 1)
    trust = 92.0 if partner.get("status") in {"QUESTIONNAIRE_SUBMITTED", "UNDER_REVIEW", "MEETING_SCHEDULED", "PROPOSAL_READY", "OPERATING"} else 84.0
    mrv_accuracy = min(100.0, 88.0 + len(projects) * 4)
    operational_stability = min(100.0, 76.0 + min(charger_count, 20) * 0.8 + (6 if taxi_count >= 100 else 0))
    business_value = min(100.0, 70.0 + min(float(report.get("after_report", {}).get("expected_revenue_krw") or 0) / 5000000, 20) + (5 if str(carbon.get("mrv_interest") or "").upper() in {"YES", "HIGH"} else 0))
    score = round((data_quality + trust + mrv_accuracy + operational_stability + business_value) / 5, 1)
    readiness = "REPLICATION_READY" if score >= 90 else "PILOT_READY" if score >= 80 else "NOT_READY"
    certification = {
        "certification_id": f"GTC-{partner_id}",
        "partner_id": partner_id,
        "partner_name": partner.get("company_name") or partner_id,
        "status": "CERTIFIED" if score >= 80 else "NEEDS_REVIEW",
        "golden_template_score": score,
        "replication_readiness": readiness,
        "audit": {
            "vehicle_data": "PASS" if taxi_count > 0 else "FAIL",
            "charging_data": "PASS" if charger_count >= 0 else "FAIL",
            "power_data": "PASS",
            "solar_data": "PASS" if "solar_installed" in energy or solar_capacity >= 0 else "WARNING",
            "mrv_result": "PASS" if projects else "FAIL",
            "carbon_value_result": "PASS" if report.get("after_report", {}).get("expected_carbon_value_krw") else "FAIL",
        },
        "score_breakdown": {
            "data_quality": data_quality,
            "trust": trust,
            "mrv_accuracy": mrv_accuracy,
            "operational_stability": round(operational_stability, 1),
            "business_value": round(business_value, 1),
        },
        "standard_operating_procedure": [
            "Partner Folder에서 차량, 충전, 전력, 태양광 기본 데이터를 수집한다.",
            "Trust & Evidence 기준으로 데이터 출처와 변경 이력을 확인한다.",
            "MRV 계산 결과와 Carbon Value를 생성한다.",
            "Executive Dashboard에서 Before / After Transformation을 검토한다.",
            "Transformation Report와 Golden Template Certification을 보관한다.",
        ],
        "replication_package": {
            "questionnaire": "READY",
            "proposal": "READY",
            "kpi": "READY",
            "dashboard": "READY",
            "api_settings": "READY",
            "data_dictionary": "READY",
        },
        "target_markets": [
            {"rank": 1, "region": "수원", "priority": "HIGH", "reason": "택시/모빌리티 밀집 지역"},
            {"rank": 2, "region": "성남", "priority": "HIGH", "reason": "기업/모빌리티 전환 수요"},
            {"rank": 3, "region": "부천", "priority": "MEDIUM", "reason": "수도권 복제 가능 시장"},
            {"rank": 4, "region": "인천", "priority": "MEDIUM", "reason": "물류/충전 인프라 확장 가능"},
        ],
        "transformation_report_id": report.get("report_id"),
        "certified_by": actor,
        "certified_at": _now(),
    }
    return certification


def certify_golden_template(partner_id: str, actor: str = "system") -> dict[str, Any]:
    return _save_file_golden_template(build_golden_template_certification(partner_id, actor=actor))


def get_golden_template(partner_id: str) -> Optional[dict[str, Any]]:
    certification = _get_file_golden_template(partner_id)
    if certification:
        return certification
    partner = get_partner_pipeline(partner_id)
    if not partner:
        return None
    return certify_golden_template(partner_id, actor="system")


def golden_template_summary() -> dict[str, Any]:
    certifications = _list_file_golden_templates()
    if not certifications:
        partners = list_partner_pipeline()
        if partners:
            certifications = [certify_golden_template(partners[0]["partner_id"], actor="system")]
    top = certifications[0] if certifications else {}
    return {
        "storage_mode": "postgres" if is_postgres_configured() else "server_file_fallback",
        "golden_template_count": len(certifications),
        "top_partner": top.get("partner_name") or "-",
        "golden_template_score": top.get("golden_template_score") or 0,
        "certification_status": top.get("status") or "-",
        "replication_readiness": top.get("replication_readiness") or "-",
        "target_markets": top.get("target_markets") or [],
        "latest_certification": top or None,
        "certifications": certifications,
    }


def build_commercial_business_case(partner_id: str, actor: str = "system") -> dict[str, Any]:
    partner = get_partner_pipeline(partner_id)
    if not partner:
        raise ValueError("PARTNER_NOT_FOUND")
    projects = generate_business_projects(partner_id=partner_id, actor=actor)["projects"]
    report = get_transformation_report(partner_id) or generate_transformation_report(partner_id, actor=actor)
    mobility = partner.get("mobility") or {}
    energy = partner.get("energy") or {}
    taxi_count = float(mobility.get("taxi_count") or 0)
    ev_taxi_count = float(mobility.get("ev_taxi_count") or 0)
    charger_count = float(energy.get("charger_count") or 0)
    solar_capacity = float(energy.get("solar_capacity_kw") or 0)
    target = report.get("target_state") or {}
    after = report.get("after_report") or {}
    current_ev = float(report.get("current_state", {}).get("ev_taxi_count") or ev_taxi_count)
    target_ev = float(target.get("target_ev_taxi_count") or current_ev)
    ev_conversion_count = max(0, target_ev - current_ev)
    annual_energy_saving = round(ev_conversion_count * 1800000)
    annual_ops_saving = round(taxi_count * 240000)
    annual_solar_saving = round(max(0, float(target.get("target_solar_capacity_kw") or solar_capacity) - solar_capacity) * 165000)
    annual_cost_saving = annual_energy_saving + annual_ops_saving + annual_solar_saving
    annual_carbon_value = round(float(after.get("expected_carbon_value_krw") or sum(float(item.get("expected_value_krw") or 0) for item in projects)))
    annual_new_revenue = round(float(after.get("expected_arr_krw") or sum(float(item.get("arr_krw") or 0) for item in projects)))
    expected_co2e = round(float(after.get("expected_co2e_ton") or sum(float(item.get("expected_co2e_ton") or 0) for item in projects)), 3)
    roi_pct = round(float(after.get("expected_roi_pct") or 0), 1)
    expected_revenue = round(float(after.get("expected_revenue_krw") or sum(float(item.get("project_revenue_krw") or 0) for item in projects)))
    transformation = get_transformation(partner_id) or build_partner_transformation(partner, actor=actor)
    investment = round(float((transformation.get("investment_roadmap") or {}).get("capex_krw") or 0))
    annual_total_benefit = annual_cost_saving + annual_carbon_value
    payback_period_years = round(investment / max(annual_total_benefit, 1), 1) if investment else 0
    business_case = {
        "commercial_case_id": f"COM-{partner_id}",
        "partner_id": partner_id,
        "partner_name": partner.get("company_name") or partner_id,
        "proposal_first_page": {
            "annual_cost_saving_krw": annual_cost_saving,
            "annual_new_revenue_krw": annual_new_revenue,
            "payback_period_years": payback_period_years,
            "expected_co2e_ton": expected_co2e,
            "expected_carbon_value_krw": annual_carbon_value,
            "roi_pct": roi_pct,
        },
        "input_basis": {
            "vehicle_count": taxi_count,
            "ev_count": ev_taxi_count,
            "charger_count": charger_count,
            "solar_capacity_kw": solar_capacity,
            "target_ev_count": target_ev,
            "target_solar_capacity_kw": float(target.get("target_solar_capacity_kw") or 0),
        },
        "benefit_breakdown": {
            "energy_cost_saving_krw": annual_energy_saving,
            "operations_saving_krw": annual_ops_saving,
            "solar_saving_krw": annual_solar_saving,
            "annual_total_benefit_krw": annual_total_benefit,
            "annual_new_revenue_krw": annual_new_revenue,
            "expected_project_revenue_krw": expected_revenue,
            "estimated_investment_krw": investment,
        },
        "business_case_message": "고객은 Carbon을 사지 않는다. 고객은 절감액과 수익을 산다.",
        "generated_by": actor,
        "generated_at": _now(),
    }
    return business_case


def transformation_summary() -> dict[str, Any]:
    transformations = list_transformations()
    avg_score = round(sum(float(item.get("transformation_score") or 0) for item in transformations) / len(transformations), 1) if transformations else 0
    total_5y_revenue = round(sum(float(item.get("business_plan_5y", {}).get("expected_revenue_krw") or 0) for item in transformations))
    total_5y_value = round(sum(float(item.get("business_plan_5y", {}).get("expected_carbon_value_krw") or 0) for item in transformations))
    stage_counts: dict[str, int] = {}
    for item in transformations:
        stage = item.get("growth_stage") or "DISCOVERY"
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    top_stage = transformations[0].get("growth_stage") if transformations else "-"
    top_readiness = transformations[0].get("carbon_readiness") if transformations else "-"
    top_partner_id = transformations[0]["partner_id"] if transformations else None
    return {
        "storage_mode": "postgres" if is_postgres_configured() else "server_file_fallback",
        "total_partners": len(transformations),
        "average_transformation_score": avg_score,
        "top_growth_stage": top_stage,
        "top_carbon_readiness": top_readiness,
        "total_5y_revenue_krw": total_5y_revenue,
        "total_5y_carbon_value_krw": total_5y_value,
        "stage_counts": stage_counts,
        "latest_report": get_transformation_report(top_partner_id) if top_partner_id else None,
        "golden_template": golden_template_summary().get("latest_certification"),
        "commercial_case": build_commercial_business_case(top_partner_id) if top_partner_id else None,
        "transformations": transformations,
    }
