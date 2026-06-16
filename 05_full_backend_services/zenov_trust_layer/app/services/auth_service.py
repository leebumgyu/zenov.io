from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from ..database.auth_crud import (
    get_auth_session,
    get_partner_auth_account,
    get_password_reset_token,
    get_referral_auth_account,
    list_auth_audit_logs,
    list_partner_auth_accounts,
    list_referral_auth_accounts,
    save_auth_audit_log,
    save_auth_session,
    save_partner_auth_account,
    save_password_reset_token,
    save_referral_auth_account,
)

try:  # pragma: no cover - optional production dependency
    import bcrypt  # type: ignore
except Exception:  # pragma: no cover - local demo fallback
    bcrypt = None


PARTNER_ROLES = {
    "PARTNER_ADMIN": {
        "fleet:read",
        "driver:manage",
        "vehicle:manage",
        "report:read",
        "partner_code:manage",
        "mrv:read",
    },
    "PARTNER_MANAGER": {"fleet:read", "driver:read", "vehicle:read", "mrv:read", "report:read"},
    "PARTNER_READ_ONLY": {"fleet:read", "mrv:read", "report:read"},
    "PARTNER_FINANCE": {"settlement:read", "point:read", "marketplace:read", "report:read"},
}

REFERRAL_ROLES = {
    "REFERRAL_OWNER": {"referral:own:read", "reward:own:read"},
    "REFERRAL_AGENT": {"referral:link:create", "referral:status:read"},
    "REFERRAL_READ_ONLY": {"referral:own:read"},
}

LOCK_THRESHOLD = 5
SESSION_HOURS = 8


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-KR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def _hash_password(password: str) -> str:
    if bcrypt is not None:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        return f"bcrypt${hashed.decode('utf-8')}"
    salt = os.urandom(16)
    iterations = 210_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        base64.b64encode(salt).decode("ascii"),
        iterations,
        base64.b64encode(digest).decode("ascii"),
    )


def _verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("bcrypt$") and bcrypt is not None:
        return bool(bcrypt.checkpw(password.encode("utf-8"), password_hash.removeprefix("bcrypt$").encode("utf-8")))
    if password_hash.startswith("scrypt$"):
        try:
            _, salt_b64, n, r, p, digest_b64 = password_hash.split("$", 5)
            salt = base64.b64decode(salt_b64)
            expected = base64.b64decode(digest_b64)
            actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p))
            return hmac.compare_digest(actual, expected)
        except Exception:
            return False
    if password_hash.startswith("pbkdf2_sha256$"):
        try:
            _, salt_b64, iterations, digest_b64 = password_hash.split("$", 3)
            salt = base64.b64decode(salt_b64)
            expected = base64.b64decode(digest_b64)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
            return hmac.compare_digest(actual, expected)
        except Exception:
            return False
    return False


def _audit(
    *,
    account_type: str,
    subject_code: str,
    event_type: str,
    event_status: str,
    message: str,
    actor: str = "system",
    detail: dict[str, Any] | None = None,
) -> None:
    save_auth_audit_log(
        {
            "auth_audit_id": _new_id("AAUD"),
            "account_type": account_type,
            "subject_code": subject_code,
            "event_type": event_type,
            "event_status": event_status,
            "message": message,
            "actor": actor,
            "detail": detail or {},
            "created_at": _now(),
        }
    )


