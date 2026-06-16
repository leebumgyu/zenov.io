# 07. GitHub Final Structure Check

Use this checklist after uploading files to GitHub.

## Vercel Frontend Repository

The GitHub root must show:

```text
index.html
app.css
app.js
partner/
education/
locales/
vercel.json
```

The GitHub root must not show:

```text
01_frontend_vercel/
ZENOV_PRODUCTION_DEPLOY_100MAX/
```

## Render API Repository

The GitHub root must show:

```text
README.md
render.yaml
requirements.txt
render_api/
```

Inside `render_api/`:

```text
__init__.py
main.py
```

The GitHub root must not show:

```text
02_api_render/
```

## Optional Full Backend Repository

The GitHub root must show:

```text
requirements.txt
render.yaml
zenov_trust_layer/
db/
docs/
```

Inside `zenov_trust_layer/app/services/`, verify:

```text
auth_service.py
asset_transfer_service.py
country_service.py
country_config_registry.py
localization_engine.py
executive_copilot_service.py
partner_service.py
```

The GitHub root must not show:

```text
03_full_platform_root_config/
04_full_backend_core/
05_full_backend_services/
06_db_docs/
```

