# ZENOV Sprint 14 Commercial Readiness & Tenant Platform Report

## Objective

Zenov is no longer a single-project deployment. It now supports multiple companies as a SaaS platform.

## Implemented Files

- `db/postgres/018_tenant_schema.sql`
- `zenov_trust_layer/app/database/tenant_crud.py`
- `zenov_trust_layer/app/services/tenant_service.py`
- `zenov_trust_layer/app/tenant_middleware.py`
- `zenov_trust_layer/app/services/subscription_service.py`
- `zenov_trust_layer/app/services/billing_service.py`
- `zenov_trust_layer/app/tenant_routes.py`
- `outputs/zenov-mobility-data-platform/web/index.html`

## Core Features

### Tenant Isolation

Each tenant can have its own:

- Dashboard
- Asset summary
- Wallet summary
- Registry summary
- Report summary
- Import job summary

Legacy `owner_entity` values remain supported so existing Ansan Transport data continues to work.

### Role-Based Access Control

Supported roles:

- `SUPER_ADMIN`
- `PARTNER_ADMIN`
- `FLEET_MANAGER`
- `DRIVER`
- `AUDITOR`

### Subscription Engine

Supported plans:

- `FREE`
- `PILOT`
- `ENTERPRISE`
- `GOVERNMENT`

Default `PILOT` plan:

- Monthly fee: 500,000 KRW
- Seat limit: 10
- Vehicle limit: 200
- Asset limit: 500
- Monthly API call limit: 50,000

### Billing Engine

Each tenant receives a billing account with:

- Billing email
- Currency
- Payment status
- Monthly fee
- Next invoice estimate

## Implemented APIs

- `POST /api/v1/tenants`
- `GET /api/v1/tenants`
- `GET /api/v1/tenants/plans`
- `GET /api/v1/tenants/{tenant_id}/dashboard`
- `GET /api/v1/tenants/{tenant_id}/subscription`
- `GET /api/v1/tenants/{tenant_id}/billing`
- `GET /api/v1/tenants/{tenant_id}/access-check`

Both `tenant_id` and `tenant_slug` are supported on tenant-specific routes.

## Browser Verification

Demo UI added:

- `CREATE ANSAN TENANT`
- `CREATE BUSAN TENANT`
- `LOAD ANSAN TENANT DASHBOARD`
- `LOAD BILLING`

Verified state after 143-row import:

- Tenant count: 2
- Ansan plan: `PILOT`
- Ansan tenant assets: 143
- Ansan tenant wallets: 143
- Ansan tenant report count: 1
- Browser console errors: 0

Screenshot:

- `outputs/zenov-mobility-data-platform/sprint14-tenant-platform.png`

## Completion Criteria

New companies can now be added by creating a tenant.

No DB reconstruction is required for:

- Second taxi company onboarding
- Bus company onboarding
- Logistics company onboarding
- Energy company onboarding

## Next Sprint

Sprint 15 should become Marketplace Integration Layer:

- Charging providers
- Insurance companies
- Maintenance shops
- Tire providers
- EV manufacturers
- Financial institutions
