from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any

from .database.partner_crud import (
    action_command_summary,
    business_project_summary,
    carbon_economy_summary,
    credit_readiness_summary,
    create_program,
    dashboard_partner_summary,
    generate_action_commands,
    generate_business_projects,
    generate_carbon_economy,
    generate_credit_readiness,
    generate_programs,
    generate_transformation_report,
    generate_transformations,
    certify_golden_template,
    get_action_command,
    get_business_project,
    get_carbon_economy,
    get_credit_readiness,
    get_golden_template,
    get_partner_pipeline,
    get_program,
    get_transformation,
    get_transformation_report,
    golden_template_summary,
    link_project_to_program,
    list_partner_pipeline,
    partner_market_intelligence_summary,
    program_dashboard,
    program_summary,
    save_partner_pipeline,
    save_partner_questionnaire,
    transformation_summary,
    update_action_command_status,
    update_business_project_status,
    update_partner_pipeline,
)
from .database.postgres import is_postgres_configured
from .services.partner_service import (
    connect_partner,
    partner_status,
    register_partner,
    partner_dashboard,
    partner_health,
    partner_imports,
    partner_mapping_errors,
)
from .services.partner_gateway import ingest_partner_payload


router = APIRouter(prefix="/api/v1/partners", tags=["partners"])
executive_router = APIRouter(prefix="/api/v1/executive-dashboard", tags=["executive-dashboard"])
market_intelligence_router = APIRouter(prefix="/api/v1/market-intelligence", tags=["market-intelligence"])
action_command_router = APIRouter(prefix="/api/v1/action-commands", tags=["action-commands"])
business_project_router = APIRouter(prefix="/api/v1/projects", tags=["business-projects"])
program_router = APIRouter(prefix="/api/v1/programs", tags=["programs"])
credit_readiness_router = APIRouter(prefix="/api/v1/credit-readiness", tags=["credit-readiness"])
carbon_economy_router = APIRouter(prefix="/api/v1/economy", tags=["carbon-economy"])
transformation_router = APIRouter(prefix="/api/v1/transformation", tags=["transformation"])


class PartnerRegisterRequest(BaseModel):
    partner_id: Optional[str] = None
    partner_name: str
    partner_type: str = "TAXI_COMPANY"
    source_system: str = "TMONEY_CSV"
    data_format: str = "CSV"
    field_map: Optional[dict[str, str]] = None


class PartnerConnectRequest(BaseModel):
    partner_id: str
    integration_type: str = "CSV_IMPORT"
    endpoint_url: Optional[str] = None


class PartnerGatewayIngestRequest(BaseModel):
    partner_id: str
    source_type: str = "TMONEY_CSV"
    payload: dict = Field(default_factory=dict)


class PartnerPipelineRequest(BaseModel):
    partner_id: Optional[str] = None
    company_name: Optional[str] = None
    business_type: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    region: Optional[str] = None
    status: str = "NEW"
    mobility: dict[str, Any] = Field(default_factory=dict)
    energy: dict[str, Any] = Field(default_factory=dict)
    carbon_esg: dict[str, Any] = Field(default_factory=dict)
    documents: dict[str, Any] = Field(default_factory=dict)
    owner: dict[str, Any] = Field(default_factory=dict)
    next_action: dict[str, Any] = Field(default_factory=dict)
    meeting: dict[str, Any] = Field(default_factory=dict)
    proposal: dict[str, Any] = Field(default_factory=dict)
    sales_execution: dict[str, Any] = Field(default_factory=dict)
    partner_success: dict[str, Any] = Field(default_factory=dict)
    opportunity: dict[str, Any] = Field(default_factory=dict)
    sales_automation: dict[str, Any] = Field(default_factory=dict)


class PartnerPatchRequest(BaseModel):
    patch: dict[str, Any] = Field(default_factory=dict)


class QuestionnaireRequest(BaseModel):
    mobility: dict[str, Any] = Field(default_factory=dict)
    energy: dict[str, Any] = Field(default_factory=dict)
    carbon_esg: dict[str, Any] = Field(default_factory=dict)
    documents: dict[str, Any] = Field(default_factory=dict)


class ActionStatusRequest(BaseModel):
    action_status: str


class ProjectStatusRequest(BaseModel):
    status: str


class ProgramRequest(BaseModel):
    program_id: Optional[str] = None
    program_name: Optional[str] = None
    program_type: str = "REGIONAL_CARBON_PROGRAM"
    owner: Optional[str] = None
    region: str = "Global"
    status: str = "IDEA"


class ProgramProjectLinkRequest(BaseModel):
    project_id: str
    contribution_score: Optional[float] = None


