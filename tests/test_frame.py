"""Tests for disinfo/components/elements.py — Frame and StillImage."""
import pytest
from PIL import Image

from disinfo.components.elements import Frame


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def solid_frame(w=10, h=10, color=(255, 0, 0, 255)) -> Frame:
    return Frame(Image.new('RGBA', (w, h), color))


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestFrameConstruction:
    def test_dimensions_match_image(self):
        f = solid_frame(20, 15)
        assert f.width == 20
        assert f.height == 15

    def test_size_property(self):
        f = solid_frame(8, 12)
        assert f.size == (8, 12)

    def test_auto_hash_is_set(self):
        f = solid_frame()
        assert f.hash is not None

    def test_explicit_hash(self):
        f = Frame(Image.new('RGBA', (4, 4)), hash='my-hash')
        assert f.hash == 'my-hash'

    def test_fallback_factory(self):
        f = Frame.fallback(hash='test', size=(5, 5))
        assert f.width == 5
        assert f.height == 5


# ---------------------------------------------------------------------------
# reposition
# ---------------------------------------------------------------------------

class TestReposition:
    def test_same_size(self):
        f = solid_frame(8, 8)
        r = f.reposition(0, 0)
        assert r.size == (8, 8)

    def test_positive_offset(self):
        f = solid_frame(8, 8, color=(255, 255, 255, 255))
        r = f.reposition(2, 2)
        # top-left corner should be transparent after repositioning
        px = r.image.getpixel((0, 0))
        assert px[3] == 0  # alpha channel

    def test_hash_differs_from_original(self):
        f = solid_frame()
        r = f.reposition(1, 1)
        assert r.hash != f.hash


# ---------------------------------------------------------------------------
# rotate
# ---------------------------------------------------------------------------

class TestRotate:
    def test_rotate_360_same_size(self):
        f = solid_frame(10, 10)
        r = f.rotate(360)
        assert r.size == f.size

    def test_rotate_90_swaps_dimensions(self):
        f = solid_frame(10, 6)
        r = f.rotate(90)
        assert r.width == 6
        assert r.height == 10


# ---------------------------------------------------------------------------
# trim / crop_even
# ---------------------------------------------------------------------------

class TestTrim:
    def test_trim_reduces_size(self):
        f = solid_frame(10, 10)
        t = f.trim(left=1, upper=1, right=1, lower=1)
        assert t.width == 8
        assert t.height == 8

    def test_trim_only_right(self):
        f = solid_frame(10, 10)
        t = f.trim(right=3)
        assert t.width == 7

    def test_crop_even(self):
        f = solid_frame(10, 10)
        c = f.crop_even(horizontal=2, vertical=2)
        assert c.width == 6
        assert c.height == 6


# ---------------------------------------------------------------------------
# rescale
# ---------------------------------------------------------------------------

class TestRescale:
    def test_scale_by_two(self):
        f = solid_frame(10, 10)
        r = f.rescale(2.0)
        assert r.width == 20
        assert r.height == 20

    def test_scale_by_half(self):
        f = solid_frame(10, 10)
        r = f.rescale(0.5)
        assert r.width == 5
        assert r.height == 5

    def test_independent_xy_scale(self):
        f = solid_frame(10, 10)
        r = f.rescale((2.0, 0.5))
        assert r.width == 20
        assert r.height == 5


# ---------------------------------------------------------------------------
# opacity
# ---------------------------------------------------------------------------

class TestOpacity:
    def test_zero_opacity_fully_transparent(self):
        f = solid_frame(4, 4, color=(255, 0, 0, 255))
        r = f.opacity(0.0)
        px = r.image.getpixel((0, 0))
        assert px[3] == 0

    def test_full_opacity_preserves_alpha(self):
        f = solid_frame(4, 4, color=(255, 0, 0, 255))
        r = f.opacity(1.0)
        px = r.image.getpixel((0, 0))
        assert px[3] == 255


# ---------------------------------------------------------------------------
# brightness / contrast
# ---------------------------------------------------------------------------

class TestBrightness:
    def test_double_brightness_increases_value(self):
        f = solid_frame(4, 4, color=(100, 100, 100, 255))
        b = f.brightness(2.0)
        px = b.image.getpixel((0, 0))
        assert px[0] > 100

    def test_zero_brightness_black(self):
        f = solid_frame(4, 4, color=(200, 200, 200, 255))
        b = f.brightness(0.0)
        px = b.image.getpixel((0, 0))
        assert px[0] == 0


class TestContrast:
    def test_returns_frame(self):
        f = solid_frame()
        assert isinstance(f.contrast(1.5), Frame)


# ---------------------------------------------------------------------------
# tag / hash / eq
# ---------------------------------------------------------------------------

class TestHashAndEquality:
    def test_same_image_equal(self):
        img = Image.new('RGBA', (4, 4), (1, 2, 3, 4))
        f1 = Frame(img)
        f2 = Frame(img)
        assert f1 == f2

    def test_different_images_not_equal(self):
        f1 = solid_frame(4, 4, color=(255, 0, 0, 255))
        f2 = solid_frame(4, 4, color=(0, 255, 0, 255))
        assert f1 != f2

    def test_tag_overrides_hash(self):
        f = solid_frame()
        f.tag('my-tag')
        # Frame.__hash__ returns hash(self.hash[1]) when tagged
        assert hash(f) == hash('my-tag')

    def test_repr_contains_hash(self):
        f = Frame(Image.new('RGBA', (2, 2)), hash='repr-test')
        assert 'repr-test' in repr(f)
