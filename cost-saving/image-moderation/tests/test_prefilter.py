import io

import pytest
from PIL import Image, ImageDraw

from image_moderation.models import ModerationCategory
from image_moderation.prefilter import PHashFilter


@pytest.fixture
def img_bytes():
    img = Image.new("RGB", (64, 64), "white")
    ImageDraw.Draw(img).rectangle([10, 10, 40, 50], fill="black")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def test_bad_csv_rows_skipped_with_warning(tmp_path, img_bytes):
    good = PHashFilter.compute_hash(img_bytes)
    db = tmp_path / "db.csv"
    db.write_text(
        "hash,category\n"          # header
        f"{good},violence\n"
        "\n"
        "zzzzzzzzzzzzzzzz,spam\n"  # bad hex
        "abcd,spam\n"              # wrong length
        f"{good},not_a_category\n"
        "only_one_column\n"
        "a,b,c\n"
    )
    with pytest.warns(UserWarning) as rec:
        f = PHashFilter(db)
    assert len(rec) == 6
    r = f.check(img_bytes)
    assert r is not None and r.category == ModerationCategory.VIOLENCE


def test_result_types_are_python_natives(tmp_path, img_bytes):
    path = tmp_path / "x.png"
    path.write_bytes(img_bytes)
    f = PHashFilter()
    f.add_hash(f.compute_hash(path), ModerationCategory.SPAM)
    r = f.check(path)
    assert type(r.details["distance"]) is int and r.details["distance"] == 0
    assert type(r.confidence) is float and r.confidence == 1.0


def test_no_match_and_roundtrip(tmp_path, img_bytes):
    f = PHashFilter()
    f.add_hash("ffffffffffffffff", ModerationCategory.SPAM)
    assert f.check(img_bytes) is None
    f.save_db(tmp_path / "out.csv")
    assert PHashFilter(tmp_path / "out.csv")._known_hashes == f._known_hashes
    with pytest.raises(ValueError):
        f.add_hash("nothex", ModerationCategory.SPAM)
