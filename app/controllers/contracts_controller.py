import re
from typing import Dict, List, Optional, Any

# ---- in-memory store ----
_CONTRACTS: Dict[str, str] = {}

# simple clause regexes (add more later)
PATTERNS = {
    "WithholdingTax": re.compile(r"\b(withholding\s+tax|tax\s+withheld|WHT)\b", re.IGNORECASE),
    "GrossUp":        re.compile(r"\bgross-?up\b", re.IGNORECASE),
    "VAT":            re.compile(r"\b(VAT|value[-\s]?added\s+tax|sales\s+tax)\b", re.IGNORECASE),
    "GoverningLaw":   re.compile(r"\bgoverning\s+law\b", re.IGNORECASE),
}

def _extract_clauses(text: str) -> List[Dict[str, Any]]:
    clauses = []
    for name, rx in PATTERNS.items():
        for m in rx.finditer(text):
            start, end = m.span()
            snippet = text[max(0, start-80): min(len(text), end+120)]
            clauses.append({
                "name": name,
                "match": m.group(0),
                "span": [start, end],
                "snippet": snippet.strip()
            })
    return clauses

# -------- public API used by router --------
def index_contract(cid: str, text: str) -> None:
    _CONTRACTS[cid] = text

def get_clauses(cid: str) -> Optional[Dict[str, Any]]:
    text = _CONTRACTS.get(cid)
    if text is None:
        return None
    return {"contractId": cid, "clauses": _extract_clauses(text)}

def evaluate_contract(cid: str) -> Optional[Dict[str, Any]]:
    text = _CONTRACTS.get(cid)
    if text is None:
        return None
    clauses = _extract_clauses(text)
    has_wht  = any(c["name"] == "WithholdingTax" for c in clauses)
    has_gup  = any(c["name"] == "GrossUp"        for c in clauses)
    has_vat  = any(c["name"] == "VAT"            for c in clauses)

    issues = []

    # Rule 1: If WHT present but no Gross-Up -> high risk
    if has_wht and not has_gup:
        issues.append({
            "id": "gross-up-required",
            "severity": "high",
            "explanation": "Withholding tax mentioned but no gross-up protection found.",
            "suggestion": "Add a gross-up clause ensuring payer bears WHT."
        })

    # Rule 2: If VAT mentioned, suggest invoice wording/reverse charge check
    if has_vat and re.search(r"reverse\s+charge", text, re.IGNORECASE) is None:
        issues.append({
            "id": "vat-wording",
            "severity": "medium",
            "explanation": "VAT mentioned without 'reverse charge' wording.",
            "suggestion": "Add VAT wording (e.g., reverse charge where applicable)."
        })

    return {
        "contractId": cid,
        "summary": {"withholdingTax": has_wht, "grossUp": has_gup, "vat": has_vat},
        "clauses": clauses,
        "issues": issues
    }
