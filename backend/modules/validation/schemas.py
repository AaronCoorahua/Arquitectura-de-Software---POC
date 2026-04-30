from decimal import Decimal

from pydantic import BaseModel, Field


class ValidateInvoiceRequest(BaseModel):
    ruc_emisor: str = Field(min_length=11, max_length=11)
    ruc_pagador: str = Field(min_length=11, max_length=11)
    serie: str
    correlativo: str
    monto: Decimal = Field(gt=0)


class ValidateInvoiceResponse(BaseModel):
    is_valid: bool
    source: str
    observations: list[str]
    rejection_reason: str | None = None
