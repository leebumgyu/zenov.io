# ZENOV Sprint 12 Partner Integration Hub Report

## Objective

Build a Partner Integration Hub so new taxi companies, bus companies, charging operators, insurers, ERP systems, and IoT systems can connect to Zenov without code changes.

Core rule:

> If a developer must modify code to connect a new partner, the integration model has failed. Zenov must be config-driven.

## Implemented Files

- `db/postgres/016_partner_hub_schema.sql`
- `zenov_trust_layer/app/database/partner_crud.py`
- `zenov_trust_layer/app/services/partner_api_keys.py`
- `zenov_trust_layer/app/services/partner_mapping_engine.py`
- `zenov_trust_layer/app/services/partner_gateway.py`
- `zenov_trust_layer/app/services/partner_service.py`
- `zenov_trust_layer/app/partner_routes.py`
- `outputs/zenov-mobility-data-platform/web/index.html`

## Core Tables

- `partners`
- `partner_api_keys`
- `partner_data_mappings`
- `partner_integrations`
- `partner_health_logs`

## Partner Lifecycle

- `INVITED`
- `ONBOARDING`
- `CONNECTED`
- `ACTIVE`
- `SUSPENDED`

## Data Mapping Engine

Supported initial mapping templates:

- `TMONEY_CSV` -> `taxi_daily_operation`
- `DTG` -> `vehicle_operation_log`
- `GPS` -> `mobility_tracking_log`
- `CHARGER_API` -> `charging_session`

Example:

```text
T-money CSV
-> partner_data_mapping
-> taxi_daily_operation
-> Evidence Layer
```

## Implemented APIs

- `POST /api/v1/partners/register`
- `POST /api/v1/partners/connect`
- `GET /api/v1/partners/status`
- `GET /api/v1/partners/health`
- `POST /api/v1/partners/gateway/ingest`

Existing partner self-service APIs remain active:

- `GET /api/v1/partners/{partner_id}/dashboard`
- `GET /api/v1/partners/{partner_id}/health`
- `GET /api/v1/partners/{partner_id}/imports`
- `GET /api/v1/partners/{partner_id}/mapping-errors`

## Smoke Test

Partner:

- `BUSAN_TAXI`

Result:

- Register: `INVITED`
- Mapping: `MAPPING_OK`
- Connect: `CONNECTED`
- Gateway ingest: `ACCEPTED`
- Standard model: `taxi_daily_operation`
- Health: `CONNECTED`

Browser:

- Partner Hub buttons render.
- Register, Connect, and T-money Mapping Test buttons work.
- Console errors: 0

Screenshot:

- `outputs/zenov-mobility-data-platform/sprint12-partner-hub.png`

## Next Sprint

Sprint 13 should become Data Exchange Gateway:

- Webhook
- REST API
- CSV Import
- SFTP Import
- Event Streaming
