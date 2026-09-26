from __future__ import annotations

import base64
import io
import math
from pathlib import Path

from PIL import Image, ImageOps

# Claude's server-side image limits. Images larger than these are downscaled
# by the API before tokenization, so they cap what an image can cost.
#   standard: Haiku 4.5 (and Sonnet/Opus 4.6 and earlier) - 1568 px long edge
#   high_res: Sonnet 5, Opus 4.7+ - 2576 px long edge
IMAGE_LIMITS = {
    "standard": {"max_long_edge": 1568, "max_tokens": 1568},
    "high_res": {"max_long_edge": 2576, "max_tokens": 4784},
}
PIXELS_PER_TOKEN = 750


def preprocess_image(
    source: str | bytes | Path,
    max_size: int = 768,
    quality: int = 75,
    output_format: str = "JPEG",
) -> tuple[str, dict]:
    """Resize and compress an image for moderation, returning base64 and metadata.

    Applies EXIF orientation, flattens transparency onto white, downsizes so
    the long edge is <= max_size, and re-encodes (which also drops EXIF).

    Returns:
        (base64_string, metadata_dict) where metadata includes original and
        final dimensions, byte sizes, and estimated image token counts
        (`estimated_tokens` for the processed image, `estimated_tokens_original`
        for sending the original as-is, both on a standard-limit model).
    """
    opened = Image.open(source if isinstance(source, (str, Path)) else io.BytesIO(source))
    with opened:
        original_mode = opened.mode
        img = ImageOps.exif_transpose(opened)
        original_size = img.size

        if _has_alpha(img):
            rgba = img.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.getchannel("A"))
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail((max_size, max_size), Image.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format=output_format, quality=quality, optimize=True)
    compressed_bytes = buffer.getvalue()

    b64 = base64.standard_b64encode(compressed_bytes).decode("utf-8")

    w, h = img.size
    metadata = {
        "original_size": original_size,
        "original_mode": original_mode,
        "final_size": (w, h),
        "bytes_original": _get_original_bytes(source),
        "bytes_compressed": len(compressed_bytes),
        "estimated_tokens": estimate_image_tokens(w, h),
        "estimated_tokens_original": estimate_image_tokens(*original_size),
    }

    return b64, metadata


def estimate_image_tokens(width: int, height: int, tier: str = "standard") -> int:
    """Estimate image input tokens: (width * height) / 750, after applying the
    downscale the API itself performs for images over the model's limits.

    tier: "standard" (Haiku 4.5) or "high_res" (Sonnet 5).
    """
    limits = IMAGE_LIMITS[tier]
    long_edge = max(width, height)
    if long_edge > limits["max_long_edge"]:
        scale = limits["max_long_edge"] / long_edge
        width, height = width * scale, height * scale
    tokens = math.ceil(width * height / PIXELS_PER_TOKEN)
    return min(tokens, limits["max_tokens"])


# Backwards-compatible private alias.
_estimate_image_tokens = estimate_image_tokens


def _has_alpha(img: Image.Image) -> bool:
    return img.mode in ("RGBA", "LA", "PA", "RGBa", "La") or (
        img.mode == "P" and "transparency" in img.info
    )


def _get_original_bytes(source: str | bytes | Path) -> int:
    if isinstance(source, bytes):
        return len(source)
    if isinstance(source, (str, Path)):
        return Path(source).stat().st_size
    return 0
