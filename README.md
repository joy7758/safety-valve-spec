# Safety Valve Spec (SVS)

## Quick Copy-Paste
- Latest release: `v0.1.4`
- Pinned issue: https://github.com/joy7758/safety-valve-spec/issues/1
- Changelog: `CHANGELOG.md`
- Announcement: `docs/ANNOUNCE_v0.1.2.md`

One-command demo + proofs:
```bash
git clone https://github.com/joy7758/safety-valve-spec.git
cd safety-valve-spec
git checkout v0.1.4
cd examples/reference-pack
DEMO_WITH_CONFORMANCE=1 make demo
```

<!-- SVS_BADGE_BEGIN -->
![SVS Compatible](dist/svs-compat.badge.svg)

```bash
python tools/compat_verify.py dist/svs-compat.attestation.json
```
<!-- SVS_BADGE_END -->


A minimal, verifiable **Audit Receipt** standard + **Conformance Tests** for AI/Agent actions.

## What this is
- A **receipt format** (JSON) that can be cryptographically verified.
- A **policy gate contract**: no receipt → no real-world action.
- A **conformance test suite**: pass the tests → claim compatibility.

## Compatibility
An implementation is **SVS-Compatible** if it:
1) produces verifiable receipts for ALLOW/DENY/DEGRADE,
2) enforces "no receipt, no action" at the action boundary,
3) passes the conformance tests in `conformance/tests.md`.

## Quick Start
- Spec: `spec/receipt-v0.1.md`
- JSON Schema: `schemas/receipt.v0.1.json`
- Test plan: `conformance/tests.md`
- Verify tool: `tools/verify_receipt.py`

> v0.1 focuses on **action-boundary enforcement** and **receipt verifiability**.

## CA Mode (recommended)
- Root CA issues an SVS certificate binding `kid -> public_key`.
- Implementations sign receipts with their own keys and embed the cert.
- Verifiers validate: cert signature (root) -> receipt signature (leaf) -> nonce/time-window.

### Commands
```bash
source .venv/bin/activate
python tools/ca_generate_root.py
python tools/ca_issue_cert.py
python tools/receipt_sign.py examples/allow.receipt.json examples/signed/allow.receipt.signed.json
python tools/verify_receipt.py examples/signed/allow.receipt.signed.json
```

## Conformance
Run all conformance tests locally:
```bash
source .venv/bin/activate
bash conformance/run.sh
cat conformance/report.json
```

Note:
- T01/T07/T09/T10 are now covered by the gateway action-boundary demo in `conformance/run.sh`.

## Gateway Demo (action-boundary)
Run the gateway:
```bash
source .venv/bin/activate
python -m uvicorn demo.gateway_server:app --host 127.0.0.1 --port 8089
```
Conformance runner will start/stop it automatically:
```bash
bash conformance/run.sh
```

### Recommended transport
Use `X-SVS-Receipt-B64` header (base64-encoded UTF-8 JSON) to avoid quoting issues across shells/CI.

## Revocation (CRL)
SVS supports CRL v0.1 (signed by Root CA). Verifiers may load an active CRL and reject revoked `kid`s.
- Spec: `spec/crl-v0.1.md`
- Tooling: `tools/crl_generate.py`, `tools/crl_verify.py`

## Compatibility Attestation
After conformance passes, SVS can emit a signed compatibility attestation:
- Spec: `spec/compat-attestation-v0.1.md`
- Emit: `python tools/compat_emit.py --report conformance/report.json --out dist/svs-compat.attestation.json`
- Verify: `python tools/compat_verify.py dist/svs-compat.attestation.json`

Conformance runner does this automatically and outputs `dist/svs-compat.attestation.json`.

<!-- SVS_REUSABLE_WORKFLOW_BEGIN -->
## Reusable Conformance Workflow (for other repos)

Other repositories can reuse this conformance workflow:

```yaml
name: svs-check
on:
  push:
  pull_request:

jobs:
  svs:
    uses: <OWNER>/<REPO>/.github/workflows/svs-conformance.yml@<REF>
```

It uploads artifacts:
- conformance/report.json
- dist/svs-compat.attestation.json
- dist/svs-compat.badge.svg
- dist/svs-compat.badge.md
<!-- SVS_REUSABLE_WORKFLOW_END -->

