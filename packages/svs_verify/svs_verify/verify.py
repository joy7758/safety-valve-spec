import time

from . import reason_codes as R
from .crypto import b64d, canonical_json, parse_rfc3339, verify_ed25519


def verify_crl(crl: dict, root_pk_raw: bytes, root_kid: str):
  if crl.get("issuer_kid") != root_kid:
    return False, R.FAIL_CERT_WRONG_ISSUER
  payload = dict(crl)
  sig_b64 = payload.pop("sig_b64", None)
  if not sig_b64:
    return False, R.FAIL_CERT_INVALID
  if not verify_ed25519(root_pk_raw, canonical_json(payload), b64d(sig_b64)):
    return False, R.FAIL_CERT_INVALID
  return True, R.PASS


def verify_receipt(
  receipt: dict,
  root_pk_raw: bytes,
  root_kid: str,
  time_window_seconds: int = 300,
  crl: dict | None = None,
  replay_db: dict | None = None,
):
  sig = receipt.get("signature") or {}
  if sig.get("alg") != "Ed25519":
    return False, R.FAIL_UNSUPPORTED_ALG

  cert = sig.get("cert")
  if not cert:
    return False, R.FAIL_MISSING_CERT

  if cert.get("issuer_kid") != root_kid:
    return False, R.FAIL_CERT_WRONG_ISSUER

  # verify cert signature
  cert_payload = dict(cert)
  cert_sig_b64 = cert_payload.pop("sig_b64", None)
  if not cert_sig_b64:
    return False, R.FAIL_CERT_INVALID
  if not verify_ed25519(root_pk_raw, canonical_json(cert_payload), b64d(cert_sig_b64)):
    return False, R.FAIL_CERT_INVALID

  # cert validity
  try:
    now = time.time()
    ia = parse_rfc3339(cert.get("issued_at")).timestamp()
    ea = parse_rfc3339(cert.get("expires_at")).timestamp()
  except Exception:
    return False, R.FAIL_CERT_EXPIRED
  if not (ia <= now <= ea):
    return False, R.FAIL_CERT_EXPIRED

  # optional CRL
  if crl is not None:
    ok, code = verify_crl(crl, root_pk_raw, root_kid)
    if not ok:
      return False, code
    subject_kid = sig.get("kid")
    for e in crl.get("entries", []):
      if e.get("subject_kid") == subject_kid:
        return False, R.FAIL_CERT_REVOKED

  # time window
  try:
    issued_at = parse_rfc3339(receipt.get("issued_at")).timestamp()
  except Exception:
    return False, R.FAIL_EXPIRED_RECEIPT
  if abs(now - issued_at) > time_window_seconds:
    return False, R.FAIL_EXPIRED_RECEIPT

  # replay (optional in this standalone tool)
  if replay_db is not None:
    nonce = receipt.get("nonce", "")
    rid = receipt.get("receipt_id", "")
    key = f"{rid}:{nonce}"
    if key in replay_db:
      return False, R.FAIL_REPLAY
    replay_db[key] = receipt.get("issued_at")

  # verify receipt signature
  subject_pk_raw = b64d(cert.get("subject_public_key_b64"))
  payload = dict(receipt)
  payload.pop("signature", None)

  receipt_sig_b64 = sig.get("sig")
  if not receipt_sig_b64:
    return False, R.FAIL_INVALID_SIGNATURE
  if not verify_ed25519(subject_pk_raw, canonical_json(payload), b64d(receipt_sig_b64)):
    return False, R.FAIL_INVALID_SIGNATURE

  return True, R.PASS


def verify_attestation(att: dict, root_pk_raw: bytes):
  payload = dict(att)
  sig_b64 = payload.pop("sig_b64", None)
  if not sig_b64:
    return False, "MISSING_SIG"
  if payload.get("spec_id") != "svs" or payload.get("spec_version") != "0.1":
    return False, R.FAIL_WRONG_SPEC
  if payload.get("conformance", {}).get("overall") != "PASS":
    return False, R.FAIL_NOT_PASS
  if not verify_ed25519(root_pk_raw, canonical_json(payload), b64d(sig_b64)):
    return False, R.FAIL_CERT_INVALID
  return True, R.PASS
