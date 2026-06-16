# ZENOV SPRINT 24 Global Asset Ownership & Custody Engine Report

## Objective

Carbon asset creation is not enough. Every Carbon Asset Candidate must have a clear owner, custodian, and chain of ownership.

Sprint 24 adds a Global Ownership Ledger for verified MRV asset packages.

## Added Files

- `db/postgres/028_asset_ownership_schema.sql`
- `zenov_trust_layer/app/asset_ownership_routes.py`
- `zenov_trust_layer/app/services/ownership_service.py`
- `zenov_trust_layer/app/services/custody_service.py`
- `zenov_trust_layer/app/services/asset_transfer_service.py`
- `zenov_trust_layer/app/services/ownership_audit_service.py`

## API

- `GET /api/v1/assets/ownership/summary`
- `GET /api/v1/assets/{asset_id}/ownership`
- `POST /api/v1/assets/transfer`
- `GET /api/v1/assets/{asset_id}/history`

## Ownership Model

```text
Asset
↓
Owner
↓
Custodian
↓
Transfer History
```

Supported owner types:

- Driver
- Fleet Company
- Project Owner
- Partner Company
- Zenov Asset Pool
- Government Program

## Custody Rule

Beneficial owner and custodian are separated.

Default demo custodian:

```text
ZENOV_CUSTODY / Zenov Asset Pool
```

## Transfer Rule

Asset transfer records ownership history only.

It does not execute financial settlement.
It does not issue carbon credits.
It does not register an external registry record.

## Verification

Local API verification:

- CSV import: `SUCCESS`
- Asset Candidate generated: `YES`
- Ownership registered: `ANSAN_TRANS / Fleet Company`
- Custody registered: `ZENOV_CUSTODY`
- Transfer simulation: `TRANSFER_COMPLETED`
- New owner: `ZENOV_ASSET_POOL`
- History query: transfer history and chain of ownership returned

Browser verification:

- Ownership panel visible
- Ownership Summary loaded
- Latest Asset Ownership loaded
- Transfer to Zenov Pool simulated
- Ownership History loaded
- Browser console errors: `0`

## Final Rule

Carbon Asset Candidate is not a Carbon Credit.

It is a verified MRV data package with ownership, custody, and transfer history that can later support registry, settlement, and retirement workflows.
