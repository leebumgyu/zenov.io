# ZENOV SPRINT 20 - ASEAN Localization & Multi-Country Framework Report

## Objective

Zenov is not a Korea-only platform. Sprint 20 adds a config-driven country framework so Korea, Thailand, Malaysia, Indonesia, and Vietnam can share the same Trust Layer while using country-specific carbon factors, currencies, languages, registry profiles, and report formats.

## Implemented Files

- `db/postgres/024_country_framework_schema.sql`
- `zenov_trust_layer/app/config/countries/KR.yaml`
- `zenov_trust_layer/app/config/countries/TH.yaml`
- `zenov_trust_layer/app/config/countries/MY.yaml`
- `zenov_trust_layer/app/config/countries/ID.yaml`
- `zenov_trust_layer/app/config/countries/VN.yaml`
- `zenov_trust_layer/app/services/country_config_registry.py`
- `zenov_trust_layer/app/services/country_service.py`
- `zenov_trust_layer/app/services/localization_engine.py`
- `zenov_trust_layer/app/services/methodology_adapter.py`
- `zenov_trust_layer/app/country_routes.py`

## API

- `GET /api/v1/countries`
- `POST /api/v1/countries/bootstrap`
- `POST /api/v1/countries`
- `GET /api/v1/countries/{country_code}`
- `POST /api/v1/countries/methodology-adapters`
- `GET /api/v1/countries/methodology-adapters/list`
- `POST /api/v1/countries/reports/localize`

## Country Profiles

Each country config includes:

- Country Code
- Language
- Currency
- Timezone
- Grid Emission Factor
- Fuel Emission Factors
- MRV Methodologies
- Local Registry
- Government Reporting Format
- Report Language and Labels

## Config-Driven Rule

```text
New country = add YAML config.
Core Trust Layer code must not change.
```

## Demo Screen

The `/demo-web/` page now includes:

- ASEAN Localization & Multi-Country Framework panel
- Country dashboard
- KR / TH / MY profile buttons
- Thailand report localization demo

## Current KPI

- Country onboarding target: 7 days or less by YAML config
- Localization coverage: 100% for configured country files
- Country-specific template count: 5
- Methodology adapter count: 5
