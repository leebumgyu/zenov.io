from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .ai_copilot_routes import router as ai_copilot_router
from .auth_routes import router as auth_router
from .asset_ownership_routes import router as asset_ownership_router
from .country_routes import router as country_router
from .customer_success_routes import router as customer_success_router
from .localization_routes import router as localization_router
from .methodology_routes import router as methodology_router
from .ops_routes import router as ops_router
from .partner_routes import action_command_router, business_project_router, carbon_economy_router, credit_readiness_router, executive_router, market_intelligence_router, program_router, router as partner_router, transformation_router
from .partner_referral_code_routes import partner_router as partner_code_router
from .partner_referral_code_routes import referral_router as referral_code_router
from .portfolio_kpi_routes import router as portfolio_kpi_router
from .production_routes import router as production_router
from .report_routes import router as report_router
from .routes import router
from .settlement_routes import router as settlement_router
from .tenant_middleware import TenantContextMiddleware
from .tenant_routes import router as tenant_router
from .wallet_routes import router as wallet_router
from .database.migrations import initialize_postgres_schema
from .database.postgres import postgres_status

app = FastAPI(
    title="ZENOV Trust Layer API",
    version="TRUST_LAYER_SPRINT_1",
    description="Global ID, Trust Packet, Validation Engine, Reject Log, and Audit Trail.",
)

app.add_middleware(TenantContextMiddleware)


@app.middleware("http")
async def no_cache_demo_web(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/demo-web"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.include_router(router)
app.include_router(auth_router)
app.include_router(report_router)
app.include_router(methodology_router)
app.include_router(wallet_router)
app.include_router(ops_router)
app.include_router(portfolio_kpi_router)
app.include_router(partner_router)
app.include_router(executive_router)
app.include_router(market_intelligence_router)
app.include_router(action_command_router)
app.include_router(business_project_router)
app.include_router(program_router)
app.include_router(credit_readiness_router)
app.include_router(carbon_economy_router)
app.include_router(transformation_router)
app.include_router(partner_code_router)
app.include_router(referral_code_router)
app.include_router(tenant_router)
app.include_router(settlement_router)
app.include_router(customer_success_router)
app.include_router(production_router)
app.include_router(country_router)
app.include_router(localization_router)
app.include_router(ai_copilot_router)
app.include_router(asset_ownership_router)


@app.on_event("startup")
def startup_initialize_database():
    app.state.postgres_schema = initialize_postgres_schema()

DEMO_WEB_DIR = Path(__file__).resolve().parents[2] / "outputs" / "zenov-mobility-data-platform" / "web"
if DEMO_WEB_DIR.exists():
    app.mount("/demo-web", StaticFiles(directory=DEMO_WEB_DIR, html=True), name="demo-web")


@app.get("/health")
def health():
    return {"status": "ok", "service": "zenov-trust-layer"}


@app.get("/api/v1/storage/status")
def storage_status():
    return {
        "status": "ok",
        "postgres": postgres_status(),
        "schema": getattr(app.state, "postgres_schema", {"configured": False, "applied": False}),
        "partner_file_fallback": str(
            Path(__file__).resolve().parents[2]
            / "outputs"
            / "zenov-mobility-data-platform"
            / "data"
            / "partner_pipeline_store.json"
        ),
    }
