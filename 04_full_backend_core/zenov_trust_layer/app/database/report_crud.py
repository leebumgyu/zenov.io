from typing import Any, Optional

from ..storage import mrv_reports, save_mrv_report_memory


def save_report(report: dict[str, Any]) -> None:
    save_mrv_report_memory(report)


def get_report(report_id: str) -> Optional[dict[str, Any]]:
    return mrv_reports.get(report_id)


def list_reports() -> list[dict[str, Any]]:
    return sorted(mrv_reports.values(), key=lambda item: item.get("created_at", ""), reverse=True)
