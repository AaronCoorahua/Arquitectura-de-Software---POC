from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    VALIDATING = "validating"
    REJECTED = "rejected"
    PUBLISHED = "published"
    PARTIALLY_FUNDED = "partially_funded"
    FUNDED = "funded"
    PAID = "paid"


class PurchaseStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class TrackingStatus(str, Enum):
    INVOICE_UPLOADED = "invoice_uploaded"
    SUNAT_VALIDATED = "sunat_validated"
    INVOICE_PUBLISHED = "invoice_published"
    PURCHASE_REGISTERED = "purchase_registered"
