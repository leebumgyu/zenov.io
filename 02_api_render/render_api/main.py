import json
import os
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware


DATABASE_URL = os.getenv("DATABASE_URL", "")

app = FastAPI(title="ZENOV Partner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zenov.io",
        "https://www.zenov.io",
        "https://zenov-io.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:8010",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12].upper()}"


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
        "partner_id": str(partner_id),
        "company_name": payload.get("company_name") or "",
        "business_type": payload.get("business_type") or "",
        "contact_name": payload.get("contact_name") or "",
        "contact_phone": payload.get("contact_phone") or "",
        "contact_email": payload.get("contact_email") or "",
        "region": payload.get("region") or "",
        "status": payload.get("status") or "NEW",
        "updated_at": now_iso(),
    }
    partner.setdefault("created_at", now_iso())
    return partner


@app.get("/health")
def health():
    return {"status": "ok", "service": "zenov-partner-api"}


@app.get("/api/v1/storage/status")
def storage_status():
    if not DATABASE_URL:
        return {
            "status": "ok",
            "postgres": {"configured": False, "connected": False, "mode": "missing_database_url"},
        }
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        return {
            "status": "ok",
            "postgres": {"configured": True, "connected": True, "mode": "postgres"},
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
        conn.execute(
            """
            INSERT INTO partner_audit_logs (log_id, partner_id, event_type, event_json)
            VALUES (%(log_id)s, %(partner_id)s, 'PARTNER_SAVED', %(event_json)s::jsonb)
            """,
            {
                "log_id": new_id("LOG"),
                "partner_id": partner["partner_id"],
                "event_json": json.dumps({"saved_at": now_iso(), "status": partner["status"]}, ensure_ascii=False),
            },
        )
    return {"status": "SAVED", "storage_rule": "POSTGRES_DATABASE", "partner": partner}


@app.get("/api/v1/partners")
def list_partners():
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT payload_json FROM partners ORDER BY updated_at DESC"
        ).fetchall()
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
