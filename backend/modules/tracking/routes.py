from fastapi import APIRouter

from modules.tracking.schemas import TrackingResponse
from modules.tracking.services import get_tracking_by_invoice


router = APIRouter()


@router.get("/facturas/{invoice_id}/tracking", response_model=list[TrackingResponse])
def get_tracking(invoice_id: str) -> list[TrackingResponse]:
    return get_tracking_by_invoice(invoice_id)
