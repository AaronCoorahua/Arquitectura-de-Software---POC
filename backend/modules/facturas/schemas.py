from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from modules.shared.schemas import InvoiceStatus


class InvoiceCreate(BaseModel):
    seller_id: str = "seller_mock_001"
    ruc_emisor: str = Field(min_length=11, max_length=11)
    ruc_pagador: str = Field(min_length=11, max_length=11)
    serie: str
    correlativo: str
    monto: Decimal = Field(gt=0)
    fecha_emision: date
    fecha_vencimiento: date
    tasa_interes: Decimal = Field(gt=0)
    archivo_xml: str

    @model_validator(mode="after")
    def validate_dates(self) -> "InvoiceCreate":
        if self.fecha_vencimiento <= self.fecha_emision:
            raise ValueError("fecha_vencimiento debe ser posterior a fecha_emision")
        return self


class InvoiceResponse(BaseModel):
    invoice_id: str
    status: InvoiceStatus
    message: str
    rejection_reason: str | None = None


class InvoiceListItem(BaseModel):
    invoice_id: str
    seller_id: str
    ruc_emisor: str
    ruc_pagador: str
    serie: str
    correlativo: str
    monto: Decimal
    monto_disponible: Decimal
    tasa_interes: Decimal
    status: InvoiceStatus
