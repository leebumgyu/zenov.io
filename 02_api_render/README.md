# ZENOV Render API Fixed Package

Use this package when Render deployment fails because the full platform package was uploaded in numbered chunks.

This is the production partner API for:

- `GET /health`
- `GET /api/v1/storage/status`
- `POST /api/v1/partners`
- `GET /api/v1/partners`
- `GET /api/v1/partners/{partner_id}`
- `GET /api/v1/executive-dashboard/summary`

## GitHub Upload

Upload the contents of this folder to a new GitHub repository or a clean repository root:

```text
render_api/
requirements.txt
render.yaml
README.md
```

## Render Settings

Root Directory:

```text
leave blank
```

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
python3 -m uvicorn render_api.main:app --host 0.0.0.0 --port $PORT
```

Environment Variables:

```text
DATABASE_URL=your Supabase PostgreSQL URL
ZENOV_ENV=PRODUCTION
```

## Test URLs

```text
https://YOUR-RENDER-URL.onrender.com/health
https://YOUR-RENDER-URL.onrender.com/api/v1/storage/status
```

Expected storage status:

```json
{
  "postgres": {
    "configured": true,
    "connected": true,
    "mode": "postgres"
  }
}
```