def _handle_value_error(exc: ValueError):
    message = str(exc)
    if "VALIDATION_FAILED" in message:
        raise HTTPException(status_code=422, detail=message) from exc
    if "PARTNER_NOT_FOUND" in message:
        raise HTTPException(status_code=404, detail=message) from exc
    if "PROJECT_NOT_FOUND" in message:
        raise HTTPException(status_code=404, detail=message) from exc
    if "PROGRAM_NOT_FOUND" in message:
        raise HTTPException(status_code=404, detail=message) from exc
    raise HTTPException(status_code=400, detail=message) from exc


@router.post("")
def create_partner_pipeline(request: PartnerPipelineRequest):
    try:
        partner = save_partner_pipeline(request.model_dump(), actor="web")
        projects = generate_business_projects(partner.get("partner_id"), actor="web")
        storage_rule = "POSTGRES_DATABASE" if is_postgres_configured() else "SERVER_FILE_FALLBACK"
        return {
            "status": "SAVED",
            "storage_rule": storage_rule,
            "partner": partner,
            "business_projects": projects,
        }
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("")
def list_partner_pipeline_view():
    return {"status": "OK", "partners": list_partner_pipeline()}


@router.patch("/{partner_id}")
def patch_partner_pipeline(partner_id: str, request: PartnerPatchRequest):
    try:
        partner = update_partner_pipeline(partner_id, request.patch, actor="web")
        projects = generate_business_projects(partner_id, actor="web")
        return {"status": "UPDATED", "partner": partner, "business_projects": projects}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/{partner_id}/questionnaire")
def post_partner_questionnaire(partner_id: str, request: QuestionnaireRequest):
    try:
        partner = save_partner_questionnaire(partner_id, request.model_dump(), actor="web")
        projects = generate_business_projects(partner_id, actor="web")
        return {"status": "QUESTIONNAIRE_SAVED", "partner": partner, "business_projects": projects}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/{partner_id}/questionnaire")
def get_partner_questionnaire(partner_id: str):
    partner = get_partner_pipeline(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="PARTNER_NOT_FOUND")
    return {
        "status": "OK",
        "partner_id": partner_id,
        "questionnaire": {
            "mobility": partner.get("mobility", {}),
            "energy": partner.get("energy", {}),
            "carbon_esg": partner.get("carbon_esg", {}),
            "documents": partner.get("documents", {}),
        },
    }


