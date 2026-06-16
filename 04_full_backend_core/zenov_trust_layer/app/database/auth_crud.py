from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from ..storage import (
    auth_audit_logs,
    auth_sessions,
    partner_auth_accounts,
    password_reset_tokens,
    referral_auth_accounts,
    save_auth_audit_log_memory,
    save_auth_session_memory,
    save_partner_auth_account_memory,
    save_password_reset_token_memory,
    save_referral_auth_account_memory,
)

AUTH_STORE = (
    Path(__file__).resolve().parents[3]
    / "outputs"
    / "zenov-mobility-data-platform"
    / "data"
    / "auth_store.json"
)


def _read_store() -> dict[str, Any]:
    if not AUTH_STORE.exists():
        return {
            "partner_auth_accounts": {},
            "referral_auth_accounts": {},
            "auth_audit_logs": [],
            "auth_sessions": {},
            "password_reset_tokens": {},
        }
    try:
        return json.loads(AUTH_STORE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "partner_auth_accounts": {},
            "referral_auth_accounts": {},
            "auth_audit_logs": [],
            "auth_sessions": {},
            "password_reset_tokens": {},
        }


def _write_store(store: dict[str, Any]) -> None:
    AUTH_STORE.parent.mkdir(parents=True, exist_ok=True)
    AUTH_STORE.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def save_partner_auth_account(account: dict[str, Any]) -> dict[str, Any]:
    save_partner_auth_account_memory(account)
    store = _read_store()
    store.setdefault("partner_auth_accounts", {})
    store["partner_auth_accounts"][account["partner_code"]] = account
    _write_store(store)
    return account


def save_referral_auth_account(account: dict[str, Any]) -> dict[str, Any]:
    save_referral_auth_account_memory(account)
    store = _read_store()
    store.setdefault("referral_auth_accounts", {})
    store["referral_auth_accounts"][account["referral_code"]] = account
    _write_store(store)
    return account


def get_partner_auth_account(partner_code: str) -> Optional[dict[str, Any]]:
    account = partner_auth_accounts.get(partner_code)
    if account:
        return account
    account = _read_store().get("partner_auth_accounts", {}).get(partner_code)
    if account:
        save_partner_auth_account_memory(account)
    return account


def get_referral_auth_account(referral_code: str) -> Optional[dict[str, Any]]:
    account = referral_auth_accounts.get(referral_code)
    if account:
        return account
    account = _read_store().get("referral_auth_accounts", {}).get(referral_code)
    if account:
        save_referral_auth_account_memory(account)
    return account


def list_partner_auth_accounts() -> list[dict[str, Any]]:
    store_accounts = _read_store().get("partner_auth_accounts", {})
    combined = {**store_accounts, **partner_auth_accounts}
    return list(combined.values())


def list_referral_auth_accounts() -> list[dict[str, Any]]:
    store_accounts = _read_store().get("referral_auth_accounts", {})
    combined = {**store_accounts, **referral_auth_accounts}
    return list(combined.values())


def save_auth_session(session: dict[str, Any]) -> dict[str, Any]:
    save_auth_session_memory(session)
    store = _read_store()
    store.setdefault("auth_sessions", {})
    store["auth_sessions"][session["access_token"]] = session
    _write_store(store)
    return session


def get_auth_session(access_token: str) -> Optional[dict[str, Any]]:
    session = auth_sessions.get(access_token)
    if session:
        return session
    return _read_store().get("auth_sessions", {}).get(access_token)


def save_auth_audit_log(log: dict[str, Any]) -> dict[str, Any]:
    save_auth_audit_log_memory(log)
    store = _read_store()
    store.setdefault("auth_audit_logs", [])
    store["auth_audit_logs"].append(log)
    _write_store(store)
    return log


def list_auth_audit_logs(subject_code: str | None = None) -> list[dict[str, Any]]:
    combined = [*_read_store().get("auth_audit_logs", []), *auth_audit_logs]
    if subject_code:
        return [log for log in combined if log.get("subject_code") == subject_code]
    return combined


def save_password_reset_token(token: dict[str, Any]) -> dict[str, Any]:
    save_password_reset_token_memory(token)
    store = _read_store()
    store.setdefault("password_reset_tokens", {})
    store["password_reset_tokens"][token["reset_token"]] = token
    _write_store(store)
    return token


def get_password_reset_token(reset_token: str) -> Optional[dict[str, Any]]:
    token = password_reset_tokens.get(reset_token)
    if token:
        return token
    return _read_store().get("password_reset_tokens", {}).get(reset_token)
