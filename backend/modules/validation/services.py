from fastapi import HTTPException

from modules.validation.schemas import ValidateInvoiceRequest, ValidateInvoiceResponse


def validate_invoice_data(payload: ValidateInvoiceRequest) -> ValidateInvoiceResponse:
    # TODO: implementar simulacion/mock de SUNAT.
    # Ideas sugeridas por el README:
    # - devolver aceptado o rechazado
    # - incluir source = "sunat_mock"
    # - devolver observations y rejection_reason
    # - cubrir al menos un caso exitoso y uno fallido
    raise HTTPException(
        status_code=501,
        detail="TODO: implementar simulacion de SUNAT para el POC",
    )
