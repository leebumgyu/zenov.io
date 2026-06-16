from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from .services.annual_report_generator import generate_report_pdf
from .services.report_service import generate_annual_report, get_mrv_report, list_mrv_reports


router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


class GenerateReportRequest(BaseModel):
    project_name: str = "Ansan Transport EV Taxi Carbon MRV"
    owner_entity: str = "ANSAN_TRANS"
    reporting_year: int = Field(default_factory=lambda: datetime.utcnow().year)
    methodology_id: Optional[str] = None
    methodology_version: Optional[str] = None
    language_code: str = "ko-KR"


@router.post("/generate")
def generate_report(request: GenerateReportRequest):
    return generate_annual_report(
        project_name=request.project_name,
        owner_entity=request.owner_entity,
        reporting_year=request.reporting_year,
        methodology_id=request.methodology_id,
        methodology_version=request.methodology_version,
        language_code=request.language_code,
    )


@router.get("")
def list_reports():
    return {"count": len(list_mrv_reports()), "items": list_mrv_reports()}


@router.get("/{report_id}")
def get_report(report_id: str):
    report = get_mrv_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/pdf")
def get_report_pdf(report_id: str):
    report = get_mrv_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    pdf = generate_report_pdf(report)
    filename = f"{report_id}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
