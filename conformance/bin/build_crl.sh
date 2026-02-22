#!/usr/bin/env bash
set -euo pipefail
# Ensure keys exist
test -f keys/root_ca.sk.b64 || python tools/ca_generate_root.py
test -f keys/impl.kid || python tools/ca_issue_cert.py

IMPL_KID="$(cat keys/impl.kid)"
python tools/crl_generate.py conformance/vectors/crl.active.json "$IMPL_KID"
python tools/crl_verify.py conformance/vectors/crl.active.json
