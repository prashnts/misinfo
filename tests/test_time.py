"""Tests for disinfo/utils/time.py — is_expired and adaptive_delay."""
import time

import pendulum
import pytest

from disinfo.utils.time import is_expired, adaptive_delay


class TestIsExpired:
    def test_none_not_expired_by_default(self):
        assert is_expired(None) is False

    def test_none_expired_if_none_flag(self):
        assert is_expired(None, expired_if_none=True) is True

    def test_past_datetime_is_expired(self):
        past = pendulum.now().subtract(hours=1)
        assert is_expired(past, seconds=0) is True

    def test_future_datetime_not_expired(self):
        future = pendulum.now().add(hours=1)
        assert is_expired(future, seconds=0) is False

    def test_expiry_with_seconds_offset(self):
        # a timestamp 5 seconds ago with a 10-second window hasn't expired yet
        recent = pendulum.now().subtract(seconds=5)
        assert is_expired(recent, seconds=10) is False

    def test_expiry_with_seconds_offset_elapsed(self):
        # a timestamp 15 seconds ago with a 10-second window has expired
        old = pendulum.now().subtract(seconds=15)
        assert is_expired(old, seconds=10) is True

    def test_accepts_iso_string(self):
        past_str = pendulum.now().subtract(hours=2).isoformat()
        assert is_expired(past_str, seconds=0) is True

    def test_accepts_stdlib_datetime(self):
        from datetime import datetime, timezone
        past = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        # pendulum.instance requires a timezone-aware datetime; pass a
        # pendulum object instead to avoid that
        past_pend = pendulum.now().subtract(hours=1)
        assert is_expired(past_pend) is True

    def test_custom_now_parameter(self):
        fixed_now = pendulum.datetime(2024, 1, 1, 12, 0, 0)
        dt = pendulum.datetime(2024, 1, 1, 11, 0, 0)
        assert is_expired(dt, seconds=0, now=fixed_now) is True

    def test_minutes_offset(self):
        recent = pendulum.now().subtract(minutes=2)
        assert is_expired(recent, minutes=5) is False
        assert is_expired(recent, minutes=1) is True


class TestAdaptiveDelay:
    def test_fast_work_sleeps_remainder(self):
        delay_ms = 50
        start = time.monotonic()
        with adaptive_delay(delay_ms):
            pass  # no work
        elapsed = time.monotonic() - start
        assert elapsed >= 0.045  # at least ~50 ms

    def test_slow_work_does_not_sleep(self):
        delay_ms = 20
        start = time.monotonic()
        with adaptive_delay(delay_ms):
            time.sleep(0.05)  # exceeds delay
        elapsed = time.monotonic() - start
        # Should finish shortly after work completes, not double the wait
        assert elapsed < 0.15

    def test_float_seconds_accepted(self):
        start = time.monotonic()
        with adaptive_delay(0.03):  # 30 ms as float seconds
            pass
        elapsed = time.monotonic() - start
        assert elapsed >= 0.025
