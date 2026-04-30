from modules.validation.schemas import ValidateInvoiceRequest, ValidateInvoiceResponse


def validate_invoice_data(payload: ValidateInvoiceRequest) -> ValidateInvoiceResponse:
    if payload.correlativo.endswith("99"):
        return ValidateInvoiceResponse(
            is_valid=False,
            source="sunat_mock",
            observations=["SUNAT mock marco la factura como observada."],
            rejection_reason="SUNAT validation failed",
        )

    return ValidateInvoiceResponse(
        is_valid=True,
        source="sunat_mock",
        observations=["Factura validada por la fuente mock."],
        rejection_reason=None,
    )
