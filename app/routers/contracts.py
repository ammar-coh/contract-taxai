from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from controllers.contracts_controller import (
    index_contract, get_clauses, evaluate_contract
)

router = APIRouter()

class IndexBody(BaseModel):
    id: str
    text: str

@router.post("")
def index(body: IndexBody):
    index_contract(body.id, body.text)
    return {"indexed": body.id}

@router.get("/{cid}/clauses")
def clauses(cid: str):
    text = get_clauses(cid)
    if text is None:
        raise HTTPException(404, "contract not found")
    return text

@router.post("/{cid}/evaluate")
def evaluate(cid: str):
    result = evaluate_contract(cid)
    if result is None:
        raise HTTPException(404, "contract not found")
    return result
@router.get("")
def info():
    return {"ok": True, "use": ["POST /contracts", "GET /contracts/{cid}/clauses", "POST /contracts/{cid}/evaluate"]}

