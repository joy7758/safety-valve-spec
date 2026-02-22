#!/usr/bin/env python3
import json
import os


def svg_badge(label: str, value: str) -> str:
  label_w = max(60, 8 * len(label) + 18)
  value_w = max(90, 8 * len(value) + 18)
  total = label_w + value_w

  v = value.upper()
  if "PASS" in v:
    right = "#2ea44f"
  elif "FAIL" in v:
    right = "#d73a49"
  else:
    right = "#dbab09"

  return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_w}" height="20" fill="#24292f"/>
    <rect x="{label_w}" width="{value_w}" height="20" fill="{right}"/>
    <rect width="{total}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_w/2}" y="14">{label}</text>
    <text x="{label_w + value_w/2}" y="14">{value}</text>
  </g>
</svg>
'''


def main():
  import argparse

  ap = argparse.ArgumentParser()
  ap.add_argument("--att", default="dist/svs-compat.attestation.json")
  ap.add_argument("--svg", default="dist/svs-compat.badge.svg")
  ap.add_argument("--md", default="dist/svs-compat.badge.md")
  args = ap.parse_args()

  att = json.load(open(args.att, "r", encoding="utf-8"))
  overall = att.get("conformance", {}).get("overall", "UNKNOWN")
  spec_ver = att.get("spec_version", "0.1")

  os.makedirs(os.path.dirname(args.svg), exist_ok=True)
  open(args.svg, "w", encoding="utf-8").write(svg_badge("SVS", f"{overall} v{spec_ver}"))

  md = f"""# SVS Compatibility Badge

![SVS Compatible](dist/svs-compat.badge.svg)

## Verify
```bash
python tools/compat_verify.py dist/svs-compat.attestation.json
```
"""
  open(args.md, "w", encoding="utf-8").write(md)
  print("OK:", args.svg)
  print("OK:", args.md)


if __name__ == "__main__":
  main()
