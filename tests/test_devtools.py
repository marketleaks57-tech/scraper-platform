import asyncio
from pathlib import Path

from src.devtools import BrowserReplayer, HistoryEvent, HistoryReplay, ScreenshotDiff


def test_history_replay_search_and_render():
    events = [HistoryEvent("load", "page"), HistoryEvent("click", "button A")]
    replay = HistoryReplay(events)
    trace = replay.render_trace()
    assert "[load] page" in trace
    assert replay.search("button") == [events[1]]


def test_screenshot_diff_hash(tmp_path: Path):
    baseline = tmp_path / "a.txt"
    candidate = tmp_path / "b.txt"
    baseline.write_text("one", encoding="utf-8")
    candidate.write_text("two", encoding="utf-8")

    diff = ScreenshotDiff(baseline, candidate).compare()
    assert diff.changed is True
    assert diff.details in {"hash-compare", "pixel-compare"}


def test_browser_replay_counts_without_playwright(tmp_path: Path):
    har = tmp_path / "session.har"
    har.write_text(
        '{"log": {"entries": [{"request": {"url": "http://example.com"}}]}}',
        encoding="utf-8",
    )
    replayer = BrowserReplayer(har)
    count = asyncio.run(replayer.replay())
    assert count == 1
