# Objects v0.1 (Type Dictionary)

Spec ID: `svs`
Version: `0.1`

This dictionary defines minimal objects used by SVS receipts and policy gating.

---

## 1) Actor  (svs:Actor:v0.1)
**Purpose**: Identify who initiates or owns an action.
Required:
- type: string  (e.g., "user" | "system" | "service")
- id: string
Optional:
- tenant_id: string
- display: string

## 2) Agent  (svs:Agent:v0.1)
**Purpose**: Identify the AI/agent runtime.
Required:
- name: string
- version: string
Optional:
- model: string
- framework: string
- build_id: string

## 3) IntentAnchor  (svs:IntentAnchor:v0.1)
**Purpose**: Bind long-horizon goals / task scope.
Required:
- intent_id: string
Optional:
- scope: string
- parent_intent_id: string

## 4) Policy  (svs:Policy:v0.1)
**Purpose**: Identify the policy set used.
Required:
- policy_id: string
- policy_version: string
Optional:
- policy_hash: string

## 5) Tool  (svs:Tool:v0.1)
**Purpose**: Identify the execution target/system.
Required:
- name: string
- action_type: string
Optional:
- endpoint: string
- permission_scope: string

## 6) Action  (svs:Action:v0.1)
**Purpose**: Describe the intended operation.
Required:
- action_id: string
- params_digest: string  (e.g., "sha256:<...>")
Optional:
- params_schema_id: string

## 7) EvidenceRef  (svs:EvidenceRef:v0.1)
**Purpose**: Reference supporting evidence (optional but recommended for high risk).
Required:
- evidence_type: string
- digest: string
Optional:
- uri: string
- note: string

## 8) ContextDigest  (svs:ContextDigest:v0.1)
**Purpose**: Hash of relevant input context.
Required:
- context_digest: string

## 9) PolicyDecision  (svs:PolicyDecision:v0.1)
**Purpose**: The enforced outcome.
Required:
- effect: "ALLOW" | "DENY" | "DEGRADE"
- reason_code: string  (see `spec/reason-codes-v0.1.md`)
Optional:
- constraints: object

## 10) AuditReceipt  (svs:AuditReceipt:v0.1)
**Purpose**: Verifiable enforcement receipt.
Required:
- receipt_version: "0.1"
- receipt_id: string
- issued_at: RFC3339 UTC
- nonce: string
- actor: Actor
- agent: Agent
- intent: IntentAnchor
- policy: Policy
- tool: Tool
- action: Action
- context_digest: string
- decision: PolicyDecision
- signature: object (Ed25519 + cert mode)
Optional:
- output_digest: string (required for ALLOW/DEGRADE by policy)
- evidence_refs: EvidenceRef[]
