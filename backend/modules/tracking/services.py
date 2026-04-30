from modules.shared.schemas import TrackingStatus
from modules.shared.services import generate_id, tracking_events, utc_now
from modules.tracking.schemas import TrackingResponse


def add_tracking(invoice_id: str, status: TrackingStatus, message: str) -> None:
    tracking_events.append(
        {
            "event_id": generate_id("trk"),
            "invoice_id": invoice_id,
            "status": status,
            "message": message,
            "created_at": utc_now(),
        }
    )


def get_tracking_by_invoice(invoice_id: str) -> list[TrackingResponse]:
    return [
        TrackingResponse(
            event_id=event["event_id"],
            invoice_id=event["invoice_id"],
            status=event["status"],
            message=event["message"],
            created_at=event["created_at"],
        )
        for event in tracking_events
        if event["invoice_id"] == invoice_id
    ]
