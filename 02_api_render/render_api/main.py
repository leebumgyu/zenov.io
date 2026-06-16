import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware


DATABASE_URL = os.getenv("DATABASE_URL", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SIGNALCARE_TO_EMAIL = os.getenv("SIGNALCARE_TO_EMAIL", "contact@zenov.io")
SIGNALCARE_CC_EMAIL = os.getenv("SIGNALCARE_CC_EMAIL", "zenovou@gmail.com")
SIGNALCARE_FROM_EMAIL = os.getenv("SIGNALCARE_FROM_EMAIL", "Zenov Website <contact@zenov.io>")

app = FastAPI(title="ZENOV Partner API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zenov.io",
        "https://www.zenov.io",
        "https://zenov-io.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:8010",
        "http://127.0.0.1:8020",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12].upper()}"


def clean(value: Any) -> str:
    return str(value or "").strip()


def number(value: Any) -> float:
    try:
        parsed = float(value or 0)
        return parsed if parsed == parsed else 0
    except (TypeError, ValueError):
        return 0


def format_krw(value: Any) -> str:
    return f"{int(round(number(value))):,} KRW"


def db_url() -> str:
    if not DATABASE_URL:
        raise HTTPException(status_code=503, detail="DATABASE_URL_NOT_CONFIGURED")
    return DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


def connect():
    return psycopg.connect(db_url(), autocommit=True)


