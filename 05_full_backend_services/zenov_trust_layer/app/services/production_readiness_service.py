from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ..storage import (
    operational_runbooks,
    production_readiness_checks,
    save_operational_runbook_memory,
    save_production_readiness_check_memory,
)


READINESS_TEMPLATE = [
    ("BACKUP", "Daily database backup configured", "HIGH"),
    ("RECOVERY", "Restore procedure tested", "HIGH"),
    ("MONITORING", "API and import monitoring enabled", "HIGH"),
    ("SECURITY", "Secrets and API keys isolated", "HIGH"),
    ("RBAC", "Role-based access control configured", "MEDIUM"),
    ("AUDIT_LOG", "Audit logs are append-only and searchable", "HIGH"),
]

RUNBOOK_TEMPLATE = [
    (
        "INCIDENT_RESPONSE",
        "장애 대응 절차",
        [
            "장애 범위 확인",
            "최근 import job 및 failed row 확인",
            "Trace API로 packet/evidence/MRV 상태 확인",
            "고객에게 영향 범위와 예상 복구 시간을 공유",
        ],
    ),
    (
        "DATA_RECOVERY",
        "데이터 복구 절차",
        [
            "백업 스냅샷 확인",
            "손상된 import job 격리",
            "failed_import_rows reason_code 검토",
            "재처리 전 hash/signature 재검증",
        ],
    ),
    (
        "CUSTOMER_SUPPORT",
        "고객 지원 절차",
        [
            "Customer Health 확인",
            "Day 1/7/30/60/90 마일스톤 확인",
            "파트너 대시보드 연결 상태 확인",
            "다음 성공 액션을 고객에게 안내",
        ],
    ),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def bootstrap_readiness_checks(tenant_id: Optional[str] = "ansan-trans") -> list[dict[str, Any]]:
    existing = [
        item for item in production_readiness_checks.values()
        if item.get("tenant_id") == tenant_id
    ]
    if existing:
        return sorted(existing, key=lambda item: item.get("category", ""))
    checks = []
    for category, name, severity in READINESS_TEMPLATE:
        check = {
            "check_id": _new_id("PRD"),
            "tenant_id": tenant_id,
            "category": category,
            "check_name": name,
            "status": "PASS" if category in {"MONITORING", "AUDIT_LOG", "RBAC"} else "PENDING",
            "severity": severity,
            "evidence_ref": None,
            "owner_role": "SUPER_ADMIN",
            "checked_at": _now() if category in {"MONITORING", "AUDIT_LOG", "RBAC"} else None,
            "created_at": _now(),
        }
        save_production_readiness_check_memory(check)
        checks.append(check)
    return checks


def update_readiness_check(check_id: str, status: str, evidence_ref: Optional[str] = None) -> dict[str, Any]:
    check = production_readiness_checks.get(check_id)
    if not check:
        raise ValueError("READINESS_CHECK_NOT_FOUND")
    check["status"] = status.upper()
    check["evidence_ref"] = evidence_ref
    check["checked_at"] = _now()
    save_production_readiness_check_memory(check)
    return check


def readiness_summary(tenant_id: Optional[str] = "ansan-trans") -> dict[str, Any]:
    checks = bootstrap_readiness_checks(tenant_id)
    total = len(checks)
    passed = sum(1 for item in checks if item.get("status") == "PASS")
    blocked = [item for item in checks if item.get("status") not in {"PASS", "WAIVED"} and item.get("severity") == "HIGH"]
    score = round((passed / total) * 100, 2) if total else 0
    status = "PRODUCTION_READY" if score >= 90 and not blocked else "NOT_READY"
    return {
        "tenant_id": tenant_id,
        "status": status,
        "readiness_score": score,
        "passed_checks": passed,
        "total_checks": total,
        "blocking_checks": blocked,
        "checks": checks,
    }


def bootstrap_runbooks(tenant_id: Optional[str] = "ansan-trans") -> list[dict[str, Any]]:
    existing = [
        item for item in operational_runbooks.values()
        if item.get("tenant_id") == tenant_id
    ]
    if existing:
        return sorted(existing, key=lambda item: item.get("runbook_type", ""))
    items = []
    for runbook_type, title, steps in RUNBOOK_TEMPLATE:
        runbook = {
            "runbook_id": _new_id("RUNBOOK"),
            "tenant_id": tenant_id,
            "runbook_type": runbook_type,
            "title": title,
            "severity": "HIGH",
            "steps": steps,
            "owner_role": "OPERATIONS",
            "status": "ACTIVE",
            "created_at": _now(),
            "updated_at": _now(),
        }
        save_operational_runbook_memory(runbook)
        items.append(runbook)
    return items


def list_runbooks(tenant_id: Optional[str] = "ansan-trans") -> dict[str, Any]:
    items = bootstrap_runbooks(tenant_id)
    return {"tenant_id": tenant_id, "count": len(items), "items": items}
