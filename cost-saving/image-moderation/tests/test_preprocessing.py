import base64
import io

import pytest
from PIL import Image

from image_moderation.preprocessing import estimate_image_tokens, preprocess_image


def decode(b64):
    return Image.open(io.BytesIO(base64.b64decode(b64)))


def encode(img, fmt, **kw):
    buf = io.BytesIO()
    img.save(buf, fmt, **kw)
    return buf.getvalue()


@pytest.mark.parametrize("mode", ["RGBA", "LA"])
def test_transparent_composites_on_white(mode):
    img = Image.new(mode, (100, 100), (0, 0) if mode == "LA" else (0, 0, 0, 0))
    b64, meta = preprocess_image(encode(img, "PNG"))
    px = decode(b64).convert("RGB").getpixel((50, 50))
    assert all(c > 245 for c in px), px
    assert meta["original_mode"] == mode


def test_palette_with_transparency_on_white():
    img = Image.new("P", (50, 50), 0)
    img.putpalette([0, 0, 0] * 256)
    b64, _ = preprocess_image(encode(img, "PNG", transparency=0))
    assert all(c > 245 for c in decode(b64).convert("RGB").getpixel((25, 25)))


def test_exif_orientation_applied():
    img = Image.new("RGB", (400, 200), (200, 0, 0))
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 CW on display
    b64, meta = preprocess_image(encode(img, "JPEG", exif=exif), max_size=768)
    assert meta["original_size"] == (200, 400)
    assert decode(b64).size == (200, 400)
    assert 0x0112 not in decode(b64).getexif()


def test_resize_and_meta(tmp_path):
    p = tmp_path / "big.png"
    Image.new("RGB", (3840, 2160), (1, 2, 3)).save(p)
    b64, meta = preprocess_image(p, max_size=768)
    assert meta["final_size"] == (768, 432)
    assert meta["estimated_tokens"] == 443  # ceil(768*432/750)
    assert meta["bytes_original"] == p.stat().st_size


def test_token_formula():
    assert estimate_image_tokens(750, 1) == 1
    assert estimate_image_tokens(768, 768) == 787
    assert estimate_image_tokens(1000, 1000) == 1334
    # API downscales to the model's long-edge limit before tokenizing, then caps
    assert estimate_image_tokens(3840, 2160) == 1568
    assert estimate_image_tokens(3840, 2160, tier="high_res") == 4784
    assert estimate_image_tokens(1568, 400) == 837
