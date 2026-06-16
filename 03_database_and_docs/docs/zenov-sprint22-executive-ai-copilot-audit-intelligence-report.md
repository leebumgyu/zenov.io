# ZENOV SPRINT 22 Executive AI Copilot & Audit Intelligence Report

## Objective

Executive AI Copilot is a read-only intelligence layer over verified Zenov data.

AI does not create data, approve verification, register assets, or change methodology.
It explains Portfolio, Asset, Registry, Compliance, and Report status from the existing Trust Chain.

## Added Files

- `db/postgres/026_ai_copilot_schema.sql`
- `zenov_trust_layer/app/ai_copilot_routes.py`
- `zenov_trust_layer/app/services/natural_language_query_engine.py`
- `zenov_trust_layer/app/services/executive_copilot_service.py`
- `zenov_trust_layer/app/services/audit_intelligence_service.py`
- `zenov_trust_layer/app/services/evidence_explainer.py`

## API

- `POST /api/v1/copilot/query`
- `GET /api/v1/copilot/query-logs`
- `GET /api/v1/copilot/audit/asset/latest`
- `GET /api/v1/copilot/audit/asset/{asset_id}`
- `GET /api/v1/copilot/evidence/{evidence_id}`
- `GET /api/v1/copilot/examples`

## Supported Questions

- 이번 달 총 감축량은?
- 안산교통 Asset은 몇 개인가?
- 태국 프로젝트 상태는?
- Verification Reject 원인은?
- MRR은 얼마인가?
- AST-2026-0001은 어떤 근거로 생성되었는가?

## Guardrail

The Copilot blocks the following commands:

- Asset creation
- Verification approval
- Registry registration
- Methodology change
- Carbon Credit issuance

Blocked response status:

```json
{
  "status": "BLOCKED",
  "intent": "FORBIDDEN_ACTION",
  "guardrail": "READ_ONLY_COPILOT"
}
```

## Audit Intelligence

The asset explainer traces:

```text
Packet
↓
Evidence
↓
MRV
↓
Verification
↓
Asset Candidate
↓
Registry Status
```

The response includes:

- `packet_id`
- `evidence_id`
- `mrv_id`
- `verification_id`
- `asset_id`
- `registry_id`
- `traceability_status`

## Verification

Local TestClient verification:

- 143-row Ansan Transport CSV import: `SUCCESS`
- Asset Candidate count: `143`
- Asset count query: `ANSWERED / ASSET_COUNT`
- Total reduction query: `ANSWERED / PORTFOLIO_REDUCTION`
- Thailand country status query: `ANSWERED / COUNTRY_STATUS`
- Verification reject reason query: `ANSWERED / VERIFICATION_REJECT_REASON`
- MRR query: `ANSWERED / MRR`
- Forbidden Registry registration command: `BLOCKED / FORBIDDEN_ACTION`
- Latest Asset explanation: `EXPLAINED`

## Final Rule

Executive AI Copilot is not an automation agent.

It is an explanation layer for verified Trust Chain data.
