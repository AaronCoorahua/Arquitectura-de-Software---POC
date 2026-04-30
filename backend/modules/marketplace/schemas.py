from decimal import Decimal

from pydantic import BaseModel, Field

from modules.shared.schemas import PurchaseStatus, TrackingStatus


class PurchaseCreate(BaseModel):
    investor_id: str = "investor_mock_001"
    amount: Decimal = Field(gt=0)
    payment_method: str
    use_wallet_balance: bool = False
    insurance_opt_in: bool = False


class PurchaseResponse(BaseModel):
    purchase_id: str
    invoice_id: str
    status: PurchaseStatus
    owned_fraction: Decimal
    expected_return: Decimal
    tracking_status: TrackingStatus
