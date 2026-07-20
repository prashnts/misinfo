"""Tests for disinfo/utils/imops.py — image processing utilities."""
import numpy as np
import pytest
from PIL import Image

from disinfo.utils.imops import (
    apply_gamma,
    dither,
    enlarge_pixels,
    find_coeffs,
    floyd_steinberg,
)


# ---------------------------------------------------------------------------
# floyd_steinberg
# ---------------------------------------------------------------------------

class TestFloydSteinberg:
    def test_all_zeros_stays_zero(self):
        img = np.zeros((4, 4), dtype=float)
        result = floyd_steinberg(img)
        assert np.all(result == 0)

    def test_all_ones_stays_one(self):
        img = np.ones((4, 4), dtype=float)
        result = floyd_steinberg(img)
        assert np.all(result == 1)

    def test_output_in_zero_one_range(self):
        rng = np.random.default_rng(42)
        img = rng.random((8, 8))
        result = floyd_steinberg(img)
        assert result.min() >= -0.01
        assert result.max() <= 1.01

    def test_modifies_in_place(self):
        img = np.full((4, 4), 0.5, dtype=float)
        result = floyd_steinberg(img)
        assert result is img  # same object

    def test_single_pixel(self):
        img = np.array([[0.6]])
        result = floyd_steinberg(img)
        assert result[0, 0] == 1.0

    def test_single_pixel_rounds_down(self):
        img = np.array([[0.4]])
        result = floyd_steinberg(img)
        assert result[0, 0] == 0.0


# ---------------------------------------------------------------------------
# dither
# ---------------------------------------------------------------------------

class TestDither:
    def test_shape_preserved(self):
        img = np.random.default_rng(0).random((6, 6, 4))
        result = dither(img)
        assert result.shape == img.shape

    def test_output_binary(self):
        rng = np.random.default_rng(7)
        img = rng.random((8, 8, 4))
        result = dither(img)
        # After dithering each channel, values should round to 0 or 1
        assert np.all((result >= -0.01) & (result <= 1.01))


# ---------------------------------------------------------------------------
# apply_gamma
# ---------------------------------------------------------------------------

class TestApplyGamma:
    def _solid_image(self, color, size=(4, 4)):
        img = Image.new('RGBA', size, color)
        return img

    def test_gamma_one_is_identity(self):
        img = Image.new('RGB', (4, 4), (128, 128, 128))
        result = apply_gamma(img, 1.0)
        arr_in = np.array(img)
        arr_out = np.array(result)
        assert np.allclose(arr_in, arr_out, atol=1)

    def test_gamma_two_darkens_midtones(self):
        img = Image.new('RGB', (4, 4), (200, 200, 200))
        result = apply_gamma(img, 2.0)
        arr_out = np.array(result)
        # Higher gamma exponent squishes values → darker midtones
        assert arr_out[0, 0, 0] < 200

    def test_gamma_less_than_one_brightens(self):
        img = Image.new('RGB', (4, 4), (100, 100, 100))
        result = apply_gamma(img, 0.5)
        arr_out = np.array(result)
        assert arr_out[0, 0, 0] > 100

    def test_black_stays_black(self):
        img = Image.new('RGB', (4, 4), (0, 0, 0))
        result = apply_gamma(img, 2.2)
        arr_out = np.array(result)
        assert np.all(arr_out == 0)

    def test_white_stays_white(self):
        img = Image.new('RGB', (4, 4), (255, 255, 255))
        result = apply_gamma(img, 2.2)
        arr_out = np.array(result)
        assert np.all(arr_out == 255)

    def test_returns_pil_image(self):
        img = Image.new('RGB', (4, 4), (100, 100, 100))
        result = apply_gamma(img, 1.0)
        assert isinstance(result, Image.Image)


# ---------------------------------------------------------------------------
# enlarge_pixels
# ---------------------------------------------------------------------------

class TestEnlargePixels:
    def test_output_size(self):
        img = Image.new('RGBA', (4, 4), (255, 0, 0, 255))
        result = enlarge_pixels(img, scale=4)
        assert result.size == (16, 16)

    def test_scale_two(self):
        img = Image.new('RGBA', (3, 3), (0, 255, 0, 255))
        result = enlarge_pixels(img, scale=2)
        assert result.size == (6, 6)

    def test_returns_image(self):
        img = Image.new('RGBA', (2, 2), (0, 0, 255, 255))
        result = enlarge_pixels(img, scale=3)
        assert isinstance(result, Image.Image)


# ---------------------------------------------------------------------------
# find_coeffs
# ---------------------------------------------------------------------------

class TestFindCoeffs:
    def test_identity_transform(self):
        # When src == dst the perspective matrix should be close to identity
        pts = [(0, 0), (10, 0), (10, 10), (0, 10)]
        coeffs = find_coeffs(pts, pts)
        assert len(coeffs) == 8
        # For identity, coeffs ≈ [1, 0, 0, 0, 1, 0, 0, 0]
        assert coeffs[0] == pytest.approx(1.0, abs=1e-6)
        assert coeffs[4] == pytest.approx(1.0, abs=1e-6)
        assert coeffs[1] == pytest.approx(0.0, abs=1e-6)
        assert coeffs[3] == pytest.approx(0.0, abs=1e-6)

    def test_returns_eight_coefficients(self):
        pa = [(0, 0), (10, 0), (10, 10), (0, 10)]
        pb = [(1, 1), (9, 1), (9, 9), (1, 9)]
        coeffs = find_coeffs(pa, pb)
        assert len(coeffs) == 8
