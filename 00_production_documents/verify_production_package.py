from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "01_frontend_vercel/index.html",
    "01_frontend_vercel/app.css",
    "01_frontend_vercel/app.js",
    "01_frontend_vercel/partner/index.html",
    "01_frontend_vercel/vercel.json",
    "02_api_render/requirements.txt",
    "02_api_render/render.yaml",
    "02_api_render/render_api/__init__.py",
    "02_api_render/render_api/main.py",
    "04_full_backend_core/zenov_trust_layer/app/main.py",
    "04_full_backend_core/zenov_trust_layer/app/partner_routes.py",
    "04_full_backend_core/zenov_trust_layer/app/database/partner_crud.py",
    "05_full_backend_services/zenov_trust_layer/app/services/__init__.py",
    "05_full_backend_services/zenov_trust_layer/app/services/auth_service.py",
    "05_full_backend_services/zenov_trust_layer/app/services/asset_transfer_service.py",
    "05_full_backend_services/zenov_trust_layer/app/services/country_service.py",
    "05_full_backend_services/zenov_trust_layer/app/services/country_config_registry.py",
    "05_full_backend_services/zenov_trust_layer/app/services/localization_engine.py",
    "05_full_backend_services/zenov_trust_layer/app/services/executive_copilot_service.py",
    "05_full_backend_services/zenov_trust_layer/app/services/partner_service.py",
    "03_database_and_docs/db/postgres/031_partner_pipeline_production_schema.sql",
]


FORBIDDEN_NAMES = {
    ".DS_Store",
    ".env",
    "partner_pipeline_store.json",
    "auth_store.json",
}


def main() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    forbidden = [
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and (path.name in FORBIDDEN_NAMES or path.suffix.lower() == ".pdf")
    ]
    oversized = []
    for child in ROOT.iterdir():
        if child.is_dir():
            count = sum(1 for path in child.rglob("*") if path.is_file())
            if count > 100:
                oversized.append((child.name, count))

    if missing or forbidden or oversized:
        if missing:
            print("MISSING FILES:")
            for item in missing:
                print(f"- {item}")
        if forbidden:
            print("FORBIDDEN FILES:")
            for item in forbidden:
                print(f"- {item}")
        if oversized:
            print("FOLDERS OVER 100 FILES:")
            for name, count in oversized:
                print(f"- {name}: {count}")
        raise SystemExit(1)

    print("ZENOV_PRODUCTION_PACKAGE_OK")
    print("No required files are missing.")
    print("No forbidden files were found.")
    print("Every upload folder is under 100 files.")


if __name__ == "__main__":
    main()
