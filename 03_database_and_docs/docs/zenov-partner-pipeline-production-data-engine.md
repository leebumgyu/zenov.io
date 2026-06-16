# ZENOV Partner Pipeline Production Data Engine

## Purpose

Partner Folder data must be stored through the server API first.

LocalStorage is now only a browser-side cache and emergency fallback.

## Implemented API

Partner:

- `POST /api/v1/partners`
- `GET /api/v1/partners`
- `GET /api/v1/partners/{partner_id}`
- `PATCH /api/v1/partners/{partner_id}`

Questionnaire:

- `POST /api/v1/partners/{partner_id}/questionnaire`
- `GET /api/v1/partners/{partner_id}/questionnaire`

Workflow:

- `POST /api/v1/partners/{partner_id}/actions`
- `PATCH /api/v1/partners/{partner_id}/status`
- `POST /api/v1/partners/{partner_id}/meetings`
- `POST /api/v1/partners/{partner_id}/proposals`

Sales Execution:

- `POST /api/v1/partners/{partner_id}/send-material`
- `POST /api/v1/partners/{partner_id}/feedback`
- `GET /api/v1/partners/{partner_id}/conversion-score`

Partner Success:

- `POST /api/v1/partners/{partner_id}/monthly-report`
- `GET /api/v1/partners/{partner_id}/success`
- `GET /api/v1/partners/dashboard/partner-success`

Executive Dashboard:

- `GET /api/v1/executive-dashboard/summary`
- `GET /api/v1/executive-dashboard/pipeline`
- `GET /api/v1/executive-dashboard/opportunities`
- `GET /api/v1/executive-dashboard/revenue-expansion`

## PostgreSQL Schema

Apply:

```bash
psql "$DATABASE_URL" -f db/postgres/031_partner_pipeline_production_schema.sql
```

The migration adds/creates:

- `partners`
- `questionnaires`
- `partner_status_history`
- `partner_actions`
- `meetings`
- `proposals`
- `sales_execution`
- `sent_materials`
- `feedback_logs`
- `partner_success`
- `partner_uploaded_files`
- `partner_pipeline_audit_logs`

## Run Server

Use FastAPI, not a static-only Python server:

```bash
python3 -m uvicorn zenov_trust_layer.app.main:app --host 127.0.0.1 --port 8010
```

Do not use this for production partner saving:

```bash
python3 -m http.server 8010
```

That command only serves static files. It does not provide `/api/v1/partners`, so the browser falls back to local cache.

Then open:

```text
http://127.0.0.1:8010/demo-web/partner/index.html?v=98
http://127.0.0.1:8010/demo-web/index.html?v=98
```

## Storage Status Check

Open:

```text
http://127.0.0.1:8010/api/v1/storage/status
```

Expected production mode:

```json
{
  "postgres": {
    "configured": true,
    "connected": true,
    "mode": "postgres"
  }
}
```

If `DATABASE_URL` is empty, partner submissions are saved by the server to:

```text
outputs/zenov-mobility-data-platform/data/partner_pipeline_store.json
```

This is a server-side fallback, not the final production database.

## Supabase / PostgreSQL Setup

Set `DATABASE_URL` before starting FastAPI:

```bash
export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres"
python3 -m uvicorn zenov_trust_layer.app.main:app --host 127.0.0.1 --port 8010
```

On startup, the API applies:

```text
db/postgres/016_partner_hub_schema.sql
db/postgres/031_partner_pipeline_production_schema.sql
```

Then `POST /api/v1/partners` stores Partner Folder submissions in PostgreSQL.

## Verification Result

Browser flow verified:

```text
Partner Folder
-> Sample Partner
-> Mark Operating
-> Send Monthly Report
-> Primary Storage = SERVER DB
-> Executive Dashboard auto aggregation
```

Current local mode:

```text
storage_mode = memory_fallback
```

Reason:

```text
DATABASE_URL is not configured in this local run.
```

Production target:

```text
storage_mode = postgres
```

## Final Rule

The frontend must treat server API as primary storage.

LocalStorage is only:

- temporary cache
- offline draft
- emergency backup
