from decimal import Decimal

from fastapi import HTTPException

from modules.marketplace.schemas import PurchaseCreate, PurchaseResponse
from modules.shared.schemas import InvoiceStatus, PurchaseStatus, TrackingStatus
from modules.shared.services import generate_id, invoices, purchases, supported_payment_methods
from modules.tracking.services import add_tracking


def buy_invoice_service(invoice_id: str, payload: PurchaseCreate) -> PurchaseResponse:
    invoice = invoices.get(invoice_id)

    if invoice is None:
        raise HTTPException(status_code=404, detail="La factura no existe")

    if invoice["status"] not in {InvoiceStatus.PUBLISHED, InvoiceStatus.PARTIALLY_FUNDED}:
        raise HTTPException(status_code=400, detail="La factura no esta disponible para compra")

    if payload.payment_method not in supported_payment_methods:
        raise HTTPException(status_code=400, detail="Metodo de pago no soportado por el POC")

    if payload.amount > invoice["monto_disponible"]:
        raise HTTPException(status_code=400, detail="El monto solicitado supera el saldo disponible de la factura")

    purchase_id = generate_id("pur")
    owned_fraction = (payload.amount / invoice["monto"]).quantize(Decimal("0.0001"))
    expected_return = (payload.amount * (Decimal("1") + invoice["tasa_interes"])).quantize(Decimal("0.01"))

    purchases[purchase_id] = {
        "purchase_id": purchase_id,
        "invoice_id": invoice_id,
        "investor_id": payload.investor_id,
        "amount": payload.amount,
        "payment_method": payload.payment_method,
        "owned_fraction": owned_fraction,
        "expected_return": expected_return,
        "status": PurchaseStatus.CONFIRMED,
    }

    invoice["monto_disponible"] = (invoice["monto_disponible"] - payload.amount).quantize(Decimal("0.01"))
    invoice["status"] = (
        InvoiceStatus.FUNDED if invoice["monto_disponible"] == Decimal("0.00") else InvoiceStatus.PARTIALLY_FUNDED
    )
    add_tracking(invoice_id, TrackingStatus.PURCHASE_REGISTERED, "Compra registrada correctamente.")

    return PurchaseResponse(
        purchase_id=purchase_id,
        invoice_id=invoice_id,
        status=PurchaseStatus.CONFIRMED,
        owned_fraction=owned_fraction,
        expected_return=expected_return,
        tracking_status=TrackingStatus.PURCHASE_REGISTERED,
    )
