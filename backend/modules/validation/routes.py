from fastapi import APIRouter

from modules.validation.schemas import ValidateInvoiceRequest, ValidateInvoiceResponse
from modules.validation.services import validate_invoice_data


router = APIRouter()


@router.post("/validate_invoice", response_model=ValidateInvoiceResponse)
def validate_invoice(payload: ValidateInvoiceRequest) -> ValidateInvoiceResponse:
    return validate_invoice_data(payload)
