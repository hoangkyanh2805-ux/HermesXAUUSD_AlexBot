"""Volume tracker — daily/weekly/monthly lots (KPI display only)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.common import data_path, load_json, save_json
from src.desk_config import load_market_config


def _store() -> dict[str, Any]:
    cfg = load_market_config()
    return load_json(
        data_path("volume_tracker.json"),
        {
            "daily": {},
            "weekly": {},
            "monthly": {},
            "kpi_target_monthly_lots": float(cfg["volume_kpi_monthly_lots"]),
            "total_all_time": 0.0,
        },
    )


def _save(store: dict[str, Any]) -> None:
    save_json(data_path("volume_tracker.json"), store)


def _week_key(ts: datetime) -> str:
    iso = ts.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def record_volume(*, lots: float, ts: datetime | None = None) -> dict[str, Any]:
    """Increment volume on signal close — never triggers new trades."""
    ts = ts or datetime.now(timezone.utc)
    store = _store()
    day = ts.strftime("%Y-%m-%d")
    month = ts.strftime("%Y-%m")
    week = _week_key(ts)

    store["daily"][day] = round(float(store["daily"].get(day, 0)) + lots, 2)
    store["weekly"][week] = round(float(store["weekly"].get(week, 0)) + lots, 2)
    store["monthly"][month] = round(float(store["monthly"].get(month, 0)) + lots, 2)
    store["total_all_time"] = round(float(store.get("total_all_time", 0)) + lots, 2)
    _save(store)
    return get_summary(ts=ts)


def _trading_days_in_month(ts: datetime) -> tuple[int, int, int]:
    """Return (days_in_month, weekdays_passed, weekdays_remaining) Mon-Fri."""
    import calendar

    year, month = ts.year, ts.month
    days_in_month = calendar.monthrange(year, month)[1]
    passed = 0
    total_weekdays = 0
    for day in range(1, days_in_month + 1):
        wd = datetime(year, month, day, tzinfo=timezone.utc).weekday()
        if wd < 5:
            total_weekdays += 1
            if day <= ts.day:
                passed += 1
    remaining = max(0, total_weekdays - passed)
    return total_weekdays, passed, remaining


def get_summary(ts: datetime | None = None) -> dict[str, Any]:
    ts = ts or datetime.now(timezone.utc)
    store = _store()
    day = ts.strftime("%Y-%m-%d")
    month = ts.strftime("%Y-%m")
    week = _week_key(ts)
    target = float(store.get("kpi_target_monthly_lots", 200))
    monthly = float(store.get("monthly", {}).get(month, 0))
    daily = float(store.get("daily", {}).get(day, 0))
    weekly = float(store.get("weekly", {}).get(week, 0))
    progress = round(monthly / target, 3) if target > 0 else 0.0
    remaining = round(max(0.0, target - monthly), 2)

    _, days_passed, days_remaining = _trading_days_in_month(ts)
    actual_pace = round(monthly / days_passed, 2) if days_passed > 0 else 0.0
    required_pace = (
        round(remaining / days_remaining, 2) if days_remaining > 0 and remaining > 0 else 0.0
    )
    total_weekdays, _, _ = _trading_days_in_month(
        datetime(ts.year, ts.month, 28, tzinfo=timezone.utc)
    )
    projected = round(actual_pace * total_weekdays, 2) if actual_pace > 0 else 0.0

    return {
        "daily_lots": daily,
        "weekly_lots": weekly,
        "monthly_lots": monthly,
        "kpi_target_monthly_lots": target,
        "kpi_progress": progress,
        "kpi_progress_percent": round(progress * 100, 2),
        "kpi_display_only": True,
        "total_all_time": float(store.get("total_all_time", 0)),
        "remaining_to_kpi": remaining,
        "trading_days_passed": days_passed,
        "trading_days_remaining": days_remaining,
        "required_daily_pace": required_pace,
        "actual_daily_pace": actual_pace,
        "projected_month_end_lots": projected,
    }
