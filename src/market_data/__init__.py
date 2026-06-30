"""Market data package."""

from src.market_data.live_feed import fetch_live_macro, fetch_live_macro_safe

__all__ = ["fetch_live_macro", "fetch_live_macro_safe"]
