import base64
import datetime
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

RFC3339 = "%Y-%m-%dT%H:%M:%SZ"


def utcnow():
  return datetime.datetime.utcnow().replace(microsecond=0)


def to_rfc3339(dt: datetime.datetime) -> str:
  return dt.strftime(RFC3339)


def parse_rfc3339(s: str) -> datetime.datetime:
  return datetime.datetime.strptime(s, RFC3339)


def b64e(b: bytes) -> str:
  return base64.b64encode(b).decode("ascii")


def b64d(s: str) -> bytes:
  return base64.b64decode(s.encode("ascii"))


def canonical_json(obj) -> bytes:
  # stable: sort_keys + no whitespace
  return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def gen_ed25519_keypair():
  sk = Ed25519PrivateKey.generate()
  pk = sk.public_key()
  sk_raw = sk.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
  )
  pk_raw = pk.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
  )
  return sk_raw, pk_raw


def load_sk_raw(raw: bytes) -> Ed25519PrivateKey:
  return Ed25519PrivateKey.from_private_bytes(raw)


def load_pk_raw(raw: bytes) -> Ed25519PublicKey:
  return Ed25519PublicKey.from_public_bytes(raw)


def sign_ed25519(sk_raw: bytes, msg: bytes) -> bytes:
  sk = load_sk_raw(sk_raw)
  return sk.sign(msg)


def verify_ed25519(pk_raw: bytes, msg: bytes, sig: bytes) -> bool:
  pk = load_pk_raw(pk_raw)
  try:
    pk.verify(sig, msg)
    return True
  except Exception:
    return False
