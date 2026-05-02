from fastapi import HTTPException

from modules.validation.schemas import ValidateInvoiceRequest, ValidateInvoiceResponse


def validate_invoice_data(payload: ValidateInvoiceRequest) -> ValidateInvoiceResponse:
    observations: list[str] = []

    if payload.serie.upper().startswith("ERR"):
        raise HTTPException(status_code=503, detail="SUNAT service unavailable")

    if payload.ruc_emisor == payload.ruc_pagador:
        return ValidateInvoiceResponse(
            is_valid=False,
            source="sunat_mock",
            observations=["El emisor y el pagador no pueden ser el mismo RUC."],
            rejection_reason="SUNAT validation failed",
        )

    if payload.correlativo.endswith("999") or payload.ruc_emisor.endswith("00"):
        observations.append("SUNAT mock marco la factura como observada.")
        return ValidateInvoiceResponse(
            is_valid=False,
            source="sunat_mock",
            observations=observations,
            rejection_reason="SUNAT validation failed",
        )

    if payload.monto >= 10000:
        observations.append("SUNAT mock aplico revision reforzada por monto alto.")

    observations.append("Factura validada correctamente por SUNAT mock.")
    return ValidateInvoiceResponse(
        is_valid=True,
        source="sunat_mock",
        observations=observations,
        rejection_reason=None,
    )
