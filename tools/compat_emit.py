#!/usr/bin/env python3
import json, uuid, os
try:
  from tools.svs_crypto import utcnow, to_rfc3339, b64d, b64e, canonical_json, sign_ed25519
except ModuleNotFoundError:
  from svs_crypto import utcnow, to_rfc3339, b64d, b64e, canonical_json, sign_ed25519

def main():
  import argparse
  ap = argparse.ArgumentParser()
  ap.add_argument("--report", default="conformance/report.json")
  ap.add_argument("--out", default="dist/svs-compat.attestation.json")
  args = ap.parse_args()

  # Load report
  rep = json.load(open(args.report, "r", encoding="utf-8"))
  overall = rep.get("overall")
  if overall != "PASS":
    raise SystemExit("Report overall is not PASS")

  results = rep.get("results", [])
  passed = [r["id"] for r in results if r.get("status") == "PASS"]
  skipped = [r["id"] for r in results if r.get("status") == "SKIP"]

  # Load implementation cert/kid (subject)
  cert = json.load(open("keys/impl.cert.json", "r", encoding="utf-8"))
  subject_kid = open("keys/impl.kid", "r", encoding="utf-8").read().strip()
  subject_cert_id = cert.get("cert_id")

  # Load root issuer
  issuer_kid = open("keys/root_ca.kid", "r", encoding="utf-8").read().strip()
  root_sk = b64d(open("keys/root_ca.sk.b64", "r", encoding="utf-8").read().strip())

  payload = {
    "att_version": "0.1",
    "att_id": f"att-{uuid.uuid4()}",
    "spec_id": "svs",
    "spec_version": "0.1",
    "issuer_kid": issuer_kid,
    "issued_at": to_rfc3339(utcnow()),
    "subject": {
      "subject_kid": subject_kid,
      "subject_cert_id": subject_cert_id
    },
    "conformance": {
      "overall": "PASS",
      "passed": passed,
      "skipped": skipped,
      "report_path": args.report
    },
    "policy": {
      "reason_codes_version": "0.1",
      "namespace_version": "0.1"
    }
  }

  sig = sign_ed25519(root_sk, canonical_json(payload))
  att = dict(payload)
  att["sig_b64"] = b64e(sig)

  os.makedirs(os.path.dirname(args.out), exist_ok=True)
  json.dump(att, open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
  print("OK:", args.out)

if __name__ == "__main__":
  main()
