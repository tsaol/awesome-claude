import base64
import io
from pathlib import Path

from PIL import Image


def preprocess_image(
    source: str | bytes | Path,
    max_size: int = 768,
    quality: int = 75,
    output_format: str = "JPEG",
) -> tuple[str, dict]:
    """Resize and compress an image for moderation, returning base64 and metadata.

    Returns:
        (base64_string, metadata_dict) where metadata includes original and
        final dimensions, compression ratio, and estimated token count.
    """
    if isinstance(source, (str, Path)):
        img = Image.open(source)
    else:
        img = Image.open(io.BytesIO(source))

    original_size = img.size
    original_mode = img.mode

    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img.thumbnail((max_size, max_size), Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format=output_format, quality=quality, optimize=True)
    compressed_bytes = buffer.getvalue()

    b64 = base64.standard_b64encode(compressed_bytes).decode("utf-8")

    w, h = img.size
    estimated_tokens = _estimate_image_tokens(w, h)

    metadata = {
        "original_size": original_size,
        "original_mode": original_mode,
        "final_size": (w, h),
        "bytes_original": _get_original_bytes(source),
        "bytes_compressed": len(compressed_bytes),
        "estimated_tokens": estimated_tokens,
    }

    return b64, metadata


def _estimate_image_tokens(width: int, height: int) -> int:
    """Approximate Claude's image token consumption based on resolution."""
    pixels = width * height
    if pixels <= 40_000:
        return 170
    elif pixels <= 160_000:
        return 680
    elif pixels <= 640_000:
        return 1365
    else:
        return int(pixels / 750)


def _get_original_bytes(source: str | bytes | Path) -> int:
    if isinstance(source, bytes):
        return len(source)
    if isinstance(source, (str, Path)):
        return Path(source).stat().st_size
    return 0
