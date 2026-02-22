from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import json, os, base64
from tools.verify_lib import verify_receipt_obj, VerifyConfig

app = FastAPI(title="SVS Gateway Demo")

CFG = VerifyConfig(time_window_seconds=300, replay_db_path="conformance/state/seen_nonces.json")

STATE = {
  "protected_requests": 0,
  "receipts_verified": 0,
  "allowed": 0,
  "denied": 0,
  "degraded": 0,
}

class ExecReq(BaseModel):
  action: str
  mode: str = "commit"  # commit/preview
  payload: dict = {}
  receipt: dict | None = None  # optional body receipt

def _parse_receipt(
  x_svs_receipt_b64: str | None,
  x_svs_receipt: str | None,
  body_receipt: dict | None
):
  if body_receipt is not None:
    return body_receipt

  if x_svs_receipt_b64:
    try:
      raw = base64.b64decode(x_svs_receipt_b64.encode("ascii"))
      return json.loads(raw.decode("utf-8"))
    except Exception:
      raise HTTPException(status_code=403, detail={"reason_code":"RECEIPT_B64_PARSE_ERROR"})

  if x_svs_receipt:
    try:
      return json.loads(x_svs_receipt)
    except Exception:
      raise HTTPException(status_code=403, detail={"reason_code":"RECEIPT_PARSE_ERROR"})

  raise HTTPException(status_code=403, detail={"reason_code":"MISSING_RECEIPT"})

def _require_and_verify(req: ExecReq, x_svs_receipt_b64: str | None, x_svs_receipt: str | None):
  r = _parse_receipt(x_svs_receipt_b64, x_svs_receipt, req.receipt)
  ok, code = verify_receipt_obj(r, CFG)
  if not ok:
    raise HTTPException(status_code=403, detail={"reason_code":code})
  STATE["receipts_verified"] += 1
  return r

def _enforce_decision(r: dict, req: ExecReq):
  decision = (r.get("decision") or {})
  effect = decision.get("effect")
  constraints = decision.get("constraints") or {}

  if effect == "DENY":
    STATE["denied"] += 1
    raise HTTPException(status_code=403, detail={"reason_code": decision.get("reason_code","DENY")})

  if effect == "DEGRADE":
    STATE["degraded"] += 1
    # preview-only in demo
    if req.mode != "preview":
      raise HTTPException(status_code=403, detail={"reason_code":"DEGRADE_PREVIEW_ONLY"})
    if constraints.get("requires_human_confirm", False):
      return {"status":"DEGRADED_PREVIEW", "requires_human_confirm": True}
    return {"status":"DEGRADED_PREVIEW"}

  if effect == "ALLOW":
    STATE["allowed"] += 1
    if constraints.get("read_only", False) and req.mode != "preview":
      raise HTTPException(status_code=403, detail={"reason_code":"READ_ONLY"})
    return {"status":"ALLOWED"}

  raise HTTPException(status_code=403, detail={"reason_code":"UNKNOWN_EFFECT"})

@app.post("/execute")
def execute(
  req: ExecReq,
  x_svs_receipt_b64: str | None = Header(default=None),
  x_svs_receipt: str | None = Header(default=None),
):
  STATE["protected_requests"] += 1
  r = _require_and_verify(req, x_svs_receipt_b64, x_svs_receipt)
  result = _enforce_decision(r, req)
  return {"ok": True, "result": result, "action": req.action, "mode": req.mode}

@app.post("/bypass")
def bypass(
  req: ExecReq,
  x_svs_receipt_b64: str | None = Header(default=None),
  x_svs_receipt: str | None = Header(default=None),
):
  STATE["protected_requests"] += 1
  r = _require_and_verify(req, x_svs_receipt_b64, x_svs_receipt)
  result = _enforce_decision(r, req)
  return {"ok": True, "result": result, "bypass": True}

@app.get("/metrics")
def metrics():
  return STATE

@app.post("/reset")
def reset():
  for k in list(STATE.keys()):
    STATE[k] = 0
  try:
    os.remove("conformance/state/seen_nonces.json")
  except FileNotFoundError:
    pass
  return {"ok": True}
