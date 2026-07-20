"""Tests for disinfo/utils/ease/ — all easing functions are pure math so
they need no fixtures and can be tested exhaustively."""
import math

import pytest

from disinfo.utils.ease import linear, cubic, sin, circle, exp, bounce
from disinfo.utils.ease.math import tpmt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _approx(a, b, tol=1e-9):
    return abs(a - b) < tol


# ---------------------------------------------------------------------------
# tpmt (helper used by exp easing)
# ---------------------------------------------------------------------------

class TestTpmt:
    def test_zero_returns_one(self):
        # tpmt(0) = (2^0 - 0.0009765625) * scale ≈ 1
        assert abs(tpmt(0) - 1.0) < 1e-6

    def test_one_returns_zero(self):
        # tpmt(1) = (2^-10 - 0.0009765625) * scale ≈ 0
        assert abs(tpmt(1)) < 1e-6

    def test_monotone_decreasing(self):
        values = [tpmt(t / 10) for t in range(11)]
        for a, b in zip(values, values[1:]):
            assert a >= b


# ---------------------------------------------------------------------------
# Linear
# ---------------------------------------------------------------------------

class TestLinear:
    def test_identity(self):
        for v in [0.0, 0.25, 0.5, 0.75, 1.0]:
            assert linear.linear(v) == pytest.approx(v)

    def test_negative_abs(self):
        # linear takes abs(t)
        assert linear.linear(-0.5) == pytest.approx(0.5)

    def test_boundary_zero(self):
        assert linear.linear(0) == 0.0

    def test_boundary_one(self):
        assert linear.linear(1) == 1.0


# ---------------------------------------------------------------------------
# Cubic
# ---------------------------------------------------------------------------

class TestCubic:
    @pytest.mark.parametrize("fn", [cubic.cubic_in, cubic.cubic_out, cubic.cubic_in_out])
    def test_starts_at_zero(self, fn):
        assert fn(0) == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.parametrize("fn", [cubic.cubic_in, cubic.cubic_out, cubic.cubic_in_out])
    def test_ends_at_one(self, fn):
        assert fn(1) == pytest.approx(1.0, abs=1e-9)

    def test_cubic_in_midpoint_less_than_half(self):
        # cubic_in is concave-up — f(0.5) < 0.5
        assert cubic.cubic_in(0.5) < 0.5

    def test_cubic_out_midpoint_greater_than_half(self):
        # cubic_out is concave-down — f(0.5) > 0.5
        assert cubic.cubic_out(0.5) > 0.5

    def test_cubic_in_out_symmetry(self):
        # f(0.5) == 0.5
        assert cubic.cubic_in_out(0.5) == pytest.approx(0.5, abs=1e-9)

    def test_cubic_in_monotone(self):
        vals = [cubic.cubic_in(t / 100) for t in range(101)]
        for a, b in zip(vals, vals[1:]):
            assert a <= b + 1e-12


# ---------------------------------------------------------------------------
# Sin
# ---------------------------------------------------------------------------

class TestSin:
    @pytest.mark.parametrize("fn", [sin.sin_in, sin.sin_out, sin.sin_in_out])
    def test_starts_at_zero(self, fn):
        assert fn(0) == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.parametrize("fn", [sin.sin_in, sin.sin_out, sin.sin_in_out])
    def test_ends_at_one(self, fn):
        assert fn(1) == pytest.approx(1.0, abs=1e-9)

    def test_sin_in_out_symmetry(self):
        assert sin.sin_in_out(0.5) == pytest.approx(0.5, abs=1e-9)

    def test_sin_out_quarter(self):
        # sin_out(0.5) = sin(pi/4)
        assert sin.sin_out(0.5) == pytest.approx(math.sin(math.pi / 4), abs=1e-9)


# ---------------------------------------------------------------------------
# Circle
# ---------------------------------------------------------------------------

class TestCircle:
    @pytest.mark.parametrize("fn", [circle.circle_in, circle.circle_out, circle.circle_in_out])
    def test_starts_at_zero(self, fn):
        assert fn(0) == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.parametrize("fn", [circle.circle_in, circle.circle_out, circle.circle_in_out])
    def test_ends_at_one(self, fn):
        assert fn(1) == pytest.approx(1.0, abs=1e-9)

    def test_circle_in_out_symmetry(self):
        assert circle.circle_in_out(0.5) == pytest.approx(0.5, abs=1e-9)

    def test_circle_in_monotone(self):
        vals = [circle.circle_in(t / 100) for t in range(101)]
        for a, b in zip(vals, vals[1:]):
            assert a <= b + 1e-12


# ---------------------------------------------------------------------------
# Exp
# ---------------------------------------------------------------------------

class TestExp:
    @pytest.mark.parametrize("fn", [exp.exp_in, exp.exp_out, exp.exp_in_out])
    def test_starts_at_zero(self, fn):
        assert fn(0) == pytest.approx(0.0, abs=1e-6)

    @pytest.mark.parametrize("fn", [exp.exp_in, exp.exp_out, exp.exp_in_out])
    def test_ends_at_one(self, fn):
        assert fn(1) == pytest.approx(1.0, abs=1e-6)

    def test_exp_in_out_midpoint(self):
        assert exp.exp_in_out(0.5) == pytest.approx(0.5, abs=1e-6)


# ---------------------------------------------------------------------------
# Bounce
# ---------------------------------------------------------------------------

class TestBounce:
    @pytest.mark.parametrize("fn", [bounce.bounce_in, bounce.bounce_out, bounce.bounce_in_out])
    def test_starts_at_zero(self, fn):
        assert fn(0) == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.parametrize("fn", [bounce.bounce_in, bounce.bounce_out, bounce.bounce_in_out])
    def test_ends_at_one(self, fn):
        assert fn(1) == pytest.approx(1.0, abs=1e-9)

    def test_bounce_out_above_zero(self):
        # bounce_out should stay >= 0 everywhere in [0, 1]
        for i in range(101):
            assert bounce.bounce_out(i / 100) >= -1e-9

    def test_bounce_in_out_midpoint(self):
        assert bounce.bounce_in_out(0.5) == pytest.approx(0.5, abs=1e-9)
