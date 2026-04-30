from fastapi import APIRouter

from modules.marketplace.schemas import PurchaseCreate, PurchaseResponse
from modules.marketplace.services import buy_invoice_service


router = APIRouter()


@router.post("/facturas/{invoice_id}/comprar", response_model=PurchaseResponse)
def buy_invoice(invoice_id: str, payload: PurchaseCreate) -> PurchaseResponse:
    return buy_invoice_service(invoice_id, payload)
