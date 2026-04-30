from datetime import datetime

from pydantic import BaseModel

from modules.shared.schemas import TrackingStatus


class TrackingResponse(BaseModel):
    event_id: str
    invoice_id: str
    status: TrackingStatus
    message: str
    created_at: datetime