def seed_demo_auth_accounts() -> None:
    ansan_account = get_partner_auth_account("ANSAN_TRANS")
    if not ansan_account:
        save_partner_auth_account(
            {
                "partner_code": "ANSAN_TRANS",
                "partner_name": "안산교통",
                "tenant_id": "TENANT-ANSAN-001",
                "sub_unit_code": "ANSAN_GARAGE_01",
                "contract_status": "ACTIVE",
                "role": "PARTNER_ADMIN",
                "access_password_hash": _hash_password("ANSAN_ceo"),
                "status": "ACTIVE",
                "failed_login_count": 0,
                "locked_at": None,
                "created_at": _now(),
                "updated_at": _now(),
            }
        )
    elif not _verify_password("ANSAN_ceo", ansan_account.get("access_password_hash", "")):
        ansan_account["access_password_hash"] = _hash_password("ANSAN_ceo")
        ansan_account["status"] = "ACTIVE"
        ansan_account["failed_login_count"] = 0
        ansan_account["locked_at"] = None
        ansan_account["updated_at"] = _now()
        save_partner_auth_account(ansan_account)
    if not get_partner_auth_account("BUSAN_TAXI"):
        save_partner_auth_account(
            {
                "partner_code": "BUSAN_TAXI",
                "partner_name": "부산택시 파일럿",
                "tenant_id": "TENANT-BUSAN-001",
                "sub_unit_code": "BUSAN_GARAGE_01",
                "contract_status": "ONBOARDING",
                "role": "PARTNER_MANAGER",
                "access_password_hash": _hash_password("Busan!2026"),
                "status": "ACTIVE",
                "failed_login_count": 0,
                "locked_at": None,
                "created_at": _now(),
                "updated_at": _now(),
            }
        )
    if not get_referral_auth_account("BEN-REF-001"):
        save_referral_auth_account(
            {
                "referral_code": "BEN-REF-001",
                "owner_type": "SALES_MANAGER",
                "owner_name": "Ben",
                "linked_partner_code": "ANSAN_TRANS",
                "linked_sub_unit_code": "ANSAN_GARAGE_01",
                "reward_policy_id": "REF-TAXI-001",
                "role": "REFERRAL_OWNER",
                "access_password_hash": _hash_password("BenRef!2026"),
                "status": "ACTIVE",
                "failed_login_count": 0,
                "locked_at": None,
                "created_at": _now(),
                "updated_at": _now(),
            }
        )


def _permissions_for(account_type: str, role: str) -> set[str]:
    if account_type == "PARTNER":
        return set(PARTNER_ROLES.get(role, set()))
    return set(REFERRAL_ROLES.get(role, set()))


def _public_account(account_type: str, account: dict[str, Any]) -> dict[str, Any]:
    code_key = "partner_code" if account_type == "PARTNER" else "referral_code"
    permissions = sorted(_permissions_for(account_type, account["role"]))
    return {
        "account_type": account_type,
        code_key: account[code_key],
        "display_name": account.get("partner_name") or account.get("owner_name"),
        "tenant_id": account.get("tenant_id"),
        "linked_partner_code": account.get("linked_partner_code"),
        "role": account["role"],
        "status": account["status"],
        "permissions": permissions,
        "can_access_partner_admin": account_type == "PARTNER" and account["role"] == "PARTNER_ADMIN",
        "can_modify_referral_reward_policy": False,
    }


def _public_partner_code(account: dict[str, Any]) -> dict[str, Any]:
    return {
        "partner_code": account["partner_code"],
        "partner_name": account.get("partner_name"),
        "tenant_id": account.get("tenant_id"),
        "sub_unit_code": account.get("sub_unit_code", ""),
        "contract_status": account.get("contract_status", "ACTIVE"),
        "role": account.get("role"),
        "status": account.get("status"),
        "access_password_hash_present": bool(account.get("access_password_hash")),
        "created_at": account.get("created_at"),
        "updated_at": account.get("updated_at"),
    }


def _public_referral_code(account: dict[str, Any]) -> dict[str, Any]:
    return {
        "referral_code": account["referral_code"],
        "owner_type": account.get("owner_type"),
        "owner_name": account.get("owner_name"),
        "linked_partner_code": account.get("linked_partner_code"),
        "linked_sub_unit_code": account.get("linked_sub_unit_code", ""),
        "reward_policy_id": account.get("reward_policy_id"),
        "role": account.get("role"),
        "status": account.get("status"),
        "access_password_hash_present": bool(account.get("access_password_hash")),
        "created_at": account.get("created_at"),
        "updated_at": account.get("updated_at"),
    }


def _issue_session(account_type: str, account: dict[str, Any]) -> dict[str, Any]:
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=SESSION_HOURS)).isoformat()
    code_key = "partner_code" if account_type == "PARTNER" else "referral_code"
    session = {
        "session_id": _new_id("AUTH"),
        "access_token": token,
        "account_type": account_type,
        "subject_code": account[code_key],
        "role": account["role"],
        "issued_at": _now(),
        "expires_at": expires_at,
    }
    save_auth_session(session)
    return session


