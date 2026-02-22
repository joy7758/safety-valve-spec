#!/usr/bin/env python3
import argparse
import json
import os


def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--att", default="dist/svs-compat.attestation.json")
  ap.add_argument("--out", default="dist/svs-compat.latest.json")
  args = ap.parse_args()

  att = json.load(open(args.att, "r", encoding="utf-8"))
  latest = {
    "spec_id": att.get("spec_id", "svs"),
    "spec_version": att.get("spec_version", "0.1"),
    "issued_at": att.get("issued_at"),
    "issuer_kid": att.get("issuer_kid"),
    "subject": att.get("subject"),
    "conformance": att.get("conformance"),
    "attestation_path": "dist/svs-compat.attestation.json",
    "badge_svg_path": "dist/svs-compat.badge.svg",
    "badge_md_path": "dist/svs-compat.badge.md",
  }
  os.makedirs(os.path.dirname(args.out), exist_ok=True)
  json.dump(latest, open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
  print("OK:", args.out)


if __name__ == "__main__":
  main()
