from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException

from database import get_connection
from modules.marketplace.schemas import PurchaseCreate, PurchaseResponse
from modules.shared.schemas import InvoiceStatus, PurchaseStatus, TrackingStatus
from modules.shared.services import generate_id, supported_payment_methods
from modules.tracking.services import add_tracking


TWOPLACES = Decimal("0.01")
FOURPLACES = Decimal("0.0001")


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _mock_payment_gateway(payload: PurchaseCreate, investor_balance: Decimal) -> None:
    if payload.payment_method == "transferencia" and payload.amount >= Decimal("4500"):
        raise HTTPException(status_code=503, detail="Payment service unavailable")

    if payload.payment_method == "tarjeta" and payload.amount > Decimal("3000"):
        raise HTTPException(status_code=402, detail="Pago rechazado por la pasarela mock")

    if investor_balance < payload.amount:
        raise HTTPException(status_code=400, detail="Fondos insuficientes para completar la compra")


def buy_invoice_service(invoice_id: str, payload: PurchaseCreate) -> PurchaseResponse:
    if payload.payment_method not in supported_payment_methods:
        raise HTTPException(status_code=400, detail="Metodo de pago no soportado por el POC")

    with get_connection() as connection:
        invoice = connection.execute(
            """
            SELECT invoice_id, monto, monto_disponible, tasa_interes, status
            FROM invoices
            WHERE invoice_id = ?
            """,
            (invoice_id,),
        ).fetchone()

        if invoice is None:
            raise HTTPException(status_code=404, detail="La factura no existe")

        invoice_status = InvoiceStatus(invoice["status"])
        if invoice_status not in {InvoiceStatus.PUBLISHED, InvoiceStatus.PARTIALLY_FUNDED}:
            raise HTTPException(status_code=400, detail="La factura no esta disponible para compra")

        amount = _quantize_money(payload.amount)
        monto_disponible = Decimal(invoice["monto_disponible"])
        monto_total = Decimal(invoice["monto"])
        tasa_interes = Decimal(invoice["tasa_interes"])

        if amount > monto_disponible:
            raise HTTPException(status_code=400, detail="El monto supera el saldo disponible de la factura")

        investor = connection.execute(
            """
            SELECT investor_id, balance
            FROM investors
            WHERE investor_id = ?
            """,
            (payload.investor_id,),
        ).fetchone()

        if investor is None:
            raise HTTPException(status_code=404, detail="El inversionista no existe en el POC")

        investor_balance = Decimal(investor["balance"])
        _mock_payment_gateway(payload, investor_balance)

        new_balance = _quantize_money(investor_balance - amount)
        new_available = _quantize_money(monto_disponible - amount)
        new_status = InvoiceStatus.FUNDED if new_available == Decimal("0.00") else InvoiceStatus.PARTIALLY_FUNDED
        purchase_id = generate_id("pur")
        owned_fraction = (amount / monto_total).quantize(FOURPLACES, rounding=ROUND_HALF_UP)
        expected_return = _quantize_money(amount * (Decimal("1") + tasa_interes))

        connection.execute(
            "UPDATE investors SET balance = ? WHERE investor_id = ?",
            (str(new_balance), payload.investor_id),
        )
        connection.execute(
            "UPDATE invoices SET monto_disponible = ?, status = ? WHERE invoice_id = ?",
            (str(new_available), new_status.value, invoice_id),
        )
        connection.execute(
            """
            INSERT INTO purchases(
                purchase_id, invoice_id, investor_id, amount, payment_method,
                status, owned_fraction, expected_return, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                purchase_id,
                invoice_id,
                payload.investor_id,
                str(amount),
                payload.payment_method,
                PurchaseStatus.CONFIRMED.value,
                str(owned_fraction),
                str(expected_return),
            ),
        )

    add_tracking(invoice_id, TrackingStatus.PURCHASE_REGISTERED, "Compra registrada exitosamente.")
    return PurchaseResponse(
        purchase_id=purchase_id,
        invoice_id=invoice_id,
        status=PurchaseStatus.CONFIRMED,
        owned_fraction=owned_fraction,
        expected_return=expected_return,
        tracking_status=TrackingStatus.PURCHASE_REGISTERED,
    )
