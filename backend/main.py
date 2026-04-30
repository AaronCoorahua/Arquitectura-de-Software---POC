from fastapi import FastAPI

from modules.facturas.routes import router as facturas_router
from modules.marketplace.routes import router as marketplace_router
from modules.shared.routes import router as shared_router
from modules.tracking.routes import router as tracking_router
from modules.validation.routes import router as validation_router


app = FastAPI(
    title="Factoring POC API",
    version="0.1.0",
    description="POC simple y funcional para factoring.",
)

app.include_router(shared_router)
app.include_router(validation_router)
app.include_router(facturas_router)
app.include_router(marketplace_router)
app.include_router(tracking_router)
