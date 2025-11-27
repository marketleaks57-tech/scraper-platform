from __future__ import annotations

from dataclasses import dataclass

from src.agents import AgenticReport, NoOpLLM, run_agentic_check


@dataclass
class EchoLLM(NoOpLLM):
    def generate(self, messages):  # type: ignore[override]
        return ";".join(list(messages))


def test_run_agentic_check_generates_patch_and_llm_summary():
    report: AgenticReport = run_agentic_check(
        "alfabeta",
        selectors_before={"name": "div.old"},
        selectors_after={"name": "div.new"},
        llm=EchoLLM(),
    )

    assert report.selector_diffs
    assert report.proposed_patches["name"].new_selector == "div.new"
    assert report.llm_summary == "name: div.old -> div.new"


def test_run_agentic_check_handles_replay_failures():
    report = run_agentic_check(
        "alfabeta",
        replay_results=[True, False],
    )
    assert not report.replay_ok
    assert any(err.startswith("replay:") for err in report.errors)
