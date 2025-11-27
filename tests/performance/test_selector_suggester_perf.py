from src.ml.selector_suggester import SelectorSuggester


def test_selector_suggester_best_selector_under_load():
    suggester = SelectorSuggester()
    for _ in range(1000):
        suggester.record_result(".title", True)
        suggester.record_result(".price", False)
    assert suggester.best_selector() == ".title"

