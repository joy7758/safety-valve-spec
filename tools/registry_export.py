#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OBJECTS_MD = ROOT / "spec" / "objects-v0.1.md"
REASONS_MD = ROOT / "spec" / "reason-codes-v0.1.md"
REGISTRY_DIR = ROOT / "registry"

OUT_TYPES = REGISTRY_DIR / "svs-types-v0.2.json"
OUT_REASONS = REGISTRY_DIR / "svs-reason-codes-v0.2.json"
OUT_PROFILES = REGISTRY_DIR / "svs-profiles-v0.2.json"

DETERMINISTIC_GENERATED_AT = "1970-01-01T00:00:00Z"


def _source_digest(objects_text: str, reasons_text: str) -> str:
    h = hashlib.sha256()
    h.update(objects_text.encode("utf-8"))
    h.update(b"\n---\n")
    h.update(reasons_text.encode("utf-8"))
    return h.hexdigest()


def _meta(source_digest: str) -> dict:
    return {
        "spec_id": "svs",
        "export_version": "0.2",
        "source_version": "0.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "source_digest_sha256": source_digest,
    }


def _parse_field_bullet(line: str) -> tuple[str, str] | None:
    m = re.match(r"^- ([A-Za-z0-9_]+):\s*(.+)$", line.strip())
    if not m:
        return None
    return m.group(1), m.group(2).strip()


def parse_types(objects_text: str) -> list[dict]:
    header_re = re.compile(
        r"^##\s+\d+\)\s+([A-Za-z0-9_]+)\s+\((svs:[^)]+)\)\s*$", re.MULTILINE
    )
    matches = list(header_re.finditer(objects_text))
    types: list[dict] = []

    for i, m in enumerate(matches):
        name = m.group(1).strip()
        source_type_id = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(objects_text)
        section = objects_text[start:end]

        purpose = ""
        purpose_m = re.search(r"^\*\*Purpose\*\*:\s*(.+)$", section, flags=re.MULTILINE)
        if purpose_m:
            purpose = purpose_m.group(1).strip()

        required_fields: list[dict] = []
        optional_fields: list[dict] = []
        mode: str | None = None

        for raw in section.splitlines():
            line = raw.strip()
            if line == "Required:":
                mode = "required"
                continue
            if line == "Optional:":
                mode = "optional"
                continue
            if not line.startswith("- "):
                continue
            parsed = _parse_field_bullet(line)
            if not parsed:
                continue
            field_name, field_spec = parsed
            entry = {"name": field_name, "spec": field_spec}
            if mode == "required":
                required_fields.append(entry)
            elif mode == "optional":
                optional_fields.append(entry)

        types.append(
            {
                "type_name": name,
                "type_id": f"svs:{name}:v0.2",
                "source_type_id": source_type_id,
                "purpose": purpose,
                "required_fields": required_fields,
                "optional_fields": optional_fields,
            }
        )

    return sorted(types, key=lambda x: x["type_name"])


def parse_reason_codes(reasons_text: str) -> tuple[list[dict], list[dict]]:
    domains: list[dict] = []
    flat: list[dict] = []
    current_domain = "Ungrouped"
    current_codes: list[str] = []

    for raw in reasons_text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            if current_codes:
                domains.append({"domain": current_domain, "codes": current_codes})
                current_codes = []
            current_domain = line[3:].strip()
            continue
        if not line.startswith("- "):
            continue
        code = line[2:].strip()
        if not code.startswith("SVS_"):
            continue
        current_codes.append(code)
        flat.append({"code": code, "domain": current_domain})

    if current_codes:
        domains.append({"domain": current_domain, "codes": current_codes})

    domains = sorted(domains, key=lambda x: x["domain"])
    for d in domains:
        d["codes"] = sorted(d["codes"])
    flat = sorted(flat, key=lambda x: x["code"])
    return flat, domains


