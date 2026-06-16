from datetime import datetime
from typing import Optional
from uuid import uuid4


def create_global_id(object_type: str, region: str, domain: str, dt: Optional[datetime] = None) -> str:
    issued_at = dt or datetime.utcnow()
    yyyymmdd = issued_at.strftime("%Y%m%d")
    suffix = uuid4().hex[:8].upper()
    normalized_type = object_type.strip().upper()
    normalized_region = region.strip().upper()
    normalized_domain = domain.strip().upper()
    return f"{normalized_type}-{normalized_region}-{normalized_domain}-{yyyymmdd}-{suffix}"


def create_packet_id(region: str, dt: Optional[datetime] = None) -> str:
    issued_at = dt or datetime.utcnow()
    yyyymmdd = issued_at.strftime("%Y%m%d")
    suffix = uuid4().hex[:8].upper()
    return f"PKT-{region.upper()}-{yyyymmdd}-{suffix}"
