from datetime import datetime
from uuid import uuid4


invoices: dict[str, dict] = {}
purchases: dict[str, dict] = {}
tracking_events: list[dict] = []
supported_payment_methods = {"yape", "plin", "tarjeta", "transferencia", "wallet"}


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def utc_now() -> datetime:
    return datetime.utcnow()