<!-- SVS_RELEASE_BEGIN -->
## Releases

Tagging a version publishes a GitHub Release with artifacts:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Release assets include:
- report.json
- svs-compat.attestation.json
- svs-compat.latest.json
- svs-compat.badge.svg
- svs-compat.badge.md
<!-- SVS_RELEASE_END -->

<!-- SVS_INTEGRATION_BEGIN -->
## Integration

- Guide: `spec/integration-guide-v0.1.md`
- Recommended pattern: **Gateway/Proxy** (hardest to bypass)
- Receipt transport: `X-SVS-Receipt-B64`

<!-- SVS_INTEGRATION_END -->

<!-- SVS_REFERENCE_PACK_BEGIN -->
## Reference Pack (Docker Compose)

If you see `make: docker: No such file or directory`, the compose binary name is mismatched. Run `make doctor`.

Quick demo (gateway + signed receipt client):
```bash
cd examples/reference-pack
make demo
```

Quick demo with proofs (runs conformance, copies artifacts to `examples/reference-pack/artifacts/`, and verifies attestation via `svs-verify`):
```bash
cd examples/reference-pack
DEMO_WITH_CONFORMANCE=1 make demo
```

Artifacts include:
- `svs-compat.attestation.json`
- `svs-compat.badge.svg`
- `report.json`
- `svs_verify_attestation.txt`

Run full conformance in Docker:
```bash
cd examples/reference-pack
make conformance
```
<!-- SVS_REFERENCE_PACK_END -->

<!-- SVS_TOOLING_BEGIN -->
## Tooling

Standalone CLI (pip):
- `packages/svs_verify` -> `svs-verify`

```bash
pip install -e packages/svs_verify
svs-verify --help
```
<!-- SVS_TOOLING_END -->

<!-- SVS_REGISTRY_V02_BEGIN -->
## Registry Export (v0.2)

- Spec: `spec/registry-export-v0.2.md`
- Export pack: `registry/README.md`
- Registry export is deterministic and committed (`registry/*.json`).

<!-- SVS_REGISTRY_V02_END -->

<!-- ECOSYSTEM_LINKS_BEGIN -->
## Ecosystem Links / 生态关系链接

![quality-baseline](https://github.com/joy7758/safety-valve-spec/actions/workflows/quality-baseline.yml/badge.svg)

### CN
- 总入口（宪章）：[RedRock-Constitution](https://github.com/joy7758/RedRock-Constitution)
- 标准注册表：[STANDARDS_REGISTRY](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/STANDARDS_REGISTRY.md#rr-svs)
- 仓库总索引：[REPOS_INDEX_CN_EN](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/REPOS_INDEX_CN_EN.md)
- 全局生态图：[ECOSYSTEM_GRAPH_CN_EN](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/ECOSYSTEM_GRAPH_CN_EN.md)
- 机器可读元数据：[`machine-readable/repository.json`](machine-readable/repository.json)

### EN
- Governance hub: [RedRock-Constitution](https://github.com/joy7758/RedRock-Constitution)
- Standards registry: [STANDARDS_REGISTRY](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/STANDARDS_REGISTRY.md#rr-svs)
- Repositories index: [REPOS_INDEX_CN_EN](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/REPOS_INDEX_CN_EN.md)
- Global ecosystem graph: [ECOSYSTEM_GRAPH_CN_EN](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/ECOSYSTEM_GRAPH_CN_EN.md)
- Machine-readable metadata: [`machine-readable/repository.json`](machine-readable/repository.json)

### Related Repositories / 关联仓库
- [aro-audit](https://github.com/joy7758/aro-audit)
- [pFDO-Specification](https://github.com/joy7758/pFDO-Specification)
- [MCP-Legal-China](https://github.com/joy7758/MCP-Legal-China)
- [RedRock-Constitution](https://github.com/joy7758/RedRock-Constitution)

### Search Keywords / 检索关键词
`safety-valve`, `agent-safety`, `conformance`, `receipt`, `policy-gate`

### Bilingual Project Abstract / 双语项目摘要
- EN: Action-boundary receipt and conformance specification for AI agent safety controls.
- CN: 面向AI代理安全控制的动作边界凭据与一致性规范。
<!-- ECOSYSTEM_LINKS_END -->
