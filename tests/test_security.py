import json
from pathlib import Path

from src.security import PolicyGuard, VaultClient


def test_policy_guard(tmp_path: Path):
    base = tmp_path
    policy_dir = base / "vault_policies"
    policy_dir.mkdir()
    policy = {"capabilities": ["read", "write"]}
    (policy_dir / "scraper.json").write_text(json.dumps(policy), encoding="utf-8")

    vault = VaultClient(base_dir=base)
    guard = PolicyGuard(vault)

    decision = guard.check("scraper", ["read"])
    assert decision.allowed

    decision_missing = guard.check("scraper", ["delete"])
    assert not decision_missing.allowed
    assert decision_missing.missing == {"delete"}

    vault.assert_allowed("scraper", "read")


def test_read_secret_prefers_env(monkeypatch, tmp_path: Path):
    base = tmp_path
    (base / "values").mkdir()
    (base / "values" / "TOKEN").write_text("file-token", encoding="utf-8")

    monkeypatch.setenv("TOKEN", "env-token")

    vault = VaultClient(base_dir=base)
    assert vault.read_secret("TOKEN") == "env-token"
    # cached value should be returned even if env is cleared
    monkeypatch.delenv("TOKEN")
    assert vault.read_secret("TOKEN") == "env-token"
