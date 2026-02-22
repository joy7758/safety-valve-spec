from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import json
import os
from tools.verify_lib import VerifyConfig, verify_receipt_obj

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


def _require_receipt(x_svs_receipt: str | None):
  if not x_svs_receipt:
    raise HTTPException(status_code=403, detail={"reason_code": "MISSING_RECEIPT"})
  try:
    r = json.loads(x_svs_receipt)
  except Exception:
    raise HTTPException(status_code=403, detail={"reason_code": "RECEIPT_PARSE_ERROR"})

  ok, code = verify_receipt_obj(r, CFG)
  if not ok:
    raise HTTPException(status_code=403, detail={"reason_code": code})

  STATE["receipts_verified"] += 1
  return r


def _enforce_decision(r: dict, req: ExecReq):
  decision = r.get("decision") or {}
  effect = decision.get("effect")
  constraints = decision.get("constraints") or {}

  if effect == "DENY":
    STATE["denied"] += 1
    raise HTTPException(status_code=403, detail={"reason_code": decision.get("reason_code", "DENY")})

  if effect == "DEGRADE":
    # enforce degrade constraints: preview-only or require human confirm
    STATE["degraded"] += 1
    if req.mode != "preview":
      raise HTTPException(status_code=403, detail={"reason_code": "DEGRADE_PREVIEW_ONLY"})
    if constraints.get("requires_human_confirm", False):
      return {"status": "DEGRADED_PREVIEW", "requires_human_confirm": True}
    return {"status": "DEGRADED_PREVIEW"}

  if effect == "ALLOW":
    STATE["allowed"] += 1
    if constraints.get("read_only", False) and req.mode != "preview":
      raise HTTPException(status_code=403, detail={"reason_code": "READ_ONLY"})
    return {"status": "ALLOWED"}

  raise HTTPException(status_code=403, detail={"reason_code": "UNKNOWN_EFFECT"})


@app.post("/execute")
def execute(req: ExecReq, x_svs_receipt: str | None = Header(default=None)):
  STATE["protected_requests"] += 1
  r = _require_receipt(x_svs_receipt)
  result = _enforce_decision(r, req)
  return {"ok": True, "result": result, "action": req.action, "mode": req.mode}


@app.post("/bypass")
def bypass(req: ExecReq, x_svs_receipt: str | None = Header(default=None)):
  # Simulated bypass path; still must enforce receipt.
  STATE["protected_requests"] += 1
  r = _require_receipt(x_svs_receipt)
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
