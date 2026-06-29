# Guardrails — Hermes XAUUSD IB Trading Desk

Hard rules for agent, operator, and codebase. Violations block publish or merge.

## G1 — Publish Gate

**Never** post to Telegram Signal Group unless:
- `signal_decision.decision == "approve"`
- Setup `STATUS == live` (or explicit operator override logged)
- Human approval received (MVP: every publish)

## G2 — No Trade Execution

This system generates and validates **signals only**. No broker API, no order placement, no position management automation in this project phase.

## G3 — No Credential Handling

Agent and MCP must **never** request, store, or process:
- Client passwords
- Broker login credentials
- API keys for execution accounts
- 2FA tokens

## G4 — No Profit Guarantees

Prohibited in signal copy, seeding, dashboard, and brain notes:
- "Guaranteed profit" / "sure win" / "100% accuracy"
- Implied certainty of outcome
- Pressure to overtrade ("don't miss", "last chance", "all in")

**Allowed:** Historical stats with disclaimers, education, risk reminders, forward test framing.

## G5 — No Overtrading Optimization

Optimize for:
- Signal quality (RR, session fit, replay pass)
- Risk control (lot caps per group)
- Client trust (consistent format, honest journal)

Do **not** optimize for signal frequency, volume, or engagement metrics.

## G6 — Human Approval for Risky Actions

Requires Alex approval:
- Telegram Signal Group publish (MVP: all)
- Promoting setup to `live`
- Creating new cron jobs
- Changing client group risk parameters

## G7 — Replay Before Promotion

Any **new setup** must pass `replay_signals` before first `live` promotion. No exceptions.

## G8 — Journal + Brain on Close

Every closed signal must:
1. Append journal entry (`append_journal`)
2. Append brain outcome (`update_brain`)
3. Update pairing note if pattern confirmed or refuted

## G9 — Scope Boundary

**Not in this repo:**
- Content Engine
- X Funnel Pack
- BioLink funnel
- Full CRM
- Sales automation bots

## Enforcement

| Layer | Mechanism |
|-------|-----------|
| Cursor agent | `.cursor/rules/hermes-xauusd-desk.mdc` |
| Hermes agent | `agents/hermes-xauusd-agent.md` |
| MCP tools | `post_signal_to_telegram` checks decision + status |
| Operator | SOP daily review + monthly audit |

## Incident Response

If guardrail violated:
1. Stop publish / disable cron if active
2. Document in journal-room
3. Fix copy or config
4. Re-run validation before resuming
