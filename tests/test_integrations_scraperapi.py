import yaml

from src.integrations.scraperapi import ScraperAPIClient, ScraperAPISettings
from src.resource_manager.proxy_pool import ProxyPool


def test_scraperapi_client_builds_urls_and_proxies():
    settings = ScraperAPISettings(
        api_key="key123",
        default_params={"render": "true"},
    )
    client = ScraperAPIClient(settings)

    request_url = client.build_request_url("https://example.com/product", params={"country_code": "us"})
    assert "api_key=key123" in request_url
    assert "render=true" in request_url
    assert "%2F%2Fexample.com%2Fproduct" in request_url

    proxy = client.build_proxy_string(session_id="sess-1", country="ca")
    assert proxy.startswith("http://scraperapi:key123")
    assert "session_number" in proxy


def test_proxy_pool_uses_scraperapi_blueprint(tmp_path, monkeypatch):
    monkeypatch.setenv("SCRAPERAPI_API_KEY", "demo-key")
    blueprint = {
        "default_pool": {
            "providers": [
                {
                    "name": "global-scraperapi",
                    "type": "scraperapi",
                    "sticky_sessions": True,
                    "session_prefix": "test",
                    "session_pool_size": 2,
                }
            ]
        }
    }
    path = tmp_path / "proxies.yaml"
    path.write_text(yaml.safe_dump(blueprint), encoding="utf-8")

    pool = ProxyPool({}, blueprint_path=path)
    proxy = pool.choose_proxy("any-source")
    assert proxy
    assert proxy.startswith("http://scraperapi:demo-key")

