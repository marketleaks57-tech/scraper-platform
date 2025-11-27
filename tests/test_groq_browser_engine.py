from dataclasses import dataclass, field

from src.engines.groq_browser import GroqBrowserAutomationClient


@dataclass
class _DummyMessage:
    content: str = "Done"
    executed_tools: list = field(
        default_factory=lambda: [
            {"name": "browser_automation", "status": "success", "output": {"summary": "navigated"}}
        ]
    )


@dataclass
class _DummyChoice:
    message: _DummyMessage = field(default_factory=_DummyMessage)


class _DummyResponse:
    def __init__(self):
        self.choices = [_DummyChoice()]
        self.usage = {"prompt_tokens": 12, "completion_tokens": 6}

    def to_dict(self):
        return {"choices": ["omitted"], "usage": self.usage}


class _DummyChat:
    class _DummyCompletions:
        @staticmethod
        def create(**_kwargs):
            return _DummyResponse()

    def __init__(self):
        self.completions = self._DummyCompletions()


class _DummyGroqClient:
    def __init__(self):
        self.chat = _DummyChat()


def test_groq_browser_client_returns_structured_result():
    client = GroqBrowserAutomationClient(groq_client=_DummyGroqClient())
    result = client.run_workflow("Open https://example.com and summarize the hero headline.")

    assert result.content == "Done"
    assert result.executed_tools[0]["name"] == "browser_automation"
    assert result.usage["prompt_tokens"] == 12

