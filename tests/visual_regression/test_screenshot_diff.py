from pathlib import Path

from src.devtools.screenshot_diff import diff_images


def test_diff_images_handles_missing_files(tmp_path: Path):
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    first.write_bytes(b"fake")
    second.write_bytes(b"fake")

    diff_path, score = diff_images(first, second)
    assert diff_path.exists()
    assert score == 0.0

