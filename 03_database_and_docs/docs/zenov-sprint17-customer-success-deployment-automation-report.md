# ZENOV SPRINT 17 - Customer Success & Deployment Automation Report

## Objective

Reduce new customer onboarding time so a customer can connect data within 7 days, see the first MRV result within 30 days, and experience value within 90 days.

## Implemented Files

- `db/postgres/022_onboarding_schema.sql`
- `zenov_trust_layer/app/services/deployment_template_engine.py`
- `zenov_trust_layer/app/services/deployment_service.py`
- `zenov_trust_layer/app/services/onboarding_checklist.py`
- `zenov_trust_layer/app/services/customer_success_service.py`
- `zenov_trust_layer/app/customer_success_routes.py`

## API

- `POST /api/v1/customer-success/onboarding/start`
- `GET /api/v1/customer-success/onboarding`
- `GET /api/v1/customer-success/onboarding/{onboarding_id}/dashboard`
- `POST /api/v1/customer-success/onboarding/{onboarding_id}/milestones/{milestone_key}/complete`
- `POST /api/v1/customer-success/onboarding/{onboarding_id}/health-snapshot`
- `GET /api/v1/customer-success/templates`
- `POST /api/v1/customer-success/templates/bootstrap`

## Milestones

- Day 1: Data Connection
- Day 7: First Evidence
- Day 30: First MRV
- Day 60: Verification Completed
- Day 90: First Asset Created

## Customer Health Score

The first implementation calculates health from milestone completion:

- `GREEN`: customer has completed at least three key milestones.
- `YELLOW`: customer is in progress.
- `RED`: customer has a blocked milestone.

## Deployment Templates

The sprint adds config-driven onboarding templates. Taxi onboarding starts with:

- Template: `TPL-TAXI-TMONEY-CSV`
- Connector: `CSV_IMPORT`
- Sources: `TMONEY_CSV`, `TAXI_METER`, `DTG`, `GPS`, `CHARGER`

The rule is:

```text
New industry onboarding should use a template, not a code change.
```

## Demo Screen

The `/demo-web/` page now includes:

- Customer Success & Deployment Automation panel
- Start onboarding button
- Day 1 / Day 7 / Day 30 milestone completion buttons
- Health snapshot button

## Completion Criteria

- Customer onboarding project can be created.
- Partner setup template is selected.
- Deployment run is generated.
- Milestone checklist is generated.
- Health score is calculated.
- Health snapshot is stored.
