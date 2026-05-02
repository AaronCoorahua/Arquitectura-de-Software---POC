import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "factoring_poc.sqlite3"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS investors (
                investor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                balance TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                seller_id TEXT NOT NULL,
                ruc_emisor TEXT NOT NULL,
                ruc_pagador TEXT NOT NULL,
                serie TEXT NOT NULL,
                correlativo TEXT NOT NULL,
                monto TEXT NOT NULL,
                monto_disponible TEXT NOT NULL,
                fecha_emision TEXT NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                tasa_interes TEXT NOT NULL,
                status TEXT NOT NULL,
                rejection_reason TEXT,
                created_at TEXT NOT NULL
            );

            CREATE UNIQUE INDEX IF NOT EXISTS ux_invoices_identity
            ON invoices(ruc_emisor, serie, correlativo);

            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id TEXT PRIMARY KEY,
                invoice_id TEXT NOT NULL,
                investor_id TEXT NOT NULL,
                amount TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT NOT NULL,
                owned_fraction TEXT NOT NULL,
                expected_return TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id),
                FOREIGN KEY(investor_id) REFERENCES investors(investor_id)
            );

            CREATE TABLE IF NOT EXISTS tracking_events (
                event_id TEXT PRIMARY KEY,
                invoice_id TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id)
            );
            """
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO investors(investor_id, name, balance)
            VALUES (?, ?, ?)
            """,
            ("investor_mock_001", "Diana M.", "5000.00"),
        )

        invoice_count = connection.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        if invoice_count == 0:
            connection.executemany(
                """
                INSERT INTO invoices(
                    invoice_id, seller_id, ruc_emisor, ruc_pagador, serie, correlativo,
                    monto, monto_disponible, fecha_emision, fecha_vencimiento,
                    tasa_interes, status, rejection_reason, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "inv_seed_001",
                        "seller_mock_001",
                        "20123456789",
                        "20987654321",
                        "F001",
                        "1001",
                        "10000.00",
                        "2000.00",
                        "2026-04-20",
                        "2026-06-20",
                        "0.12",
                        "published",
                        None,
                        "2026-04-20T10:00:00",
                    ),
                    (
                        "inv_seed_002",
                        "seller_mock_002",
                        "20444555666",
                        "20888777666",
                        "F002",
                        "2002",
                        "5000.00",
                        "5000.00",
                        "2026-04-22",
                        "2026-05-30",
                        "0.10",
                        "published",
                        None,
                        "2026-04-22T11:00:00",
                    ),
                ],
            )

            connection.executemany(
                """
                INSERT INTO tracking_events(event_id, invoice_id, status, message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    ("trk_seed_001", "inv_seed_001", "invoice_uploaded", "Factura seed cargada.", "2026-04-20T10:00:00"),
                    ("trk_seed_002", "inv_seed_001", "sunat_validated", "Factura seed validada por SUNAT mock.", "2026-04-20T10:00:03"),
                    ("trk_seed_003", "inv_seed_001", "invoice_published", "Factura seed publicada.", "2026-04-20T10:00:04"),
                    ("trk_seed_004", "inv_seed_002", "invoice_uploaded", "Factura seed cargada.", "2026-04-22T11:00:00"),
                    ("trk_seed_005", "inv_seed_002", "sunat_validated", "Factura seed validada por SUNAT mock.", "2026-04-22T11:00:03"),
                    ("trk_seed_006", "inv_seed_002", "invoice_published", "Factura seed publicada.", "2026-04-22T11:00:04"),
                ],
            )