def _login(*, account_type: str, code: str, password: str) -> dict[str, Any]:
    seed_demo_auth_accounts()
    getter = get_partner_auth_account if account_type == "PARTNER" else get_referral_auth_account
    account = getter(code)
    if not account:
        _audit(
            account_type=account_type,
            subject_code=code,
            event_type="LOGIN_FAILED",
            event_status="FAILED",
            message="Unknown account attempted login.",
        )
        raise ValueError("INVALID_CREDENTIALS")
    if account.get("status") == "LOCKED":
        _audit(
            account_type=account_type,
            subject_code=code,
            event_type="INACTIVE_ACCOUNT_ACCESS",
            event_status="LOCKED",
            message="Locked account attempted login.",
        )
        raise PermissionError("ACCOUNT_LOCKED")
    if account.get("status") != "ACTIVE":
        _audit(
            account_type=account_type,
            subject_code=code,
            event_type="INACTIVE_ACCOUNT_ACCESS",
            event_status="BLOCKED",
            message="Inactive account attempted login.",
        )
        raise PermissionError("ACCOUNT_INACTIVE")
    if not _verify_password(password, account["access_password_hash"]):
        account["failed_login_count"] = int(account.get("failed_login_count") or 0) + 1
        if account["failed_login_count"] >= LOCK_THRESHOLD:
            account["status"] = "LOCKED"
            account["locked_at"] = _now()
            event_type, status, message = "ACCOUNT_LOCKED", "LOCKED", "Account locked after repeated failed login attempts."
        else:
            event_type, status, message = "LOGIN_FAILED", "FAILED", "Password verification failed."
        account["updated_at"] = _now()
        _audit(account_type=account_type, subject_code=code, event_type=event_type, event_status=status, message=message)
        raise PermissionError("ACCOUNT_LOCKED" if account["status"] == "LOCKED" else "INVALID_CREDENTIALS")
    account["failed_login_count"] = 0
    account["last_login_at"] = _now()
    account["updated_at"] = _now()
    session = _issue_session(account_type, account)
    _audit(
        account_type=account_type,
        subject_code=code,
        event_type="LOGIN_SUCCESS",
        event_status="SUCCESS",
        message="Login success.",
        actor=code,
        detail={"role": account["role"]},
    )
    return {
        "status": "SUCCESS",
        "token_type": "Bearer",
        "access_token": session["access_token"],
        "expires_at": session["expires_at"],
        "account": _public_account(account_type, account),
    }


def partner_login(partner_code: str, password: str) -> dict[str, Any]:
    return _login(account_type="PARTNER", code=partner_code, password=password)


def referral_login(referral_code: str, password: str) -> dict[str, Any]:
    return _login(account_type="REFERRAL", code=referral_code, password=password)


