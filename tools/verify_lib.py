import copy
import json
import os
from dataclasses import dataclass

try:
  from tools.schema_check import check_reason_code
except ModuleNotFoundError:
  from schema_check import check_reason_code
try:
  from tools.crl_verify import verify_crl
except ModuleNotFoundError:
  from crl_verify import verify_crl

try:
  from tools.svs_crypto import b64d, canonical_json, parse_rfc3339, utcnow, verify_ed25519
except ModuleNotFoundError:
  from svs_crypto import b64d, canonical_json, parse_rfc3339, utcnow, verify_ed25519

REPLAY_DB = "conformance/state/seen_nonces.json"


@dataclass
class VerifyConfig:
  crl_path: str | None = None
  time_window_seconds: int = 300
  replay_db_path: str = REPLAY_DB


def _load_seen(path: str):
  if not os.path.exists(path):
    return {"nonces": {}}
  return json.load(open(path, "r", encoding="utf-8"))


def _save_seen(path: str, db):
  os.makedirs(os.path.dirname(path), exist_ok=True)
  json.dump(db, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


def verify_receipt_obj(r: dict, cfg: VerifyConfig | None = None):
  """
  Returns: (ok: bool, code: str)
  codes: PASS, <FAIL_CODE>
  """
  if cfg is None:
    cfg = VerifyConfig()

  sig = r.get("signature") or {}
  if sig.get("alg") != "Ed25519":
    return False, "SVS_SIG_UNSUPPORTED_ALG"

  cert = sig.get("cert")
  if not cert:
    return False, "SVS_CERT_MISSING_CERT"

  # Load Root PK/KID
  try:
    root_pk = b64d(open("keys/root_ca.pk.b64", "r", encoding="utf-8").read().strip())
    root_kid = open("keys/root_ca.kid", "r", encoding="utf-8").read().strip()
  except Exception:
    return False, "SVS_CERT_WRONG_ISSUER"

  # Cert issuer check
  if cert.get("issuer_kid") != root_kid:
    return False, "SVS_CERT_WRONG_ISSUER"

  # Cert signature verify
  cert_payload = dict(cert)
  cert_sig_b64 = cert_payload.pop("sig_b64", None)
  if not cert_sig_b64:
    return False, "SVS_CERT_INVALID_SIGNATURE"
  if not verify_ed25519(root_pk, canonical_json(cert_payload), b64d(cert_sig_b64)):
    return False, "SVS_CERT_INVALID_SIGNATURE"

  # Cert validity
  try:
    now = utcnow()
    ia = parse_rfc3339(cert.get("issued_at"))
    ea = parse_rfc3339(cert.get("expires_at"))
  except Exception:
    return False, "SVS_CERT_EXPIRED"
  if not (ia <= now <= ea):
    return False, "SVS_CERT_EXPIRED"

  # CRL revocation (if present)
  if cfg.crl_path:
    try:
      import json as _json
      import os as _os
      if _os.path.exists(cfg.crl_path):
        crl = _json.load(open(cfg.crl_path, "r", encoding="utf-8"))
        ok, code = verify_crl(crl)
        if not ok:
          return False, code
        subject_kid = sig.get("kid")
        for e in crl.get("entries", []):
          if e.get("subject_kid") == subject_kid:
            return False, "SVS_CERT_REVOKED"
    except Exception:
      # If CRL is malformed/unreadable, treat as trust failure
      return False, "SVS_CERT_INVALID_SIGNATURE"

  # Receipt time window
  try:
    issued_at = parse_rfc3339(r.get("issued_at"))
  except Exception:
    return False, "SVS_TIME_RECEIPT_TIME_PARSE_ERROR"
  delta = abs((now - issued_at).total_seconds())
  if delta > cfg.time_window_seconds:
    return False, "SVS_TIME_EXPIRED_RECEIPT"

  # Replay protection (receipt_id + nonce)
  nonce = r.get("nonce", "")
  rid = r.get("receipt_id", "")
  key = f"{rid}:{nonce}"
  db = _load_seen(cfg.replay_db_path)
  if key in db["nonces"]:
    return False, "SVS_REPLAY_DETECTED"
  db["nonces"][key] = r.get("issued_at")
  _save_seen(cfg.replay_db_path, db)

  # Receipt signature verify with subject public key
  subject_pk_b64 = cert.get("subject_public_key_b64")
  if not subject_pk_b64:
    return False, "SVS_CERT_MISSING_SUBJECT_PK"
  subject_pk = b64d(subject_pk_b64)

  payload = copy.deepcopy(r)
  payload.pop("signature", None)

  receipt_sig = sig.get("sig")
  if not receipt_sig:
    return False, "SVS_SIG_MISSING_RECEIPT_SIG"
  if not verify_ed25519(subject_pk, canonical_json(payload), b64d(receipt_sig)):
    return False, "SVS_SIG_INVALID_SIGNATURE"

  # Enforce reason_code enum from schema.
  ok, code = check_reason_code(r)
  if not ok:
    return False, code

  return True, "PASS"
