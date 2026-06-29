# XAUUSD Signal Format — Telegram Signal Group

> Use for `post_signal_to_telegram`. Education framing only. No profit guarantees.

## Template

```text
🥇 XAUUSD | {setup_name}
📊 {direction} @ {entry}
🛑 SL: {sl}
🎯 TP: {tp}
📐 RR: 1:{rr}

🕐 Session: {session}
📝 {rationale_short}

⚠️ Risk reminder: Trade at your own risk. Use lot size appropriate to your account. Past performance does not guarantee future results.

#{setup_tag} #XAUUSD #Gold
```

## Fields

| Field | Required | Notes |
|-------|----------|-------|
| setup_name | Yes | e.g. London Breakout |
| direction | Yes | BUY or SELL |
| entry | Yes | Price level |
| sl | Yes | Stop loss |
| tp | Yes | Take profit |
| rr | Yes | Calculated RR ratio |
| session | Yes | London / NY / Asia |
| rationale_short | Yes | 1–2 lines, factual |
| setup_tag | Yes | lowercase slug |

## Prohibited Phrases

- Guaranteed / sure profit / 100% win
- Don't miss / last chance / all in
- Get rich / passive income promises

## Example

```text
🥇 XAUUSD | London Breakout
📊 BUY @ 2345.50
🛑 SL: 2340.00
🎯 TP: 2355.00
📐 RR: 1:2.1

🕐 Session: London
📝 Clean breakout above Asian range; spread within normal range.

⚠️ Risk reminder: Trade at your own risk. Use lot size appropriate to your account. Past performance does not guarantee future results.

#london-breakout #XAUUSD #Gold
```
