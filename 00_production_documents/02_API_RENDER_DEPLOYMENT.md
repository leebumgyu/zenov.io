# 02. API Render Deployment

## Purpose

Deploy the Zenov production API for:

```text
Partner Folder save
PostgreSQL storage status
Partner list
Executive dashboard summary
```

## Upload Folder

Upload the contents of:

```text
02_api_render
```

to a separate GitHub repository, recommended name:

```text
zenov-api
```

## Correct GitHub Root Structure

```text
README.md
render.yaml
requirements.txt
render_api/
  __init__.py
  main.py
```

Do not upload the `02_api_render` folder itself.

## Render Service Type

```text
New
Web Service
Connect GitHub repository: zenov-api
```

## Render Settings

```text
Root Directory:
blank

Build Command:
pip install -r requirements.txt

Start Command:
python3 -m uvicorn render_api.main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables

Required:

```text
DATABASE_URL=<Supabase PostgreSQL URL>
ZENOV_ENV=PRODUCTION
```

## Test URLs

After Render deployment:

```text
https://YOUR-RENDER-URL.onrender.com/health
```

Expected:

```json
{"status":"ok","service":"zenov-partner-api"}
```

Then:

```text
https://YOUR-RENDER-URL.onrender.com/api/v1/storage/status
```

Expected:

```text
configured: true
connected: true
mode: postgres
```

## Important

This is a Render Web Service.

Do not deploy this API as a Vercel Function.

