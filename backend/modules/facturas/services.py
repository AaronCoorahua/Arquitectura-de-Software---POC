from decimal import Decimal
import sqlite3

from fastapi import HTTPException

from database import get_connection
from modules.facturas.schemas import InvoiceCreate, InvoiceListItem, InvoiceResponse
from modules.shared.schemas import InvoiceStatus, TrackingStatus
from modules.shared.services import generate_id, utc_now
from modules.tracking.services import add_tracking
from modules.validation.schemas import ValidateInvoiceRequest
from modules.validation.services import validate_invoice_data


MAX_BUSINESS_RATE = Decimal("0.35")


def _business_validate_invoice(payload: InvoiceCreate) -> str | None:
    max_days = 120
    due_days = (payload.fecha_vencimiento - payload.fecha_emision).days

    if payload.tasa_interes > MAX_BUSINESS_RATE:
        return "La tasa de interes excede el limite permitido para el POC"
    if due_days > max_days:
        return "La fecha de vencimiento excede el horizonte permitido para el POC"
    return None


def create_invoice_service(payload: InvoiceCreate) -> InvoiceResponse:
    invoice_id = generate_id("inv")
    created_at = utc_now().isoformat()

    with get_connection() as connection:
        try:
            connection.execute(
                """
                INSERT INTO invoices(
                    invoice_id, seller_id, ruc_emisor, ruc_pagador, serie, correlativo,
                    monto, monto_disponible, fecha_emision, fecha_vencimiento,
                    tasa_interes, status, rejection_reason, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice_id,
                    payload.seller_id,
                    payload.ruc_emisor,
                    payload.ruc_pagador,
                    payload.serie,
                    payload.correlativo,
                    str(payload.monto),
                    str(payload.monto),
                    payload.fecha_emision.isoformat(),
                    payload.fecha_vencimiento.isoformat(),
                    str(payload.tasa_interes),
                    InvoiceStatus.VALIDATING.value,
                    None,
                    created_at,
                ),
            )
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=400,
                detail="La factura ya existe para ese emisor, serie y correlativo",
            ) from error

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

    if not validation.is_valid:
        with get_connection() as connection:
            connection.execute(
                "UPDATE invoices SET status = ?, rejection_reason = ? WHERE invoice_id = ?",
                (InvoiceStatus.REJECTED.value, validation.rejection_reason, invoice_id),
            )
        return InvoiceResponse(
            invoice_id=invoice_id,
            status=InvoiceStatus.REJECTED,
            message="Factura rechazada",
            rejection_reason=validation.rejection_reason,
        )

    add_tracking(invoice_id, TrackingStatus.SUNAT_VALIDATED, "Factura validada por SUNAT mock.")

    business_rejection = _business_validate_invoice(payload)
    if business_rejection is not None:
        with get_connection() as connection:
            connection.execute(
                "UPDATE invoices SET status = ?, rejection_reason = ? WHERE invoice_id = ?",
                (InvoiceStatus.REJECTED.value, business_rejection, invoice_id),
            )
        return InvoiceResponse(
            invoice_id=invoice_id,
            status=InvoiceStatus.REJECTED,
            message="Factura rechazada",
            rejection_reason=business_rejection,
        )

    with get_connection() as connection:
        connection.execute(
            "UPDATE invoices SET status = ?, rejection_reason = NULL WHERE invoice_id = ?",
            (InvoiceStatus.PUBLISHED.value, invoice_id),
        )

    add_tracking(invoice_id, TrackingStatus.INVOICE_PUBLISHED, "Factura publicada en marketplace.")
    return InvoiceResponse(
        invoice_id=invoice_id,
        status=InvoiceStatus.PUBLISHED,
        message="Factura validada y publicada",
        rejection_reason=None,
    )


def list_invoices_service() -> list[InvoiceListItem]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT invoice_id, seller_id, ruc_emisor, ruc_pagador, serie, correlativo,
                   monto, monto_disponible, tasa_interes, status
            FROM invoices
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [
        InvoiceListItem(
            invoice_id=row["invoice_id"],
            seller_id=row["seller_id"],
            ruc_emisor=row["ruc_emisor"],
            ruc_pagador=row["ruc_pagador"],
            serie=row["serie"],
            correlativo=row["correlativo"],
            monto=Decimal(row["monto"]),
            monto_disponible=Decimal(row["monto_disponible"]),
            tasa_interes=Decimal(row["tasa_interes"]),
            status=InvoiceStatus(row["status"]),
        )
        for row in rows
    ]