@router.patch("/{partner_id}/status")
def patch_partner_status(partner_id: str, request: PartnerPatchRequest):
    try:
        status = request.patch.get("status")
        if not status:
            raise ValueError("STATUS_REQUIRED")
        return {"status": "STATUS_UPDATED", "partner": update_partner_pipeline(partner_id, {"status": status}, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/{partner_id}/actions")
def post_partner_action(partner_id: str, request: PartnerPatchRequest):
    try:
        return {"status": "ACTION_SAVED", "partner": update_partner_pipeline(partner_id, {"next_action": request.patch}, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/{partner_id}/meetings")
def post_partner_meeting(partner_id: str, request: PartnerPatchRequest):
    try:
        return {"status": "MEETING_SAVED", "partner": update_partner_pipeline(partner_id, {"meeting": request.patch}, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/{partner_id}/proposals")
def post_partner_proposal(partner_id: str, request: PartnerPatchRequest):
    try:
        return {"status": "PROPOSAL_SAVED", "partner": update_partner_pipeline(partner_id, {"proposal": request.patch}, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/{partner_id}/send-material")
def post_partner_send_material(partner_id: str, request: PartnerPatchRequest):
    try:
        return {"status": "MATERIAL_SAVED", "partner": update_partner_pipeline(partner_id, {"sales_execution": request.patch}, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@router.post("/{partner_id}/feedback")
def post_partner_feedback(partner_id: str, request: PartnerPatchRequest):
    try:
        return {"status": "FEEDBACK_SAVED", "partner": update_partner_pipeline(partner_id, {"sales_execution": {"feedback_log": request.patch}}, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/{partner_id}/conversion-score")
def get_partner_conversion_score(partner_id: str):
    partner = get_partner_pipeline(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="PARTNER_NOT_FOUND")
    execution = partner.get("sales_execution") or {}
    return {
        "partner_id": partner_id,
        "conversion_score": execution.get("conversion_score", 0),
        "conversion_status": execution.get("conversion_status", "LOW"),
    }


@router.post("/{partner_id}/monthly-report")
def post_partner_monthly_report(partner_id: str, request: PartnerPatchRequest):
    try:
        return {"status": "MONTHLY_REPORT_SAVED", "partner": update_partner_pipeline(partner_id, {"partner_success": request.patch}, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@router.get("/{partner_id}/success")
def get_partner_success(partner_id: str):
    partner = get_partner_pipeline(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="PARTNER_NOT_FOUND")
    return {"status": "OK", "partner_id": partner_id, "partner_success": partner.get("partner_success", {})}


@router.get("/dashboard/partner-success")
def get_partner_success_dashboard():
    return {"status": "OK", "partner_success": dashboard_partner_summary().get("partner_success", {})}


@executive_router.get("/summary")
def executive_summary():
    return {"status": "OK", **dashboard_partner_summary()}


@executive_router.get("/pipeline")
def executive_pipeline():
    summary = dashboard_partner_summary()
    return {"status": "OK", "partner_summary": summary["partner_summary"], "partners": summary["partners"]}


@executive_router.get("/opportunities")
def executive_opportunities():
    summary = dashboard_partner_summary()
    return {"status": "OK", "partners": summary["partners"]}


@executive_router.get("/revenue-expansion")
def executive_revenue_expansion():
    summary = dashboard_partner_summary()
    return {"status": "OK", "partner_success": summary["partner_success"], "partners": summary["partners"]}


@market_intelligence_router.get("/summary")
def market_intelligence_summary():
    return {"status": "OK", **partner_market_intelligence_summary()}


@action_command_router.post("/generate")
def generate_action_command_cards():
    return {"status": "GENERATED", **generate_action_commands(actor="web")}


@action_command_router.get("")
def list_action_command_cards():
    return {"status": "OK", **action_command_summary()}


@action_command_router.get("/{action_id}")
def get_action_command_card(action_id: str):
    command = get_action_command(action_id)
    if not command:
        raise HTTPException(status_code=404, detail="ACTION_COMMAND_NOT_FOUND")
    return {"status": "OK", "action_command": command}


@action_command_router.patch("/{action_id}/status")
def patch_action_command_status(action_id: str, request: ActionStatusRequest):
    try:
        return {"status": "UPDATED", "action_command": update_action_command_status(action_id, request.action_status, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@business_project_router.post("/generate")
def generate_business_project_cards(partner_id: Optional[str] = None):
    return {"status": "GENERATED", **generate_business_projects(partner_id=partner_id, actor="web")}


@business_project_router.get("")
def list_business_project_cards():
    return {"status": "OK", **business_project_summary()}


@business_project_router.get("/{project_id}")
def get_business_project_card(project_id: str):
    project = get_business_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="PROJECT_NOT_FOUND")
    return {"status": "OK", "project": project}


@business_project_router.patch("/{project_id}/status")
def patch_business_project_status(project_id: str, request: ProjectStatusRequest):
    try:
        return {"status": "UPDATED", "project": update_business_project_status(project_id, request.status, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@program_router.post("")
def create_program_view(request: ProgramRequest):
    try:
        return {"status": "SAVED", "program": create_program(request.model_dump(), actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@program_router.post("/generate")
def generate_program_cards():
    return {"status": "GENERATED", **generate_programs(actor="web")}


@program_router.get("")
def list_program_cards():
    return {"status": "OK", **program_summary()}


@program_router.get("/{program_id}")
def get_program_card(program_id: str):
    program = get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="PROGRAM_NOT_FOUND")
    return {"status": "OK", "program": program}


@program_router.post("/{program_id}/projects")
def link_program_project(program_id: str, request: ProgramProjectLinkRequest):
    try:
        return {
            "status": "LINKED",
            "program": link_project_to_program(
                program_id,
                request.project_id,
                request.contribution_score,
                actor="web",
            ),
        }
    except ValueError as exc:
        _handle_value_error(exc)


@program_router.get("/{program_id}/dashboard")
def get_program_dashboard(program_id: str):
    try:
        return {"status": "OK", **program_dashboard(program_id)}
    except ValueError as exc:
        _handle_value_error(exc)


@credit_readiness_router.post("/generate")
def generate_credit_readiness_cards(project_id: Optional[str] = None):
    return {"status": "GENERATED", **generate_credit_readiness(project_id=project_id, actor="web")}


@credit_readiness_router.get("")
def list_credit_readiness_cards():
    return {"status": "OK", **credit_readiness_summary()}


@credit_readiness_router.get("/{project_id}")
def get_credit_readiness_card(project_id: str):
    readiness = get_credit_readiness(project_id)
    if not readiness:
        raise HTTPException(status_code=404, detail="CREDIT_READINESS_NOT_FOUND")
    return {"status": "OK", "credit_readiness": readiness}


@carbon_economy_router.post("/generate")
def generate_carbon_economy_cards(project_id: Optional[str] = None):
    return {"status": "GENERATED", **generate_carbon_economy(project_id=project_id, actor="web")}


@carbon_economy_router.get("/summary")
def list_carbon_economy_cards():
    return {"status": "OK", **carbon_economy_summary()}


@carbon_economy_router.get("/value-chain/{project_id}")
def get_economy_value_chain(project_id: str):
    economy = get_carbon_economy(project_id)
    if not economy:
        raise HTTPException(status_code=404, detail="CARBON_ECONOMY_NOT_FOUND")
    return {
        "status": "OK",
        "project_id": project_id,
        "value_chain": economy.get("value_chain", []),
        "carbon_economy_map": economy.get("carbon_economy_map", {}),
    }


@carbon_economy_router.get("/revenue-distribution/{project_id}")
def get_economy_revenue_distribution(project_id: str):
    economy = get_carbon_economy(project_id)
    if not economy:
        raise HTTPException(status_code=404, detail="CARBON_ECONOMY_NOT_FOUND")
    return {
        "status": "OK",
        "project_id": project_id,
        "revenue_distribution": economy.get("revenue_distribution", []),
        "economic_impact": economy.get("economic_impact", {}),
    }


@carbon_economy_router.get("/stakeholders/{project_id}")
def get_economy_stakeholders(project_id: str):
    economy = get_carbon_economy(project_id)
    if not economy:
        raise HTTPException(status_code=404, detail="CARBON_ECONOMY_NOT_FOUND")
    return {
        "status": "OK",
        "project_id": project_id,
        "stakeholders": economy.get("stakeholders", []),
        "benefits": economy.get("benefits", []),
    }


@transformation_router.post("/generate")
def generate_transformation_cards(partner_id: Optional[str] = None):
    return {"status": "GENERATED", **generate_transformations(partner_id=partner_id, actor="web")}


@transformation_router.get("/summary")
def list_transformation_cards():
    return {"status": "OK", **transformation_summary()}


@transformation_router.get("/partners/{partner_id}")
def get_transformation_card(partner_id: str):
    transformation = get_transformation(partner_id)
    if not transformation:
        raise HTTPException(status_code=404, detail="TRANSFORMATION_NOT_FOUND")
    return {"status": "OK", "transformation": transformation}


@transformation_router.post("/report/{partner_id}")
def generate_transformation_report_card(partner_id: str):
    try:
        return {"status": "GENERATED", "report": generate_transformation_report(partner_id, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@transformation_router.get("/report/{partner_id}")
def get_transformation_report_card(partner_id: str):
    report = get_transformation_report(partner_id)
    if not report:
        raise HTTPException(status_code=404, detail="TRANSFORMATION_REPORT_NOT_FOUND")
    return {"status": "OK", "report": report}


@transformation_router.post("/golden-template/{partner_id}")
def certify_golden_template_card(partner_id: str):
    try:
        return {"status": "CERTIFIED", "golden_template": certify_golden_template(partner_id, actor="web")}
    except ValueError as exc:
        _handle_value_error(exc)


@transformation_router.get("/golden-template/{partner_id}")
def get_golden_template_card(partner_id: str):
    certification = get_golden_template(partner_id)
    if not certification:
        raise HTTPException(status_code=404, detail="GOLDEN_TEMPLATE_NOT_FOUND")
    return {"status": "OK", "golden_template": certification}


@transformation_router.get("/golden-template")
def list_golden_template_cards():
    return {"status": "OK", **golden_template_summary()}


@router.post("/register")
def register_partner_view(request: PartnerRegisterRequest):
    return register_partner(**request.model_dump())


@router.post("/connect")
def connect_partner_view(request: PartnerConnectRequest):
    try:
        return connect_partner(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/status")
def get_partner_status(partner_id: Optional[str] = None):
    return partner_status(partner_id)


@router.get("/health")
def get_partner_hub_health(partner_id: Optional[str] = None):
    if partner_id:
        return partner_health(partner_id)
    return partner_status(None)


@router.post("/gateway/ingest")
def ingest_partner_gateway_payload(request: PartnerGatewayIngestRequest):
    try:
        return ingest_partner_payload(
            partner_id=request.partner_id,
            source_type=request.source_type,
            payload=request.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{partner_id}")
def get_partner_pipeline_view(partner_id: str):
    partner = get_partner_pipeline(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="PARTNER_NOT_FOUND")
    return {"status": "OK", "partner": partner}


@router.get("/{partner_id}/dashboard")
def get_partner_dashboard(partner_id: str):
    return partner_dashboard(partner_id)


@router.get("/{partner_id}/health")
def get_partner_health(partner_id: str):
    return partner_health(partner_id)


@router.get("/{partner_id}/imports")
def get_partner_imports(partner_id: str):
    return partner_imports(partner_id)


@router.get("/{partner_id}/mapping-errors")
def get_partner_mapping_errors(partner_id: str):
    return partner_mapping_errors(partner_id)
