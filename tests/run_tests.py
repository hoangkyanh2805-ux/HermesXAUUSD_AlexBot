"""Run all MVP tests without pytest."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests import test_integration, test_lot_calculator, test_phase_d, test_seeding_engine, test_signal_gate, test_signal_replay, test_sig_test_001, test_supabase_sync

MODULES = [
    test_signal_gate,
    test_lot_calculator,
    test_seeding_engine,
    test_signal_replay,
    test_phase_d,
    test_supabase_sync,
    test_sig_test_001,
    test_integration,
]


def main() -> int:
    passed = failed = 0
    for mod in MODULES:
        for name in dir(mod):
            if not name.startswith("test_"):
                continue
            fn = getattr(mod, name)
            try:
                fn()
                print(f"PASS {mod.__name__}.{name}")
                passed += 1
            except Exception as exc:
                print(f"FAIL {mod.__name__}.{name}: {exc}")
                failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
