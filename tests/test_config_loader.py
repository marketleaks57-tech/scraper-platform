from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common import config_loader


def test_load_config_merges_environment_overrides(tmp_path):
    config_dir = tmp_path / "config"
    env_dir = config_dir / "env"
    env_dir.mkdir(parents=True)

    (config_dir / "settings.yaml").write_text(
        """
app:
  name: test-app
  environment: dev
logging:
  level: INFO
scraping:
  max_retries: 3
""",
        encoding="utf-8",
    )

    (env_dir / "dev.yaml").write_text(
        """
logging:
  level: DEBUG
scraping:
  max_retries: 5
""",
        encoding="utf-8",
    )

    loaded = config_loader.load_config(config_dir=config_dir)
    assert loaded["logging"]["level"] == "DEBUG"
    assert loaded["scraping"]["max_retries"] == 5


def test_missing_required_sections_raises(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "settings.yaml").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        config_loader.load_config(config_dir=config_dir)

    assert "missing required sections" in str(excinfo.value)


def test_missing_required_fields_raises(tmp_path):
    config_dir = tmp_path / "config"
    env_dir = config_dir / "env"
    env_dir.mkdir(parents=True)

    (config_dir / "settings.yaml").write_text(
        """
app:
  name: test-app
  environment: dev
logging: {}
scraping:
  max_retries: 3
""",
        encoding="utf-8",
    )

    (env_dir / "dev.yaml").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        config_loader.load_config(config_dir=config_dir)

    assert "logging.level" in str(excinfo.value)


def test_missing_env_file_is_error(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "settings.yaml").write_text(
        """
app:
  name: test-app
  environment: staging
logging:
  level: INFO
scraping:
  max_retries: 3
""",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError):
        config_loader.load_config(config_dir=config_dir)


def test_explicit_env_argument(tmp_path):
    config_dir = tmp_path / "config"
    env_dir = config_dir / "env"
    env_dir.mkdir(parents=True)

    (config_dir / "settings.yaml").write_text(
        """
app:
  name: test-app
  environment: dev
logging:
  level: INFO
scraping:
  max_retries: 3
""",
        encoding="utf-8",
    )

    (env_dir / "prod.yaml").write_text(
        """
logging:
  level: WARNING
scraping:
  max_retries: 2
""",
        encoding="utf-8",
    )

    loaded = config_loader.load_config(env="prod", config_dir=config_dir)
    assert loaded["logging"]["level"] == "WARNING"
    assert loaded["scraping"]["max_retries"] == 2


def test_env_variable_override(monkeypatch, tmp_path):
    config_dir = tmp_path / "config"
    env_dir = config_dir / "env"
    env_dir.mkdir(parents=True)

    (config_dir / "settings.yaml").write_text(
        """
app:
  name: test-app
  environment: dev
logging:
  level: INFO
scraping:
  max_retries: 3
""",
        encoding="utf-8",
    )

    (env_dir / "staging.yaml").write_text(
        """
logging:
  level: DEBUG
scraping:
  max_retries: 4
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("SCRAPER_PLATFORM_ENV", "staging")
    loaded = config_loader.load_config(config_dir=config_dir)

    assert loaded["logging"]["level"] == "DEBUG"
    assert loaded["scraping"]["max_retries"] == 4


def test_explicit_env_precedes_env_variable(monkeypatch, tmp_path):
    config_dir = tmp_path / "config"
    env_dir = config_dir / "env"
    env_dir.mkdir(parents=True)

    (config_dir / "settings.yaml").write_text(
        """
app:
  name: test-app
  environment: dev
logging:
  level: INFO
scraping:
  max_retries: 3
""",
        encoding="utf-8",
    )

    (env_dir / "prod.yaml").write_text(
        """
logging:
  level: WARNING
scraping:
  max_retries: 2
""",
        encoding="utf-8",
    )

    (env_dir / "dev.yaml").write_text(
        """
logging:
  level: DEBUG
scraping:
  max_retries: 5
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("SCRAPER_PLATFORM_ENV", "dev")
    loaded = config_loader.load_config(env="prod", config_dir=config_dir)

    assert loaded["logging"]["level"] == "WARNING"
    assert loaded["scraping"]["max_retries"] == 2


def test_load_source_config_success(tmp_path):
    config_dir = tmp_path / "config"
    sources_dir = config_dir / "sources"
    sources_dir.mkdir(parents=True)

    (sources_dir / "alfabeta.yaml").write_text(
        """
source: alfabeta
engine: selenium
base_url: https://example.com/companies
""",
        encoding="utf-8",
    )

    cfg = config_loader.load_source_config("alfabeta", config_dir=config_dir)
    assert cfg["engine"] == "selenium"
    assert cfg["source"] == "alfabeta"


def test_load_source_config_missing_fields(tmp_path):
    config_dir = tmp_path / "config"
    sources_dir = config_dir / "sources"
    sources_dir.mkdir(parents=True)

    (sources_dir / "alfabeta.yaml").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        config_loader.load_source_config("alfabeta", config_dir=config_dir)

    assert "missing required fields" in str(excinfo.value)


def test_load_source_config_mismatch(tmp_path):
    config_dir = tmp_path / "config"
    sources_dir = config_dir / "sources"
    sources_dir.mkdir(parents=True)

    (sources_dir / "alfabeta.yaml").write_text(
        """
source: not-alfabeta
engine: selenium
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as excinfo:
        config_loader.load_source_config("alfabeta", config_dir=config_dir)

    assert "expected 'alfabeta'" in str(excinfo.value)


def test_load_source_config_missing_file(tmp_path):
    config_dir = tmp_path / "config"
    with pytest.raises(FileNotFoundError):
        config_loader.load_source_config("alfabeta", config_dir=config_dir)
