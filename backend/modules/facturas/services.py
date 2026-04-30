from fastapi import HTTPException

from modules.facturas.schemas import InvoiceCreate, InvoiceListItem, InvoiceResponse
from modules.shared.schemas import InvoiceStatus, TrackingStatus
from modules.shared.services import generate_id, invoices
from modules.tracking.services import add_tracking
from modules.validation.schemas import ValidateInvoiceRequest
from modules.validation.services import validate_invoice_data


def create_invoice_service(payload: InvoiceCreate) -> InvoiceResponse:
    exists = any(
        invoice["ruc_emisor"] == payload.ruc_emisor
        and invoice["serie"] == payload.serie
        and invoice["correlativo"] == payload.correlativo
        for invoice in invoices.values()
    )
    if exists:
        raise HTTPException(status_code=400, detail="La factura ya existe para ese emisor, serie y correlativo")

    invoice_id = generate_id("inv")
    invoice = {
        "invoice_id": invoice_id,
        "seller_id": payload.seller_id,
        "ruc_emisor": payload.ruc_emisor,
        "ruc_pagador": payload.ruc_pagador,
        "serie": payload.serie,
        "correlativo": payload.correlativo,
        "monto": payload.monto,
        "monto_disponible": payload.monto,
        "fecha_emision": payload.fecha_emision,
        "fecha_vencimiento": payload.fecha_vencimiento,
        "tasa_interes": payload.tasa_interes,
        "status": InvoiceStatus.VALIDATING,
        "rejection_reason": None,
    }
    invoices[invoice_id] = invoice
    add_tracking(invoice_id, TrackingStatus.INVOICE_UPLOADED, "Factura subida al sistema.")

    validation = validate_invoice_data(
        ValidateInvoiceRequest(
            ruc_emisor=payload.ruc_emisor,
            ruc_pagador=payload.ruc_pagador,
            serie=payload.serie,
            correlativo=payload.correlativo,
            monto=payload.monto,
        )
    )

    if validation.is_valid:
        invoice["status"] = InvoiceStatus.PUBLISHED
        add_tracking(invoice_id, TrackingStatus.SUNAT_VALIDATED, "Factura validada por SUNAT mock.")
        add_tracking(invoice_id, TrackingStatus.INVOICE_PUBLISHED, "Factura publicada en marketplace.")
        return InvoiceResponse(
            invoice_id=invoice_id,
            status=InvoiceStatus.PUBLISHED,
            message="Factura validada y publicada",
            rejection_reason=None,
        )

    invoice["status"] = InvoiceStatus.REJECTED
    invoice["rejection_reason"] = validation.rejection_reason
    return InvoiceResponse(
        invoice_id=invoice_id,
        status=InvoiceStatus.REJECTED,
        message="Factura rechazada",
        rejection_reason=validation.rejection_reason,
    )


def list_invoices_service() -> list[InvoiceListItem]:
    return [
        InvoiceListItem(
            invoice_id=invoice["invoice_id"],
            seller_id=invoice["seller_id"],
            monto=invoice["monto"],
            monto_disponible=invoice["monto_disponible"],
            tasa_interes=invoice["tasa_interes"],
            status=invoice["status"],
        )
        for invoice in invoices.values()
    ]
