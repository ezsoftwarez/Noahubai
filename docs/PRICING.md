# Noahubai Pricing

Monetization is **workflow value**, not per-token billing. Users bring their own API keys (BYOK); we charge for features that save time and enable collaboration.

## Plans

### Free (open-source core)

For single-user local use. No license required.

| Feature | Included |
|---------|----------|
| AI Hub local chat + Cursor bridge | Yes |
| BYOK providers (OpenRouter, Ollama, etc.) | Yes |
| Transcript import / outbox relay | Yes |
| Basic project organization | Yes |
| Single-machine agent workflows | Yes |
| Noahubai backend (Memory, Issue, Fixer) | Yes |
| Community support | Yes |

**License tier id:** `free`

---

### Pro

For power users who want deeper workflow automation and polish.

| Feature | Included |
|---------|----------|
| Everything in Free | Yes |
| Advanced project memory & searchable session history | Yes |
| Multi-project orchestration | Yes |
| Background automation recipes | Yes |
| Packaged updates / one-click installer channel | Yes |
| Premium import/export workflows | Yes |
| Local-first analytics & audit trail | Yes |
| Email support | Yes |

**License tier id:** `pro`

Suggested positioning: *"Ship faster with persistent project brain and automation."*

---

### Team / Studio

For small teams once single-user traction exists.

| Feature | Included |
|---------|----------|
| Everything in Pro | Yes |
| Shared workspaces | Yes |
| Team knowledge base | Yes |
| Permissioned agent actions | Yes |
| Activity history / audit logs (team scope) | Yes |
| Managed sync / relay service | Yes |
| Priority support & onboarding | Yes |

**License tier id:** `team`

Suggested positioning: *"Same local-first stack, shared safely across your studio."*

---

## What we do not charge for

- Raw LLM tokens (users pay providers directly)
- Basic local install and open-source core usage
- Optional experiment demos (job boards, freelance tools)

## Services (parallel revenue)

Available before or alongside subscriptions:

- Local AI stack setup and customization
- Packaged agent / workflow bundles for specific domains
- Cursor workflow consulting and integration help

## Technical enforcement

Plan boundaries are enforced in the backend entitlement layer:

- `GET /api/entitlements` — current plan and enabled features
- `POST /api/entitlements/activate` — activate a license key (Pro/Team)
- Premium routes return `403` with upgrade hint when the feature is not entitled

See [`backend/entitlements.py`](../backend/entitlements.py) for the feature matrix.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `NOAHUBAI_LICENSE_KEY` | Optional license key for Pro/Team |
| `NOAHUBAI_PLAN` | Override plan for dev (`free`, `pro`, `team`) |
| `NOAHUBAI_ENTITLEMENTS_STRICT` | If `true`, block premium API routes without entitlement |

Default local development: **Free**, non-strict (premium routes warn but may allow for testing).
