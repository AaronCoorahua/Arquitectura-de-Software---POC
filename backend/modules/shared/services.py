from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException

from database import get_connection
from modules.shared.schemas import InvestorBalanceResponse


supported_payment_methods = {"yape", "plin", "tarjeta", "transferencia", "wallet"}


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def utc_now() -> datetime:
    return datetime.utcnow()


def get_investor_balance_service(investor_id: str) -> InvestorBalanceResponse:
    with get_connection() as connection:
        investor = connection.execute(
            """
            SELECT investor_id, name, balance
            FROM investors
            WHERE investor_id = ?
            """,
            (investor_id,),
        ).fetchone()

    if investor is None:
        raise HTTPException(status_code=404, detail="El inversionista no existe en el POC")

    return InvestorBalanceResponse(
        investor_id=investor["investor_id"],
        name=investor["name"],
        balance=Decimal(investor["balance"]),
    )
