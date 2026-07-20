"""Tests for disinfo/components/layouts.py — hstack, vstack, composite_at, mosaic."""
import pytest
from PIL import Image

from disinfo.components.elements import Frame
from disinfo.components.layouts import (
    apply_blur,
    composite_at,
    hstack,
    mosaic,
    vstack,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def frame(w, h, color=(255, 255, 255, 255)) -> Frame:
    return Frame(Image.new('RGBA', (w, h), color))


# ---------------------------------------------------------------------------
# hstack
# ---------------------------------------------------------------------------

class TestHStack:
    def test_width_is_sum(self):
        a = frame(10, 5)
        b = frame(6, 5)
        result = hstack([a, b])
        assert result.width == 16

    def test_height_is_max(self):
        a = frame(5, 3)
        b = frame(5, 8)
        result = hstack([a, b])
        assert result.height == 8

    def test_gap_added(self):
        a = frame(10, 5)
        b = frame(10, 5)
        result = hstack([a, b], gap=4)
        assert result.width == 24

    def test_empty_list_returns_fallback(self):
        result = hstack([None, None])
        assert result.width == 1
        assert result.height == 1

    def test_nones_filtered_out(self):
        a = frame(10, 5)
        result = hstack([None, a, None])
        assert result.width == 10

    def test_top_alignment(self):
        a = frame(5, 3)
        b = frame(5, 8)
        result = hstack([a, b], align='top')
        assert result.height == 8

    def test_bottom_alignment(self):
        a = frame(5, 3)
        b = frame(5, 8)
        result = hstack([a, b], align='bottom')
        assert result.height == 8

    def test_single_element(self):
        a = frame(7, 4)
        result = hstack([a])
        assert result.size == (7, 4)


# ---------------------------------------------------------------------------
# vstack
# ---------------------------------------------------------------------------

class TestVStack:
    def test_height_is_sum(self):
        a = frame(5, 10)
        b = frame(5, 6)
        result = vstack([a, b])
        assert result.height == 16

    def test_width_is_max(self):
        a = frame(3, 5)
        b = frame(8, 5)
        result = vstack([a, b])
        assert result.width == 8

    def test_gap_added(self):
        a = frame(5, 10)
        b = frame(5, 10)
        result = vstack([a, b], gap=3)
        assert result.height == 23

    def test_empty_list_returns_fallback(self):
        result = vstack([None, None])
        assert result.width == 1
        assert result.height == 1

    def test_left_alignment(self):
        result = vstack([frame(4, 4), frame(8, 4)], align='left')
        assert result.width == 8

    def test_center_alignment(self):
        result = vstack([frame(4, 4), frame(8, 4)], align='center')
        assert result.width == 8

    def test_right_alignment(self):
        result = vstack([frame(4, 4), frame(8, 4)], align='right')
        assert result.width == 8


# ---------------------------------------------------------------------------
# apply_blur
# ---------------------------------------------------------------------------

class TestApplyBlur:
    def test_returns_frame(self):
        f = frame(10, 10)
        result = apply_blur(f, 2.0)
        assert isinstance(result, Frame)

    def test_same_size(self):
        f = frame(12, 8)
        result = apply_blur(f, 1.0)
        assert result.size == (12, 8)

    def test_zero_radius_unchanged(self):
        f = frame(4, 4, color=(200, 100, 50, 255))
        result = apply_blur(f, 0)
        # Pixel values should be identical for a solid colour
        px_in = f.image.getpixel((0, 0))
        px_out = result.image.getpixel((0, 0))
        assert px_in == px_out


# ---------------------------------------------------------------------------
# composite_at
# ---------------------------------------------------------------------------

class TestCompositeAt:
    def test_returns_frame(self):
        f = frame(4, 4, color=(255, 0, 0, 255))
        dest = frame(10, 10, color=(0, 0, 0, 255))
        result = composite_at(f, dest, anchor='mm')
        assert isinstance(result, Frame)

    def test_dest_size_preserved(self):
        f = frame(4, 4)
        dest = frame(20, 20)
        result = composite_at(f, dest, anchor='tl')
        assert result.size == (20, 20)

    def test_none_frame_returns_dest(self):
        dest = frame(8, 8)
        result = composite_at(None, dest, anchor='mm')
        assert result is dest

    @pytest.mark.parametrize("anchor", ['tl', 'tm', 'tr', 'ml', 'mm', 'mr', 'bl', 'bm', 'br'])
    def test_all_anchors(self, anchor):
        f = frame(4, 4)
        dest = frame(10, 10)
        result = composite_at(f, dest, anchor=anchor)
        assert result.size == (10, 10)


# ---------------------------------------------------------------------------
# mosaic
# ---------------------------------------------------------------------------

class TestMosaic:
    def test_size_2x2(self):
        f = frame(4, 4)
        result = mosaic(f, nx=2, ny=2)
        assert result.size == (8, 8)

    def test_size_3x2(self):
        f = frame(4, 6)
        result = mosaic(f, nx=3, ny=2)
        assert result.size == (12, 12)

    def test_seamless_same_size(self):
        f = frame(4, 4)
        result = mosaic(f, nx=2, ny=2, seamless=True)
        assert result.size == (8, 8)

    def test_non_seamless_same_size(self):
        f = frame(4, 4)
        result = mosaic(f, nx=2, ny=2, seamless=False)
        assert result.size == (8, 8)

    def test_1x1_equals_original(self):
        f = frame(4, 4, color=(42, 42, 42, 255))
        result = mosaic(f, nx=1, ny=1, seamless=False)
        assert result.size == (4, 4)
        assert result.image.getpixel((0, 0)) == f.image.getpixel((0, 0))
