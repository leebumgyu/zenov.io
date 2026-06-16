# 05. Production Test Checklist

## API Tests

Open:

```text
https://api.zenov.io/health
```

Expected:

```text
status ok
service zenov-partner-api
```

Open:

```text
https://api.zenov.io/api/v1/storage/status
```

Expected:

```text
configured true
connected true
mode postgres
```

## Frontend Tests

Open:

```text
https://zenov.io/
```

Check:

```text
CSS loads
Executive Dashboard opens
```

Open:

```text
https://zenov.io/partner/
```

Check:

```text
Partner Folder opens
Questionnaire fields are visible
Save button works
Save result says PostgreSQL DB Storage
```

## Data Test

Create test partner:

```text
Partner Code: TEST-PROD-001
Company Name: Production Test
Business Type: TAXI_COMPANY
```

Save.

Then open:

```text
https://api.zenov.io/api/v1/partners
```

Confirm the partner exists.

## Pass Condition

Production deployment is ready only when:

```text
Frontend opens on zenov.io
API opens on api.zenov.io
Partner save writes to PostgreSQL
Executive dashboard can read saved partner data
```

