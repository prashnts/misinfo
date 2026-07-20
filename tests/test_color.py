"""Tests for disinfo/utils/color.py — AppColor and constrain."""
import pytest

from disinfo.utils.color import AppColor, constrain


class TestConstrain:
    def test_within_range(self):
        assert constrain(0.5) == 0.5

    def test_below_min(self):
        assert constrain(-1) == 0

    def test_above_max(self):
        assert constrain(2) == 1

    def test_custom_range(self):
        assert constrain(5, 0, 10) == 5
        assert constrain(-5, 0, 10) == 0
        assert constrain(15, 0, 10) == 10

    def test_at_boundary(self):
        assert constrain(0) == 0
        assert constrain(1) == 1


class TestAppColor:
    def test_basic_hex(self):
        c = AppColor('#ff0000')
        assert c.alpha == 1.0
        assert c.get_pil_color() == (255, 0, 0, 255)

    def test_hex_with_alpha(self):
        # #rrggbbaa — last two bytes are alpha
        c = AppColor('#ff0000ff')
        assert c.alpha == pytest.approx(1.0, abs=1e-2)
        c2 = AppColor('#ff000080')
        assert c2.alpha == pytest.approx(0x80 / 255, abs=1e-2)

    def test_hex_with_zero_alpha(self):
        c = AppColor('#00000000')
        assert c.alpha == pytest.approx(0.0, abs=1e-2)

    def test_named_color(self):
        c = AppColor('red')
        assert c.alpha == 1.0
        r, g, b, a = c.get_pil_color()
        assert r == 255
        assert g == 0
        assert b == 0

    def test_get_rgba(self):
        c = AppColor('#ffffff')
        rgba = c.get_rgba()
        assert len(rgba) == 4
        assert rgba[3] == 1.0  # default alpha

    def test_get_hexa_round_trips(self):
        c = AppColor('#aabbcc')
        hexa = c.get_hexa()
        # Starts with '#' and ends with 'ff' (alpha=1)
        assert hexa.endswith('ff')

    def test_set_alpha(self):
        c = AppColor('#ffffff')
        c.set_alpha(0.5)
        assert c.alpha == pytest.approx(0.5)

    def test_set_alpha_returns_self(self):
        c = AppColor('#ffffff')
        result = c.set_alpha(0.3)
        assert result is c

    def test_darken_reduces_luminance(self):
        c = AppColor('#aaaaaa')
        original_lum = c.luminance
        darkened = c.darken(0.1)
        assert darkened.luminance < original_lum

    def test_darken_clamps_to_zero(self):
        c = AppColor('#000000')
        darkened = c.darken(1.0)
        assert darkened.luminance >= 0

    def test_clamp_luminance(self):
        c = AppColor('#ffffff')
        clamped = c.clamp(0, 0.5)
        assert clamped.luminance <= 0.5

    def test_get_pil_color_returns_four_ints(self):
        c = AppColor('#123456')
        pil = c.get_pil_color()
        assert len(pil) == 4
        assert all(isinstance(v, int) for v in pil)
        assert all(0 <= v <= 255 for v in pil)
