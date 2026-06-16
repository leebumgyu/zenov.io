# 06. No Missing Files Rule

This deployment package was rebuilt to prevent the two failures seen previously:

```text
Frontend path failure
Backend services import failure
```

## Backend Rule

The full backend imports service files from:

```text
zenov_trust_layer/app/services
```

Therefore the final GitHub backend repository must include:

```text
zenov_trust_layer/app/main.py
zenov_trust_layer/app/services/auth_service.py
zenov_trust_layer/app/services/country_service.py
zenov_trust_layer/app/services/asset_transfer_service.py
zenov_trust_layer/app/services/localization_engine.py
zenov_trust_layer/app/services/executive_copilot_service.py
```

If `zenov_trust_layer/app/services` is missing, Render will fail.

## Correct Full Backend Upload Order

Upload these folders to the same GitHub repository root in this order:

```text
03_full_platform_root_config
04_full_backend_core
05_full_backend_services
06_db_docs
```

Do not upload the numbered folder names themselves.

## No Collision Check

`04_full_backend_core` and `05_full_backend_services` are intentionally split.

They do not overwrite each other because:

```text
04_full_backend_core contains:
zenov_trust_layer/app/main.py
zenov_trust_layer/app/*_routes.py
zenov_trust_layer/app/database/*

05_full_backend_services contains:
zenov_trust_layer/app/services/*
```

After upload, GitHub should merge them into one package:

```text
zenov_trust_layer/app/main.py
zenov_trust_layer/app/services/auth_service.py
```

## Fast Production Path

For the first production launch, use:

```text
01_frontend_vercel
02_api_render
```

The `02_api_render` package is self-contained and does not depend on the full `zenov_trust_layer/app/services` package.

