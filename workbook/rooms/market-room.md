# Market Room — Mission Prompt

## Mission
Read XAUUSD market context before any signal decision: session, spread, volatility, news risk.

## Inputs
- `symbol` (must be XAUUSD)
- `timestamp` (UTC)
- Optional: quote feed or manual `spread_pts`

## Tool
`src/market_context.py` → `get_market_context()`

## Procedure
1. Determine active session (asia / london / ny) from timestamp.
2. Read or stub spread; flag if > `market-room/config.yaml` threshold.
3. Set volatility level (low / normal / elevated / high).
4. Check news risk window (high if major USD/XAU news within ±30 min).
5. Write `strategy-rooms/market-room/market_context.json`.

## Permissions
- Autonomous read/write in `market-room/`
- Do not publish to Telegram

## Stop Conditions
- `symbol != XAUUSD` → stop, return error
- Feed unavailable → write context with `"confidence": "low"`

## Failure Modes
- Stale quote → set `wait` recommendation downstream
- Spread spike → set `news_risk` or spread flag

## Escalation
If `news_risk == high` → Signal Room must not auto-approve non-news setups.

## Example Command
```text
/check_signal sig-001
```
(Step 1 runs automatically before Signal Room)

## Example Output
```json
{
  "symbol": "XAUUSD",
  "session": "london",
  "spread_pts": 28,
  "volatility": "normal",
  "news_risk": "low",
  "ts": "2026-06-29T08:00:00Z"
}
```

## Do Not
- Invent price levels
- Call broker APIs
- Skip this step before signal validation
