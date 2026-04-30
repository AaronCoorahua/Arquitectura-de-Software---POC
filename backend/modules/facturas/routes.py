from fastapi import APIRouter, status

from modules.facturas.schemas import InvoiceCreate, InvoiceListItem, InvoiceResponse
from modules.facturas.services import create_invoice_service, list_invoices_service


router = APIRouter()


@router.post("/facturas", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate) -> InvoiceResponse:
    return create_invoice_service(payload)


@router.get("/facturas", response_model=list[InvoiceListItem])
def list_invoices() -> list[InvoiceListItem]:
    return list_invoices_service()
