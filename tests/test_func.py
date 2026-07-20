"""Tests for disinfo/utils/func.py — throttle and uname."""
import time

import pytest

from disinfo.utils.func import throttle, uname


class TestThrottle:
    def test_called_on_first_invocation(self):
        calls = []

        @throttle(1000)
        def fn():
            calls.append(1)
            return len(calls)

        result = fn()
        assert result == 1
        assert len(calls) == 1

    def test_subsequent_calls_within_duration_return_cached(self):
        calls = []

        @throttle(500)
        def fn():
            calls.append(1)
            return len(calls)

        fn()
        fn()
        fn()
        assert len(calls) == 1

    def test_call_after_duration_executes_again(self):
        calls = []

        @throttle(10)  # 10 ms
        def fn():
            calls.append(1)
            return len(calls)

        fn()
        time.sleep(0.02)  # wait > 10 ms
        fn()
        assert len(calls) == 2

    def test_returns_cached_value_within_window(self):
        counter = [0]

        @throttle(500)
        def fn():
            counter[0] += 1
            return counter[0]

        first = fn()
        second = fn()
        assert first == second == 1

    def test_independent_throttle_instances(self):
        calls_a = []
        calls_b = []

        @throttle(500)
        def fn_a():
            calls_a.append(1)

        @throttle(500)
        def fn_b():
            calls_b.append(1)

        fn_a()
        fn_a()
        fn_b()
        assert len(calls_a) == 1
        assert len(calls_b) == 1


class TestUname:
    def test_returns_string(self):
        result = uname()
        assert isinstance(result, str)

    def test_contains_caller_info(self):
        result = uname()
        # Should reference the test function or file name
        assert 'test_func' in result or 'test_uname' in result

    def test_level_controls_depth(self):
        result_shallow = uname(level=2)
        result_deep = uname(level=5)
        # Deeper level should contain at least as many characters
        assert len(result_deep) >= len(result_shallow)
