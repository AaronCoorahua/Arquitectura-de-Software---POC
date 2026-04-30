from fastapi import HTTPException

from modules.marketplace.schemas import PurchaseCreate, PurchaseResponse
from modules.shared.schemas import InvoiceStatus
from modules.shared.services import invoices, supported_payment_methods


def buy_invoice_service(invoice_id: str, payload: PurchaseCreate) -> PurchaseResponse:
    invoice = invoices.get(invoice_id)

    if invoice is None:
        raise HTTPException(status_code=404, detail="La factura no existe")

    if invoice["status"] not in {InvoiceStatus.PUBLISHED, InvoiceStatus.PARTIALLY_FUNDED}:
        raise HTTPException(status_code=400, detail="La factura no esta disponible para compra")

    # TODO: implementar validacion/mock de pasarela de pagos o banco.
    # Por ahora solo se deja la lista base de metodos sugeridos por el README.
    if payload.payment_method not in supported_payment_methods:
        raise HTTPException(status_code=400, detail="Metodo de pago no soportado por el POC")

    raise HTTPException(
        status_code=501,
        detail="TODO: implementar simulacion de pasarela/banco para compras del POC",
    )
