#!/usr/bin/env bash
set -euo pipefail

echo "[1/2] run conformance"
bash conformance/run.sh | tee examples/reference-pack/artifacts/conformance.log

echo "[2/2] done. artifacts:"
ls -la dist || true
