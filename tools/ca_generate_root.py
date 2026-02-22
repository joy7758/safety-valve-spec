#!/usr/bin/env python3
import os
from svs_crypto import b64e, gen_ed25519_keypair


def main():
  os.makedirs("keys", exist_ok=True)
  sk, pk = gen_ed25519_keypair()
  # You control these:
  root_kid = "svs-root-kid-001"
  open("keys/root_ca.sk.b64", "w", encoding="utf-8").write(b64e(sk) + "\n")
  open("keys/root_ca.pk.b64", "w", encoding="utf-8").write(b64e(pk) + "\n")
  open("keys/root_ca.kid", "w", encoding="utf-8").write(root_kid + "\n")
  print("OK: generated Root CA")
  print("  kid:", root_kid)
  print("  keys/root_ca.sk.b64 (KEEP SECRET)")
  print("  keys/root_ca.pk.b64")


if __name__ == "__main__":
  main()
