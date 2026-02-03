"""CI matrix failure trigger for self-healing verification.

This file is intentionally Python 3.11+ only to fail the CI 3.10 job while
still passing locally on Python 3.13.
"""

from typing import Self


class _CompatProbe:
    def clone(self: Self) -> Self:
        return self


def test_self_healing_trigger_marker() -> None:
    assert _CompatProbe().clone() is not None