def build_profiles(type_ids: set[str], reason_codes: list[dict]) -> list[dict]:
    reason_list = [r["code"] for r in reason_codes]

    def pref(prefixes: list[str]) -> list[str]:
        out = [c for c in reason_list if any(c.startswith(p) for p in prefixes)]
        return sorted(out)

    profiles = [
        {
            "profile_id": "svs:ActionBoundaryGate:v0.2",
            "title": "ActionBoundaryGate",
            "type_ids": sorted(
                [
                    "svs:Actor:v0.2",
                    "svs:Agent:v0.2",
                    "svs:Tool:v0.2",
                    "svs:Action:v0.2",
                    "svs:PolicyDecision:v0.2",
                    "svs:AuditReceipt:v0.2",
                ]
            ),
            "constraints": [
                "No receipt -> no action",
                "Bypass endpoints enforce the same receipt checks",
                "DEGRADE constraints are enforced at the action boundary",
            ],
            "reason_codes": pref(["SVS_GATE_", "SVS_POLICY_", "SVS_DEGRADE_", "SVS_EFFECT_"]),
        },
        {
            "profile_id": "svs:ReceiptVerifier:v0.2",
            "title": "ReceiptVerifier",
            "type_ids": sorted(
                [
                    "svs:EvidenceRef:v0.2",
                    "svs:ContextDigest:v0.2",
                    "svs:PolicyDecision:v0.2",
                    "svs:AuditReceipt:v0.2",
                ]
            ),
            "constraints": [
                "Verify cryptographic signature and certificate chain",
                "Enforce nonce replay protection",
                "Enforce receipt time window and reason-code policy",
            ],
            "reason_codes": pref(["SVS_SIG_", "SVS_CERT_", "SVS_REPLAY_", "SVS_TIME_", "SVS_POLICY_"]),
        },
        {
            "profile_id": "svs:CompatIssuer:v0.2",
            "title": "CompatIssuer",
            "type_ids": sorted(
                [
                    "svs:Policy:v0.2",
                    "svs:PolicyDecision:v0.2",
                    "svs:AuditReceipt:v0.2",
                ]
            ),
            "constraints": [
                "Conformance overall MUST be PASS before attestation",
                "Reason-code namespace remains SVS-prefixed",
                "Export payload must remain deterministic for reproducible releases",
            ],
            "reason_codes": pref(["SVS_"]),
        },
    ]

    for profile in profiles:
        profile["type_ids"] = [tid for tid in profile["type_ids"] if tid in type_ids]

    return sorted(profiles, key=lambda x: x["profile_id"])


def _safe_write(path: Path, payload: dict) -> None:
    registry_root = REGISTRY_DIR.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    resolved = path.resolve()
    if not str(resolved).startswith(str(registry_root) + "/"):
        raise RuntimeError(f"refusing to write outside registry/: {resolved}")
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    objects_text = OBJECTS_MD.read_text(encoding="utf-8")
    reasons_text = REASONS_MD.read_text(encoding="utf-8")
    digest = _source_digest(objects_text, reasons_text)
    meta = _meta(digest)

    types = parse_types(objects_text)
    reason_codes, domains = parse_reason_codes(reasons_text)
    type_ids = {t["type_id"] for t in types}
    profiles = build_profiles(type_ids, reason_codes)

    _safe_write(
        OUT_TYPES,
        {
            "meta": meta,
            "types": types,
        },
    )
    _safe_write(
        OUT_REASONS,
        {
            "domains": domains,
            "meta": meta,
            "reason_codes": reason_codes,
        },
    )
    _safe_write(
        OUT_PROFILES,
        {
            "meta": meta,
            "profiles": profiles,
        },
    )

    print("OK: generated registry exports")
    print(f"  {OUT_TYPES.relative_to(ROOT)}")
    print(f"  {OUT_REASONS.relative_to(ROOT)}")
    print(f"  {OUT_PROFILES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
