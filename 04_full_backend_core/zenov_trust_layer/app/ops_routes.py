from fastapi import APIRouter, HTTPException

from .services.ops_drilldown_service import (
    drilldown,
    drilldown_by_evidence,
    drilldown_by_job,
    drilldown_by_packet,
    retry_failed_row,
    root_cause_summary,
)


router = APIRouter(prefix="/api/v1/ops", tags=["operations"])


@router.get("/drilldown/{lookup_id}")
def get_ops_drilldown(lookup_id: str):
    result = drilldown(lookup_id)
    if result.get("traceability_status") == "BROKEN" and result.get("reason_code") in {"EVIDENCE_NOT_FOUND"}:
        raise HTTPException(status_code=404, detail=result)
    return result


@router.get("/drilldown/packet/{packet_id}")
def get_packet_drilldown(packet_id: str):
    return drilldown_by_packet(packet_id)


@router.get("/drilldown/evidence/{evidence_id}")
def get_evidence_drilldown(evidence_id: str):
    return drilldown_by_evidence(evidence_id)


@router.get("/drilldown/job/{job_id}")
def get_job_drilldown(job_id: str):
    result = drilldown_by_job(job_id)
    if result.get("traceability_status") == "BROKEN":
        raise HTTPException(status_code=404, detail="Import job not found")
    return result


@router.get("/root-cause/summary")
def get_root_cause_summary():
    return root_cause_summary()


@router.post("/retry/{import_job_row_id}")
def retry_import_row(import_job_row_id: str):
    result = retry_failed_row(import_job_row_id)
    if result.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=result)
    return result
