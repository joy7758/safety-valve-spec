# Governance (SVS)

## Roles
- Maintainers: approve releases, manage keys/prefixes, merge spec changes.
- Contributors: propose changes via RFC.

## Change Process
- Spec changes require an RFC PR: `RFC/<id>-<title>.md`
- 2 maintainer approvals for merge.
- Backward compatibility required for v0.x (additive changes only).

## Compatibility Claims
Only implementations passing `conformance/tests.md` may claim "SVS-Compatible v0.1".