def create_partner_code(
    *,
    partner_code: str,
    partner_name: str,
    password: str,
    tenant_id: str,
    sub_unit_code: str = "",
    contract_status: str = "ACTIVE",
    role: str = "PARTNER_ADMIN",
    status: str = "ACTIVE",
) -> dict[str, Any]:
    if role not in PARTNER_ROLES:
        raise ValueError("INVALID_PARTNER_ROLE")
    normalized_status = status.upper()
    account = {
        "partner_code": partner_code,
        "partner_name": partner_name,
        "tenant_id": tenant_id,
        "sub_unit_code": sub_unit_code,
        "contract_status": contract_status,
        "role": role,
        "access_password_hash": _hash_password(password),
        "status": normalized_status,
        "failed_login_count": 0,
        "locked_at": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_partner_auth_account(account)
    _audit(
        account_type="PARTNER",
        subject_code=partner_code,
        event_type="PARTNER_CODE_CREATED",
        event_status="SUCCESS",
        message="Partner Code created and password hash stored.",
        actor=partner_code,
        detail={"tenant_id": tenant_id, "role": role, "contract_status": contract_status},
    )
    return {"status": "CREATED", "partner_code": _public_partner_code(account)}


def update_partner_code(partner_code: str, updates: dict[str, Any]) -> dict[str, Any]:
    account = get_partner_auth_account(partner_code)
    if not account:
        raise ValueError("PARTNER_CODE_NOT_FOUND")
    allowed_fields = {"partner_name", "tenant_id", "sub_unit_code", "contract_status", "role", "status", "password"}
    for key, value in updates.items():
        if key not in allowed_fields or value in {None, ""}:
            continue
        if key == "role" and value not in PARTNER_ROLES:
            raise ValueError("INVALID_PARTNER_ROLE")
        if key == "password":
            account["access_password_hash"] = _hash_password(str(value))
        elif key == "status":
            account[key] = str(value).upper()
        else:
            account[key] = value
    account["updated_at"] = _now()
    save_partner_auth_account(account)
    _audit(
        account_type="PARTNER",
        subject_code=partner_code,
        event_type="PARTNER_CODE_UPDATED",
        event_status="SUCCESS",
        message="Partner Code updated.",
        actor=partner_code,
        detail={k: v for k, v in updates.items() if k != "password"},
    )
    return {"status": "UPDATED", "partner_code": _public_partner_code(account)}


def disable_partner_code(partner_code: str) -> dict[str, Any]:
    account = get_partner_auth_account(partner_code)
    if not account:
        raise ValueError("PARTNER_CODE_NOT_FOUND")
    account["status"] = "DISABLED"
    account["updated_at"] = _now()
    save_partner_auth_account(account)
    _audit(
        account_type="PARTNER",
        subject_code=partner_code,
        event_type="PARTNER_CODE_DISABLED",
        event_status="SUCCESS",
        message="Partner Code disabled.",
        actor=partner_code,
    )
    return {"status": "DISABLED", "partner_code": _public_partner_code(account)}


def verify_partner_code(partner_code: str, password: str) -> dict[str, Any]:
    seed_demo_auth_accounts()
    account = get_partner_auth_account(partner_code)
    if not account:
        _audit(
            account_type="PARTNER",
            subject_code=partner_code,
            event_type="PARTNER_CODE_VERIFY_FAILED",
            event_status="FAILED",
            message="Partner Code not found.",
        )
        raise ValueError("PARTNER_CODE_NOT_FOUND")
    if account.get("status") != "ACTIVE":
        _audit(
            account_type="PARTNER",
            subject_code=partner_code,
            event_type="PARTNER_CODE_VERIFY_FAILED",
            event_status="BLOCKED",
            message="Partner Code is not active.",
        )
        raise PermissionError("PARTNER_CODE_INACTIVE")
    if not _verify_password(password, account["access_password_hash"]):
        _audit(
            account_type="PARTNER",
            subject_code=partner_code,
            event_type="PARTNER_CODE_VERIFY_FAILED",
            event_status="FAILED",
            message="Partner Code password verification failed.",
        )
        raise PermissionError("INVALID_PARTNER_CODE_PASSWORD")
    _audit(
        account_type="PARTNER",
        subject_code=partner_code,
        event_type="PARTNER_CODE_VERIFIED",
        event_status="SUCCESS",
        message="Partner Code verified.",
        actor=partner_code,
    )
    return {"status": "VERIFIED", "partner_code": _public_partner_code(account)}


def list_partner_codes() -> dict[str, Any]:
    seed_demo_auth_accounts()
    items = [_public_partner_code(account) for account in list_partner_auth_accounts()]
    return {"count": len(items), "items": sorted(items, key=lambda item: item["partner_code"])}


def create_referral_code(
    *,
    referral_code: str,
    owner_type: str,
    owner_name: str,
    password: str,
    linked_partner_code: str,
    reward_policy_id: str,
    linked_sub_unit_code: str = "",
    role: str = "REFERRAL_OWNER",
    status: str = "ACTIVE",
) -> dict[str, Any]:
    if role not in REFERRAL_ROLES:
        raise ValueError("INVALID_REFERRAL_ROLE")
    normalized_status = status.upper()
    linked_partner = get_partner_auth_account(linked_partner_code)
    if not linked_partner:
        _audit(
            account_type="REFERRAL",
            subject_code=referral_code,
            event_type="REFERRAL_CODE_CREATE_FAILED",
            event_status="FAILED",
            message="Linked Partner Code not found.",
            detail={"linked_partner_code": linked_partner_code},
        )
        raise ValueError("LINKED_PARTNER_CODE_NOT_FOUND")
    account = {
        "referral_code": referral_code,
        "owner_type": owner_type,
        "owner_name": owner_name,
        "linked_partner_code": linked_partner_code,
        "linked_sub_unit_code": linked_sub_unit_code,
        "reward_policy_id": reward_policy_id,
        "role": role,
        "access_password_hash": _hash_password(password),
        "status": normalized_status,
        "failed_login_count": 0,
        "locked_at": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_referral_auth_account(account)
    _audit(
        account_type="REFERRAL",
        subject_code=referral_code,
        event_type="REFERRAL_CODE_CREATED",
        event_status="SUCCESS",
        message="Referral Code created and password hash stored.",
        actor=referral_code,
        detail={"linked_partner_code": linked_partner_code, "reward_policy_id": reward_policy_id},
    )
    return {"status": "CREATED", "referral_code": _public_referral_code(account)}


def update_referral_code(referral_code: str, updates: dict[str, Any]) -> dict[str, Any]:
    account = get_referral_auth_account(referral_code)
    if not account:
        raise ValueError("REFERRAL_CODE_NOT_FOUND")
    allowed_fields = {
        "owner_type",
        "owner_name",
        "linked_partner_code",
        "linked_sub_unit_code",
        "reward_policy_id",
        "role",
        "status",
        "password",
    }
    if updates.get("linked_partner_code") and not get_partner_auth_account(str(updates["linked_partner_code"])):
        raise ValueError("LINKED_PARTNER_CODE_NOT_FOUND")
    for key, value in updates.items():
        if key not in allowed_fields or value in {None, ""}:
            continue
        if key == "role" and value not in REFERRAL_ROLES:
            raise ValueError("INVALID_REFERRAL_ROLE")
        if key == "password":
            account["access_password_hash"] = _hash_password(str(value))
        elif key == "status":
            account[key] = str(value).upper()
        else:
            account[key] = value
    account["updated_at"] = _now()
    save_referral_auth_account(account)
    _audit(
        account_type="REFERRAL",
        subject_code=referral_code,
        event_type="REFERRAL_CODE_UPDATED",
        event_status="SUCCESS",
        message="Referral Code updated.",
        actor=referral_code,
        detail={k: v for k, v in updates.items() if k != "password"},
    )
    return {"status": "UPDATED", "referral_code": _public_referral_code(account)}


def disable_referral_code(referral_code: str) -> dict[str, Any]:
    account = get_referral_auth_account(referral_code)
    if not account:
        raise ValueError("REFERRAL_CODE_NOT_FOUND")
    account["status"] = "DISABLED"
    account["updated_at"] = _now()
    save_referral_auth_account(account)
    _audit(
        account_type="REFERRAL",
        subject_code=referral_code,
        event_type="REFERRAL_CODE_DISABLED",
        event_status="SUCCESS",
        message="Referral Code disabled.",
        actor=referral_code,
    )
    return {"status": "DISABLED", "referral_code": _public_referral_code(account)}


def verify_referral_code(referral_code: str, password: str) -> dict[str, Any]:
    seed_demo_auth_accounts()
    account = get_referral_auth_account(referral_code)
    if not account:
        _audit(
            account_type="REFERRAL",
            subject_code=referral_code,
            event_type="REFERRAL_CODE_VERIFY_FAILED",
            event_status="FAILED",
            message="Referral Code not found.",
        )
        raise ValueError("REFERRAL_CODE_NOT_FOUND")
    if account.get("status") != "ACTIVE":
        _audit(
            account_type="REFERRAL",
            subject_code=referral_code,
            event_type="REFERRAL_CODE_VERIFY_FAILED",
            event_status="BLOCKED",
            message="Referral Code is not active.",
        )
        raise PermissionError("REFERRAL_CODE_INACTIVE")
    if not _verify_password(password, account["access_password_hash"]):
        _audit(
            account_type="REFERRAL",
            subject_code=referral_code,
            event_type="REFERRAL_CODE_VERIFY_FAILED",
            event_status="FAILED",
            message="Referral Code password verification failed.",
        )
        raise PermissionError("INVALID_REFERRAL_CODE_PASSWORD")
    _audit(
        account_type="REFERRAL",
        subject_code=referral_code,
        event_type="REFERRAL_CODE_VERIFIED",
        event_status="SUCCESS",
        message="Referral Code verified.",
        actor=referral_code,
    )
    return {"status": "VERIFIED", "referral_code": _public_referral_code(account)}


def list_referral_codes() -> dict[str, Any]:
    seed_demo_auth_accounts()
    items = [_public_referral_code(account) for account in list_referral_auth_accounts()]
    return {"count": len(items), "items": sorted(items, key=lambda item: item["referral_code"])}


def get_current_auth(access_token: str) -> dict[str, Any]:
    seed_demo_auth_accounts()
    token = access_token.removeprefix("Bearer ").strip()
    session = get_auth_session(token)
    if not session:
        raise PermissionError("INVALID_SESSION")
    expires_at = datetime.fromisoformat(session["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        raise PermissionError("SESSION_EXPIRED")
    account = (
        get_partner_auth_account(session["subject_code"])
        if session["account_type"] == "PARTNER"
        else get_referral_auth_account(session["subject_code"])
    )
    if not account:
        raise PermissionError("ACCOUNT_NOT_FOUND")
    return {"status": "AUTHENTICATED", "session": {k: v for k, v in session.items() if k != "access_token"}, "account": _public_account(session["account_type"], account)}


def request_password_reset(account_type: str, code: str) -> dict[str, Any]:
    seed_demo_auth_accounts()
    normalized_type = account_type.upper()
    account = get_partner_auth_account(code) if normalized_type == "PARTNER" else get_referral_auth_account(code)
    if not account:
        _audit(account_type=normalized_type, subject_code=code, event_type="PASSWORD_RESET_REQUESTED", event_status="FAILED", message="Unknown account password reset requested.")
        return {"status": "REQUEST_ACCEPTED", "message": "If the account exists, a reset token has been generated."}
    token = secrets.token_urlsafe(24)
    reset = {
        "reset_token": token,
        "account_type": normalized_type,
        "subject_code": code,
        "status": "ACTIVE",
        "created_at": _now(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
    }
    save_password_reset_token(reset)
    _audit(account_type=normalized_type, subject_code=code, event_type="PASSWORD_RESET_REQUESTED", event_status="SUCCESS", message="Password reset token generated.", actor=code)
    return {
        "status": "REQUEST_ACCEPTED",
        "message": "POC reset token returned for local demo. Production must deliver it out-of-band.",
        "reset_token": token,
    }


def confirm_password_reset(reset_token: str, new_password: str) -> dict[str, Any]:
    reset = get_password_reset_token(reset_token)
    if not reset or reset.get("status") != "ACTIVE":
        raise PermissionError("INVALID_RESET_TOKEN")
    if datetime.fromisoformat(reset["expires_at"]) < datetime.now(timezone.utc):
        reset["status"] = "EXPIRED"
        raise PermissionError("RESET_TOKEN_EXPIRED")
    account = (
        get_partner_auth_account(reset["subject_code"])
        if reset["account_type"] == "PARTNER"
        else get_referral_auth_account(reset["subject_code"])
    )
    if not account:
        raise PermissionError("ACCOUNT_NOT_FOUND")
    account["access_password_hash"] = _hash_password(new_password)
    account["failed_login_count"] = 0
    account["locked_at"] = None
    account["status"] = "ACTIVE"
    account["updated_at"] = _now()
    reset["status"] = "USED"
    _audit(
        account_type=reset["account_type"],
        subject_code=reset["subject_code"],
        event_type="PASSWORD_CHANGED",
        event_status="SUCCESS",
        message="Password changed by reset flow.",
        actor=reset["subject_code"],
    )
    return {"status": "PASSWORD_CHANGED", "account_type": reset["account_type"], "subject_code": reset["subject_code"]}


def auth_admin_summary() -> dict[str, Any]:
    seed_demo_auth_accounts()
    return {
        "partner_accounts": [
            {k: v for k, v in account.items() if k != "access_password_hash"}
            for account in list_partner_auth_accounts()
        ],
        "referral_accounts": [
            {k: v for k, v in account.items() if k != "access_password_hash"}
            for account in list_referral_auth_accounts()
        ],
        "audit_log_count": len(list_auth_audit_logs()),
        "security_rule": "5 failed login attempts lock the account.",
    }


def auth_audit(subject_code: str | None = None) -> dict[str, Any]:
    return {"items": list_auth_audit_logs(subject_code), "count": len(list_auth_audit_logs(subject_code))}
