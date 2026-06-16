# ZENOV Production Deployment Package

This folder is the latest deployment-ready package for Zenov.

Package name:

```text
ZENOV_DEPLOY_READY_20260616_V2
```

Use this package for GitHub, Vercel, and Render deployment.

---

## 1. What To Upload To GitHub

Upload the entire folder:

```text
ZENOV_DEPLOY_READY_20260616_V2
```

Required structure:

```text
ZENOV_DEPLOY_READY_20260616_V2/
├── 00_production_documents
├── 01_frontend_vercel
├── 02_api_render
├── 03_database_and_docs
├── 04_full_backend_core
├── 05_full_backend_services
└── README_PRODUCTION_DEPLOYMENT.md
```

Do not remove:

```text
04_full_backend_core
05_full_backend_services
```

The backend service files must stay included. Missing service files can break Render API deployment.

---

## 2. Vercel Frontend Deployment

Use this folder for Vercel:

```text
ZENOV_DEPLOY_READY_20260616_V2/01_frontend_vercel
```

Vercel settings:

```text
Framework Preset: Other
Root Directory: ZENOV_DEPLOY_READY_20260616_V2/01_frontend_vercel
Build Command: leave empty
Output Directory: leave empty
Install Command: leave empty
```

Main files:

```text
index.html
app.css
app.js
partner/index.html
education.html
locales/
education/
```

Production frontend behavior:

```text
01 Partner Registration & Analysis
02 Partner Dashboard
03 ESG Education Materials
```

The frontend no longer depends on:

```text
/demo-web
127.0.0.1
```

It is ready for root-domain deployment such as:

```text
https://zenov.io
```

---

## 3. Render API Deployment

Use this folder for Render:

```text
ZENOV_DEPLOY_READY_20260616_V2/02_api_render
```

Render settings:

```text
Root Directory: ZENOV_DEPLOY_READY_20260616_V2/02_api_render
Build Command: pip install -r requirements.txt
Start Command: python3 -m uvicorn render_api.main:app --host 0.0.0.0 --port $PORT
```

Important files:

```text
render.yaml
requirements.txt
render_api/main.py
render_api/__init__.py
```

Health check endpoint:

```text
/api/health
```

Partner save endpoint:

```text
/api/v1/partners
```

---

## 4. Deployment Order

Follow this order:

```text
1. Upload ZENOV_DEPLOY_READY_20260616_V2 to GitHub
2. Connect Vercel to 01_frontend_vercel
3. Verify https://zenov.io opens
4. Connect Render to 02_api_render
5. Verify Render /api/health
6. Connect frontend API URL if needed
7. Test Partner Registration & Analysis save button
```

---

## 5. Pre-Deployment Verification

Run this command from the project root:

```bash
python3 ZENOV_DEPLOY_READY_20260616_V2/00_production_documents/verify_production_package.py
```

Expected result:

```text
ZENOV_PRODUCTION_PACKAGE_OK
No required files are missing.
No forbidden files were found.
Every upload folder is under 100 files.
```

---

## 6. Current Verification Status

Latest local verification passed:

```text
ZENOV_PRODUCTION_PACKAGE_OK
```

Confirmed:

```text
Frontend files included
Partner folder loads without broken CSS
Save and analysis update button works
Language JSON files included
No /demo-web production dependency
No 127.0.0.1 hardcoded production links
Upload folders are under 100 files
```

---

## 7. Notes

Local browser testing can use:

```bash
cd ZENOV_DEPLOY_READY_20260616_V2/01_frontend_vercel
python3 -m http.server 8020
```

Then open:

```text
http://127.0.0.1:8020/
```

Production deployment should use Vercel and Render, not the local server.

