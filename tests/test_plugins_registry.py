from src.plugins import bootstrap_builtin_plugins
from src.scrapers.template.pipeline import run_template
from src.engines.playwright_engine import goto_with_retry


def test_bootstrap_registry_loads_plugins():
    registry = bootstrap_builtin_plugins()

    template_plugin = registry.get("scraper.template.pipeline")
    assert template_plugin is not None
    assert template_plugin.type == "scraper"

    loader = registry.load("scraper.template.pipeline")
    assert loader is run_template

    engines = registry.by_type("engine")
    assert "engine.playwright.goto_with_retry" in engines
    assert registry.load("engine.playwright.goto_with_retry") is goto_with_retry


def test_missing_plugin_raises_key_error():
    registry = bootstrap_builtin_plugins()
    try:
        registry.load("missing.plugin")
        assert False, "expected KeyError"
    except KeyError:
        assert True
