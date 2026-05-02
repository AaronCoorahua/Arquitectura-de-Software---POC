from fastapi import APIRouter

from modules.shared.schemas import InvestorBalanceResponse
from modules.shared.services import get_investor_balance_service


router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "factoring-poc"}


@router.get("/investors/{investor_id}", response_model=InvestorBalanceResponse)
def get_investor_balance(investor_id: str) -> InvestorBalanceResponse:
    return get_investor_balance_service(investor_id)
