from fastapi import FastAPI

from ledgerly import models
from ledgerly.routes.auth import router as auth_router
from ledgerly.routes.invoices import router as invoices_router


models.seed(models.store)

app = FastAPI(title="ledgerly")
app.include_router(auth_router)
app.include_router(invoices_router)


@app.get("/healthz")
def healthcheck():
    return {"ok": True}
