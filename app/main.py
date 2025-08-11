from fastapi import FastAPI
from routers import contracts

app = FastAPI(title="Contract & Tax AI")
app.include_router(contracts.router, prefix="/contracts", tags=["contracts"])

@app.get("/")
def root():
    return {"ok": True}
