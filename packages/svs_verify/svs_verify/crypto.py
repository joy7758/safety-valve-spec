import base64
import datetime
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

RFC3339 = "%Y-%m-%dT%H:%M:%SZ"


def b64d(s: str) -> bytes:
  return base64.b64decode(s.encode("ascii"))


def canonical_json(obj) -> bytes:
  return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def parse_rfc3339(s: str) -> datetime.datetime:
  return datetime.datetime.strptime(s, RFC3339)


def verify_ed25519(pk_raw: bytes, msg: bytes, sig: bytes) -> bool:
  pk = Ed25519PublicKey.from_public_bytes(pk_raw)
  try:
    pk.verify(sig, msg)
    return True
  except Exception:
    return False
