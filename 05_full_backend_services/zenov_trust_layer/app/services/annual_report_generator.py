from __future__ import annotations

from typing import Any


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _report_lines(report: dict[str, Any]) -> list[str]:
    snapshot = report["report_snapshot"]
    overview = snapshot["project_overview"]
    data = snapshot["data_summary"]
    mrv = snapshot["carbon_mrv_result"]
    verification = snapshot["verification_result"]
    evidence = snapshot["evidence_summary"]
    asset = snapshot["carbon_asset_summary"]
    certificate = snapshot.get("carbon_trust_certificate", {})
    return [
        "ZENOV CARBON TRUST VERIFIED",
        f"Report ID: {certificate.get('report_id')}",
        f"Methodology: {certificate.get('methodology')}",
        f"Methodology Version: {certificate.get('methodology_version')}",
        f"Verification Score: {certificate.get('verification_score')}",
        f"Verification Status: {certificate.get('verification_status')}",
        f"Asset Status: {certificate.get('asset_status')}",
        f"Generated At: {certificate.get('generated_at')}",
        f"Report Hash: {certificate.get('report_hash')}",
        "",
        "ZENOV Annual Carbon MRV Report",
        "",
        "A. Project Overview",
        f"Project Name: {overview.get('project_name')}",
        f"Owner Entity: {overview.get('owner_entity')}",
        f"Report Period: {overview.get('report_period_start')} to {overview.get('report_period_end')}",
        f"Methodology: {overview.get('methodology_id')} / {overview.get('methodology_version')}",
        f"Report Language: {overview.get('language_code', report.get('language_code', 'ko-KR'))}",
        "",
        "B. Data Summary",
        f"Vehicle Count: {data.get('vehicle_count')}",
        f"Total Distance km: {data.get('total_distance_km'):.3f}",
        f"Total Revenue KRW: {data.get('total_revenue'):.0f}",
        f"Operation Days: {data.get('operation_day_count')}",
        "",
        "C. Carbon MRV Result",
        f"Baseline kgCO2e: {mrv.get('baseline_emission_kgco2e'):.3f}",
        f"Project Emission kgCO2e: {mrv.get('project_emission_kgco2e'):.3f}",
        f"Reduction kgCO2e: {mrv.get('reduction_kgco2e'):.3f}",
        f"Reduction tCO2e: {mrv.get('reduction_tco2e'):.6f}",
        "",
        "D. Verification Result",
        f"Verification Score: {verification.get('verification_score')}",
        f"Verification Status: {verification.get('verification_status')}",
        f"Methodology Version: {verification.get('methodology_version')}",
        "",
        "E. Carbon Asset Summary",
        f"Asset Candidate Count: {asset.get('asset_candidate_count')}",
        f"Candidate Quantity tCO2e: {asset.get('candidate_quantity_tco2e'):.6f}",
        f"Registry Status Counts: {asset.get('registry_status_counts')}",
        "",
        "F. Evidence Summary",
        f"Packet Count: {evidence.get('packet_count')}",
        f"Evidence Count: {evidence.get('evidence_count')}",
        f"Hash Verified Count: {evidence.get('hash_verified_count')}",
        f"Signature Verified Count: {evidence.get('signature_verified_count')}",
        "",
        "Snapshot Integrity",
        f"Report ID: {report.get('report_id')}",
        f"Report Hash: {report.get('report_hash')}",
        f"Created At: {report.get('created_at')}",
        "",
        "Legal Notice",
        snapshot["legal_notice"],
    ]


def generate_report_pdf(report: dict[str, Any]) -> bytes:
    lines = _report_lines(report)
    content_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
    for index, line in enumerate(lines):
        if index:
            content_lines.append("T*")
        content_lines.append(f"({_pdf_escape(str(line))}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("utf-8")

    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)
