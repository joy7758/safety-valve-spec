# Threat Model v0.1

## Attack Surfaces
- Forged receipts (fake JSON)
- Tampering (modify fields post-issuance)
- Replay (re-use old receipts)
- Bypass execution path (side-channel API)
- Selective logging (drop DENY receipts)
- DoS via forced denies (should degrade locally, not global self-destruct)

## Defenses (v0.1)
- Signature verification (Ed25519)
- Nonce + time window replay protection
- Action boundary enforcement: no receipt, no action
- DENY/DEGRADE receipts mandatory
