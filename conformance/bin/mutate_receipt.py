#!/usr/bin/env python3
import json
import sys

def main():
  if len(sys.argv) < 4:
    print("Usage: mutate_receipt.py <in.json> <out.json> <mode> [args]")
    sys.exit(2)
  in_path, out_path, mode = sys.argv[1], sys.argv[2], sys.argv[3]
  r = json.load(open(in_path,"r",encoding="utf-8"))

  if mode == "tamper_effect":
    r["decision"]["effect"] = "ALLOW" if r["decision"]["effect"] != "ALLOW" else "DENY"

  elif mode == "tamper_tool":
    r["tool"]["name"] = r["tool"]["name"] + "_tampered"

  elif mode == "remove_cert":
    if "signature" in r and isinstance(r["signature"], dict):
      r["signature"].pop("cert", None)

  elif mode == "wrong_issuer":
    r["signature"]["cert"]["issuer_kid"] = "svs-root-kid-999"

  elif mode == "expire_receipt":
    # set issued_at far in past
    r["issued_at"] = "2020-01-01T00:00:00Z"

  elif mode == "replay_same_nonce":
    # keep same nonce/receipt_id; used by running verify twice
    pass

  elif mode == "forge_receipt_sig":
    r["signature"]["sig"] = "AAAA"  # base64 but wrong

  elif mode == "forge_cert_sig":
    r["signature"]["cert"]["sig_b64"] = "AAAA"

  else:
    print("Unknown mode:", mode)
    sys.exit(2)

  json.dump(r, open(out_path,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
  print("OK", out_path)

if __name__ == "__main__":
  main()
