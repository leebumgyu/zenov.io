# ZENOV Sprint 10-12 Implementation Report

## Scope

Sprint 10, 11, and 12 add the operating layer needed to move Zenov from demo data processing to commercial operations.

## Sprint 10 - Root Cause Drill-down Engine

Purpose:

Operators must identify what failed and why within 30 seconds.

Implemented APIs:

- `GET /api/v1/ops/drilldown/{lookup_id}`
- `GET /api/v1/ops/drilldown/packet/{packet_id}`
- `GET /api/v1/ops/drilldown/evidence/{evidence_id}`
- `GET /api/v1/ops/drilldown/job/{job_id}`
- `GET /api/v1/ops/root-cause/summary`
- `POST /api/v1/ops/retry/{import_job_row_id}`

Failure classification:

- `MISSING_REQUIRED_FIELD`
- `MISSING_VEHICLE_ID`
- `INVALID_DISTANCE`
- `INVALID_DATE`
- `INVALID_NUMBER`
- `DUPLICATE_OPERATION`
- `EVIDENCE_CREATION_FAILED`
- `MRV_CALCULATION_FAILED`
- `VERIFICATION_REJECTED`
- `ASSET_CREATION_FAILED`
- `REGISTRY_REGISTRATION_FAILED`

Retry states:

- `FAILED`
- `RETRY_PENDING`
- `RETRYING`
- `RECOVERED`
- `DLQ`

## Sprint 11 - KPI & Target Management Engine

Purpose:

Portfolio dashboards must show current value, target value, achievement rate, and trend.

Implemented APIs:

- `GET /api/v1/portfolio/kpi`
- `POST /api/v1/portfolio/targets`
- `GET /api/v1/portfolio/targets/{portfolio_id}`
- `POST /api/v1/portfolio/kpi/snapshot`
- `GET /api/v1/portfolio/kpi/snapshots`

Core KPI:

- Fleet Size
- Verified Carbon Reduction
- Asset Creation
- Registry Assets
- Portfolio Value

Default target:

- `target_vehicle_count`: 500
- `target_reduction_tco2e`: 1000
- `target_asset_count`: 300
- `target_registry_count`: 120
- `target_portfolio_value`: 1,000,000,000 KRW

## Sprint 12 - Partner Self-Service Dashboard

Purpose:

Partners must verify their own integration status without asking Zenov operations.

Implemented APIs:

- `GET /api/v1/partners/{partner_id}/dashboard`
- `GET /api/v1/partners/{partner_id}/health`
- `GET /api/v1/partners/{partner_id}/imports`
- `GET /api/v1/partners/{partner_id}/mapping-errors`

Partner status messages:

- `CONNECTED`
- `DATA RECEIVED`
- `MAPPING OK`
- `EVIDENCE CREATED`
- `MRV CALCULATED`
- `VERIFICATION PASSED`
- `ASSET GENERATED`

## UI

Added demo-web sections:

- Operations Root Cause Drill-down
- Portfolio KPI & Target Management
- Partner Self-Service Dashboard

## Verification

143-row success import:

- Total rows: 143
- Success rows: 143
- Failed rows: 0
- Duplicate rows: 0
- Asset candidates: 143
- Portfolio fleet KPI: 143 / 500 = 28.6%
- Partner status: CONNECTED
- Verification pass rate: 100.0%

Failure import:

- Total rows: 143
- Success rows: 0
- Failed rows: 3
- Duplicate rows: 140
- Top root cause: `DUPLICATE_OPERATION`
- Additional reasons: `MISSING_VEHICLE_ID`, `INVALID_DATE`, `NEGATIVE_DISTANCE`

Browser console errors:

- 0

Screenshot:

- `outputs/zenov-mobility-data-platform/sprint10-12-ops-kpi-partner.png`
