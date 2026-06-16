# 04. DNS Domain Setup

## Current Domain Roles

```text
zenov.io
www.zenov.io
  Frontend site on Vercel

api.zenov.io
  Backend API on Render
```

## GoDaddy DNS

Keep existing:

```text
NS records
MX records for Google Workspace
_domainconnect
```

Do not delete email DNS records.

## Add API Record

After Render API works, add:

```text
Type: CNAME
Name: api
Value: YOUR-RENDER-URL.onrender.com.
TTL: 600 seconds
```

After propagation, test:

```text
https://api.zenov.io/health
```

Expected:

```json
{"status":"ok","service":"zenov-partner-api"}
```

