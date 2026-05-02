from datetime import datetime

from database import get_connection
from modules.shared.schemas import TrackingStatus
from modules.shared.services import generate_id, utc_now
from modules.tracking.schemas import TrackingResponse


def add_tracking(invoice_id: str, status: TrackingStatus, message: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO tracking_events(event_id, invoice_id, status, message, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (generate_id("trk"), invoice_id, status.value, message, utc_now().isoformat()),
        )


def get_tracking_by_invoice(invoice_id: str) -> list[TrackingResponse]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT event_id, invoice_id, status, message, created_at
            FROM tracking_events
            WHERE invoice_id = ?
            ORDER BY created_at ASC
            """,
            (invoice_id,),
        ).fetchall()

    return [
        TrackingResponse(
            event_id=row["event_id"],
            invoice_id=row["invoice_id"],
            status=TrackingStatus(row["status"]),
            message=row["message"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]
