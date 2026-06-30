"""Market data package."""

from src.market_data.alpha_vantage import fetch_live_macro_alpha, fetch_live_macro_alpha_safe
from src.market_data.live_feed import fetch_live_macro, fetch_live_macro_safe, fetch_yahoo_macro

__all__ = [
    "fetch_live_macro",
    "fetch_live_macro_safe",
    "fetch_yahoo_macro",
    "fetch_live_macro_alpha",
    "fetch_live_macro_alpha_safe",
]