def init_db() -> None:
    if not DATABASE_URL:
        return
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS partners (
              partner_id TEXT PRIMARY KEY,
              company_name TEXT,
              business_type TEXT,
              contact_name TEXT,
              contact_phone TEXT,
              contact_email TEXT,
              region TEXT,
              status TEXT NOT NULL DEFAULT 'NEW',
              payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS partner_audit_logs (
              log_id TEXT PRIMARY KEY,
              partner_id TEXT NOT NULL,
              event_type TEXT NOT NULL,
              event_json JSONB NOT NULL DEFAULT '{}'::jsonb,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


@app.on_event("startup")
def startup() -> None:
    init_db()


def normalized_partner(payload: Dict[str, Any]) -> Dict[str, Any]:
    partner_id = payload.get("partner_id") or payload.get("partner_code") or new_id("PARTNER")
    partner = {
        **payload,
        "partner_id": clean(partner_id),
        "company_name": clean(payload.get("company_name")),
        "ceo_name": clean(payload.get("ceo_name")),
        "business_type": clean(payload.get("business_type")),
        "contact_name": clean(payload.get("contact_name")),
        "contact_phone": clean(payload.get("contact_phone")),
        "contact_email": clean(payload.get("contact_email")),
        "region": clean(payload.get("region")),
        "status": clean(payload.get("status")) or "NEW",
        "updated_at": now_iso(),
    }
    partner.setdefault("created_at", now_iso())
    return partner


def recipient_list() -> List[str]:
    recipients = [SIGNALCARE_TO_EMAIL, SIGNALCARE_CC_EMAIL]
    return [email for email in (clean(item) for item in recipients) if email]


def html_row(label: str, value: Any) -> str:
    safe_value = clean(value) or "-"
    return (
        "<tr>"
        f"<td style=\"padding:8px 10px;border-bottom:1px solid #e7edf3;color:#64748b;width:210px;\">{label}</td>"
        f"<td style=\"padding:8px 10px;border-bottom:1px solid #e7edf3;color:#111827;font-weight:600;\">{safe_value}</td>"
        "</tr>"
    )


def build_partner_email_html(partner: Dict[str, Any]) -> str:
    mobility = partner.get("mobility") or {}
    energy = partner.get("energy") or {}
    cost = partner.get("cost_structure") or {}
    goals = partner.get("business_goals") or {}
    data_status = partner.get("data_status") or {}
    opportunity = partner.get("opportunity") or {}

    return f"""
    <div style="font-family:Arial,sans-serif;background:#f8fafc;padding:24px;">
      <div style="max-width:760px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
        <div style="background:#07111f;color:#ffffff;padding:22px 24px;">
          <div style="font-size:12px;letter-spacing:1.5px;color:#67e8f9;">ZENOV SMART ESG DIAGNOSIS</div>
          <h1 style="margin:8px 0 0;font-size:22px;">새 파트너 가입 및 분석 요청</h1>
        </div>
        <div style="padding:22px 24px;">
          <h2 style="font-size:16px;margin:0 0 10px;">회사 정보</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            {html_row("파트너 코드", partner.get("partner_id"))}
            {html_row("회사명", partner.get("company_name"))}
            {html_row("대표자", partner.get("ceo_name"))}
            {html_row("담당자", partner.get("contact_name"))}
            {html_row("연락처", partner.get("contact_phone"))}
            {html_row("이메일", partner.get("contact_email"))}
            {html_row("지역", partner.get("region"))}
            {html_row("사업유형", partner.get("business_type"))}
          </table>

          <h2 style="font-size:16px;margin:24px 0 10px;">현재 운영 현황</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            {html_row("보유 택시 수", int(number(mobility.get("taxi_count"))))}
            {html_row("전기택시 수", int(number(mobility.get("ev_taxi_count"))))}
            {html_row("보유 버스 수", int(number(mobility.get("bus_count"))))}
            {html_row("전기버스 수", int(number(mobility.get("ev_bus_count"))))}
            {html_row("태양광 설치 여부", energy.get("solar_installed"))}
            {html_row("태양광 용량", f'{number(energy.get("solar_capacity_kw")):,.0f} kW')}
            {html_row("EV 충전기 상태", energy.get("ev_charger_status"))}
            {html_row("EV 충전기 수", int(number(energy.get("charger_count"))))}
            {html_row("완속 충전기", int(number(energy.get("slow_charger_count"))))}
            {html_row("급속 충전기", int(number(energy.get("fast_charger_count"))))}
          </table>

          <h2 style="font-size:16px;margin:24px 0 10px;">비용 / 데이터 / 목표</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            {html_row("차량 1대당 월 연료비 평균", format_krw(cost.get("monthly_fuel_cost")))}
            {html_row("회사 월 전기 사용량", f'{number(cost.get("company_monthly_electricity_usage")):,.0f} kWh')}
            {html_row("월 전기요금", format_krw(cost.get("monthly_electricity_cost")))}
            {html_row("가장 부담되는 비용", cost.get("biggest_cost_burden"))}
            {html_row("GPS 데이터", data_status.get("gps_data_available"))}
            {html_row("충전 데이터", data_status.get("charging_data_available"))}
            {html_row("전력 데이터", data_status.get("power_data_available"))}
            {html_row("API 제공 가능", data_status.get("api_available"))}
            {html_row("1년 목표", goals.get("one_year_goal"))}
            {html_row("3년 목표", goals.get("three_year_goal"))}
            {html_row("5년 목표", goals.get("five_year_goal"))}
          </table>

          <h2 style="font-size:16px;margin:24px 0 10px;">Zenov 자동 분석</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            {html_row("추천 프로젝트", opportunity.get("expected_project"))}
            {html_row("예상 CO2e", f'{number(opportunity.get("estimated_co2e_ton")):,.1f} tCO2e')}
            {html_row("예상 Carbon Value", format_krw(opportunity.get("estimated_carbon_value_krw")))}
            {html_row("다음 액션", opportunity.get("next_action"))}
            {html_row("상태", partner.get("status"))}
            {html_row("저장 시각", partner.get("updated_at"))}
          </table>

          <p style="margin-top:24px;color:#64748b;font-size:12px;line-height:1.6;">
            이 메일은 Zenov 파트너 가입 및 분석 화면에서 자동 발송되었습니다.
          </p>
        </div>
      </div>
    </div>
    """


def build_partner_email_text(partner: Dict[str, Any]) -> str:
    mobility = partner.get("mobility") or {}
    energy = partner.get("energy") or {}
    opportunity = partner.get("opportunity") or {}
    return "\n".join(
        [
            "[ZENOV] 새 파트너 가입 및 분석 요청",
            "",
            f"파트너 코드: {clean(partner.get('partner_id'))}",
            f"회사명: {clean(partner.get('company_name'))}",
            f"대표자: {clean(partner.get('ceo_name'))}",
            f"담당자: {clean(partner.get('contact_name'))}",
            f"연락처: {clean(partner.get('contact_phone'))}",
            f"이메일: {clean(partner.get('contact_email'))}",
            f"지역: {clean(partner.get('region'))}",
            f"사업유형: {clean(partner.get('business_type'))}",
            "",
            f"보유 택시 수: {int(number(mobility.get('taxi_count')))}",
            f"전기택시 수: {int(number(mobility.get('ev_taxi_count')))}",
            f"태양광: {clean(energy.get('solar_installed'))} / {number(energy.get('solar_capacity_kw')):,.0f} kW",
            f"EV 충전기: {clean(energy.get('ev_charger_status'))} / {int(number(energy.get('charger_count')))}기",
            "",
            f"추천 프로젝트: {clean(opportunity.get('expected_project'))}",
            f"예상 CO2e: {number(opportunity.get('estimated_co2e_ton')):,.1f} tCO2e",
            f"예상 Carbon Value: {format_krw(opportunity.get('estimated_carbon_value_krw'))}",
            f"다음 액션: {clean(opportunity.get('next_action'))}",
        ]
    )


def send_partner_email(partner: Dict[str, Any]) -> Dict[str, Any]:
    if not RESEND_API_KEY:
        return {
            "ok": False,
            "error": "EMAIL_PROVIDER_NOT_CONFIGURED",
            "message": "Set RESEND_API_KEY in Render environment variables.",
        }

    recipients = recipient_list()
    if not recipients:
        return {"ok": False, "error": "EMAIL_RECIPIENT_NOT_CONFIGURED"}

    company_name = clean(partner.get("company_name")) or clean(partner.get("partner_id")) or "New Partner"
    payload = {
        "from": SIGNALCARE_FROM_EMAIL,
        "to": recipients,
        "subject": f"[ZENOV] 새 파트너 가입 및 분석 요청 - {company_name}",
        "html": build_partner_email_html(partner),
        "text": build_partner_email_text(partner),
    }

    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response_body = response.read().decode("utf-8")
            result = json.loads(response_body) if response_body else {}
            return {"ok": True, "recipients": recipients, "id": result.get("id")}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        return {
            "ok": False,
            "error": "EMAIL_SEND_FAILED",
            "status_code": exc.code,
            "detail": detail,
        }
    except Exception as exc:
        return {"ok": False, "error": "EMAIL_SEND_FAILED", "message": str(exc)}


def write_audit_log(partner_id: str, event_type: str, event_json: Dict[str, Any]) -> None:
    if not DATABASE_URL:
        return
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO partner_audit_logs (log_id, partner_id, event_type, event_json)
            VALUES (%(log_id)s, %(partner_id)s, %(event_type)s, %(event_json)s::jsonb)
            """,
            {
                "log_id": new_id("LOG"),
                "partner_id": partner_id,
                "event_type": event_type,
                "event_json": json.dumps(event_json, ensure_ascii=False),
            },
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "zenov-partner-api",
        "email": {
            "configured": bool(RESEND_API_KEY),
            "to": SIGNALCARE_TO_EMAIL,
            "cc": SIGNALCARE_CC_EMAIL,
            "from": SIGNALCARE_FROM_EMAIL,
        },
    }


@app.get("/api/v1/storage/status")
def storage_status():
    if not DATABASE_URL:
        return {
            "status": "ok",
            "postgres": {"configured": False, "connected": False, "mode": "missing_database_url"},
            "email": {"configured": bool(RESEND_API_KEY)},
        }
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        return {
            "status": "ok",
            "postgres": {"configured": True, "connected": True, "mode": "postgres"},
            "email": {"configured": bool(RESEND_API_KEY)},
        }
    except Exception as exc:
        return {
            "status": "error",
            "postgres": {
                "configured": True,
                "connected": False,
                "mode": "postgres_error",
                "error": str(exc),
            },
            "email": {"configured": bool(RESEND_API_KEY)},
        }


@app.post("/api/v1/partners")
async def save_partner(request: Request):
    init_db()
    payload = await request.json()
    partner = normalized_partner(payload)

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO partners (
              partner_id, company_name, business_type, contact_name, contact_phone,
              contact_email, region, status, payload_json, created_at, updated_at
            )
            VALUES (
              %(partner_id)s, %(company_name)s, %(business_type)s, %(contact_name)s,
              %(contact_phone)s, %(contact_email)s, %(region)s, %(status)s,
              %(payload_json)s::jsonb, NOW(), NOW()
            )
            ON CONFLICT (partner_id) DO UPDATE SET
              company_name = EXCLUDED.company_name,
              business_type = EXCLUDED.business_type,
              contact_name = EXCLUDED.contact_name,
              contact_phone = EXCLUDED.contact_phone,
              contact_email = EXCLUDED.contact_email,
              region = EXCLUDED.region,
              status = EXCLUDED.status,
              payload_json = EXCLUDED.payload_json,
              updated_at = NOW()
            """,
            {
                **partner,
                "payload_json": json.dumps(partner, ensure_ascii=False),
            },
        )

    write_audit_log(
        partner["partner_id"],
        "PARTNER_SAVED",
        {"saved_at": now_iso(), "status": partner["status"]},
    )

    email_result = send_partner_email(partner)
    write_audit_log(
        partner["partner_id"],
        "PARTNER_EMAIL_SENT" if email_result.get("ok") else "PARTNER_EMAIL_FAILED",
        {"email": email_result, "created_at": now_iso()},
    )

    return {
        "status": "SAVED",
        "storage_rule": "POSTGRES_DATABASE",
        "partner": partner,
        "email": email_result,
    }


@app.post("/api/partner-lead-email")
async def partner_lead_email(request: Request):
    payload = await request.json()
    partner = normalized_partner(payload.get("partner") or payload)
    email_result = send_partner_email(partner)
    if not email_result.get("ok"):
        raise HTTPException(status_code=503, detail=email_result)
    return {"status": "SENT", "email": email_result}


@app.get("/api/v1/partners")
def list_partners():
    init_db()
    with connect() as conn:
        rows = conn.execute("SELECT payload_json FROM partners ORDER BY updated_at DESC").fetchall()
    partners = [row[0] for row in rows]
    return {"status": "OK", "partners": partners}


@app.get("/api/v1/partners/{partner_id}")
def get_partner(partner_id: str):
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT payload_json FROM partners WHERE partner_id = %s",
            (partner_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="PARTNER_NOT_FOUND")
    return {"status": "OK", "partner": row[0]}


@app.get("/api/v1/executive-dashboard/summary")
def executive_summary():
    init_db()
    with connect() as conn:
        rows = conn.execute("SELECT status, payload_json FROM partners").fetchall()
    partners = [row[1] for row in rows]
    total = len(partners)
    operating = sum(1 for item in partners if item.get("status") == "OPERATING")
    return {
        "status": "OK",
        "storage_mode": "postgres",
        "pipeline": {
            "total_partners": total,
            "operating_partners": operating,
            "new_partners": sum(1 for item in partners if item.get("status") == "NEW"),
        },
        "partners": partners,
    }


@app.post("/api/v1/action-commands/generate")
def generate_action_commands():
    return {"status": "OK", "commands": []}


@app.get("/api/v1/action-commands")
def list_action_commands():
    return {"status": "OK", "commands": []}
