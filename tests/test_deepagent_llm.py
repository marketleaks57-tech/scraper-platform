"""
Tests for DeepAgent LLM features: auto-selector, auto-repair, patch generation.

These tests validate the LLM-powered auto-repair capabilities.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.agents.llm_selector_engine import (
    extract_selectors_with_llm,
    extract_fields_with_llm,
    auto_extract_with_llm,
)
from src.agents.llm_patch_generator import (
    generate_selector_patch_with_llm,
    generate_code_patch_with_llm,
    PatchProposal,
)
from src.agents.deepagent_repair_engine import run_repair_session, PatchResult
from src.processors.llm.llm_client import LLMClient


class TestLLMSelectorEngine:
    """Tests for LLM-based selector extraction."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing."""
        client = Mock(spec=LLMClient)
        return client

    @pytest.fixture
    def sample_html(self):
        """Sample HTML for testing."""
        return """
        <html>
            <body>
                <div class="product">
                    <h1 class="product-name">Test Product</h1>
                    <span class="price">$99.99</span>
                    <div class="description">Test description</div>
                </div>
            </body>
        </html>
        """

    def test_extract_selectors_with_llm_success(self, mock_llm_client, sample_html):
        """Test successful selector extraction."""
        expected_selectors = {
            "name": "h1.product-name",
            "price": "span.price",
            "description": "div.description",
        }
        mock_llm_client.extract_json.return_value = expected_selectors

        result = extract_selectors_with_llm(
            sample_html,
            fields=["name", "price", "description"],
            llm_client=mock_llm_client,
        )

        assert result == expected_selectors
        mock_llm_client.extract_json.assert_called_once()

    def test_extract_selectors_with_llm_failure(self, mock_llm_client, sample_html):
        """Test selector extraction failure handling."""
        mock_llm_client.extract_json.side_effect = Exception("LLM error")

        result = extract_selectors_with_llm(
            sample_html,
            fields=["name", "price"],
            llm_client=mock_llm_client,
        )

        assert result == {}

    def test_extract_selectors_with_existing_hints(self, mock_llm_client, sample_html):
        """Test selector extraction with existing selectors as hints."""
        existing = {"name": "h1.old-name"}  # Broken selector
        expected = {"name": "h1.product-name", "price": "span.price"}
        mock_llm_client.extract_json.return_value = expected

        result = extract_selectors_with_llm(
            sample_html,
            fields=["name", "price"],
            llm_client=mock_llm_client,
            existing_selectors=existing,
        )

        assert result == expected
        # Verify existing selectors were included in prompt
        call_args = mock_llm_client.extract_json.call_args
        assert "old-name" in str(call_args)

    def test_extract_fields_with_llm_direct(self, mock_llm_client, sample_html):
        """Test direct field extraction without selectors."""
        expected_fields = {
            "name": "Test Product",
            "price": "$99.99",
            "description": "Test description",
        }
        mock_llm_client.extract_json.return_value = expected_fields

        result = extract_fields_with_llm(
            sample_html,
            fields=["name", "price", "description"],
            llm_client=mock_llm_client,
        )

        assert result == expected_fields


class TestLLMPatchGenerator:
    """Tests for LLM-based patch generation."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing."""
        return Mock(spec=LLMClient)

    @pytest.fixture
    def sample_html_old(self):
        """Old HTML snapshot."""
        return '<div class="product"><h1>Old Product</h1></div>'

    @pytest.fixture
    def sample_html_new(self):
        """New HTML snapshot (structure changed)."""
        return '<div class="item"><h2>New Product</h2></div>'

    def test_generate_selector_patch_success(self, mock_llm_client, sample_html_old, sample_html_new):
        """Test successful selector patch generation."""
        old_selectors = {"name": "h1"}
        expected_new = {"name": "h2.item"}
        
        # Mock the repair function
        with patch("src.agents.llm_patch_generator.repair_selectors_with_llm") as mock_repair:
            mock_repair.return_value = expected_new
            
            result = generate_selector_patch_with_llm(
                sample_html_old,
                sample_html_new,
                old_selectors,
                "Selector not found",
                mock_llm_client,
            )

            assert result == expected_new
            mock_repair.assert_called_once()

    def test_generate_code_patch_success(self, mock_llm_client):
        """Test successful code patch generation."""
        current_code = "def extract_item(driver, url):\n    return {}"
        error_message = "KeyError: 'name'"
        context = {"html": "<div>test</div>"}
        
        expected_patch = {
            "file_path": "pipeline.py",
            "old_code": current_code,
            "new_code": "def extract_item(driver, url):\n    return {'name': 'test'}",
            "description": "Fix missing name field",
            "confidence": 0.85,
            "affected_lines": [1, 2],
        }
        mock_llm_client.extract_json.return_value = expected_patch

        result = generate_code_patch_with_llm(
            "pipeline.py",
            current_code,
            error_message,
            context,
            mock_llm_client,
        )

        assert result is not None
        assert isinstance(result, PatchProposal)
        assert result.file_path == "pipeline.py"
        assert result.description == "Fix missing name field"

    def test_generate_code_patch_failure(self, mock_llm_client):
        """Test code patch generation failure."""
        mock_llm_client.extract_json.side_effect = Exception("LLM error")

        result = generate_code_patch_with_llm(
            "pipeline.py",
            "def test(): pass",
            "Error",
            {},
            mock_llm_client,
        )

        assert result is None


class TestDeepAgentRepairEngine:
    """Tests for DeepAgent repair engine integration."""

    @pytest.fixture
    def temp_snapshots_dir(self, tmp_path):
        """Create temporary snapshots directory."""
        snapshots_dir = tmp_path / "snapshots" / "test_source"
        snapshots_dir.mkdir(parents=True)
        return snapshots_dir

    @pytest.fixture
    def sample_selectors(self, tmp_path):
        """Create sample selectors file."""
        selectors_path = tmp_path / "selectors.json"
        selectors = {
            "product_name_selector": "h1.product-name",
            "price_selector": "span.price",
        }
        selectors_path.write_text(json.dumps(selectors))
        return selectors_path

    def test_run_repair_session_no_snapshots(self, tmp_path):
        """Test repair session with no snapshots."""
        results = run_repair_session("nonexistent_source", selectors_path=tmp_path / "selectors.json")
        assert results == []

    def test_run_repair_session_insufficient_snapshots(self, temp_snapshots_dir, sample_selectors):
        """Test repair session with insufficient snapshots."""
        # Create only one snapshot
        (temp_snapshots_dir / "snapshot1.html").write_text("<div>test</div>")
        
        results = run_repair_session(
            "test_source",
            selectors_path=sample_selectors,
        )
        assert results == []

    @patch("src.agents.deepagent_repair_engine.load_source_config")
    @patch("src.agents.deepagent_repair_engine.generate_repair_patches")
    def test_run_repair_session_with_llm(
        self,
        mock_generate_patches,
        mock_load_config,
        temp_snapshots_dir,
        sample_selectors,
        tmp_path,
    ):
        """Test repair session with LLM enabled."""
        # Create two snapshots
        (temp_snapshots_dir / "snapshot1.html").write_text("<div><h1>Old</h1></div>")
        (temp_snapshots_dir / "snapshot2.html").write_text("<div><h2>New</h2></div>")
        
        # Mock config
        mock_load_config.return_value = {
            "llm": {"enabled": True},
        }
        
        # Mock LLM patch
        mock_patch = Mock()
        mock_patch.file_path = str(sample_selectors)
        mock_patch.new_code = json.dumps({"product_name_selector": "h2"})
        mock_generate_patches.return_value = [mock_patch]
        
        # Mock REPLAY_SNAPSHOTS_DIR
        with patch("src.agents.deepagent_repair_engine.REPLAY_SNAPSHOTS_DIR", tmp_path / "snapshots"):
            results = run_repair_session(
                "test_source",
                selectors_path=sample_selectors,
                use_llm=True,
            )
        
        # Should attempt LLM repair
        assert mock_generate_patches.called

    def test_patch_result_dataclass(self):
        """Test PatchResult dataclass."""
        result = PatchResult(
            source="test",
            field="name",
            applied=True,
            reason="Selector updated",
        )
        assert result.source == "test"
        assert result.field == "name"
        assert result.applied is True
        assert result.reason == "Selector updated"


class TestAutoExtractIntegration:
    """Integration tests for auto-extract feature."""

    @patch("src.agents.llm_selector_engine.get_llm_client_from_config")
    @patch("src.agents.llm_selector_engine.load_source_config")
    def test_auto_extract_with_llm_integration(self, mock_load_config, mock_get_client):
        """Test full auto-extract integration."""
        # Mock config
        mock_load_config.return_value = {
            "llm": {"enabled": True, "provider": "openai"},
        }
        
        # Mock LLM client
        mock_client = Mock(spec=LLMClient)
        mock_client.extract_json.return_value = {
            "name": "Test Product",
            "price": "$99.99",
        }
        mock_get_client.return_value = mock_client
        
        html = "<div><h1>Test Product</h1><span>$99.99</span></div>"
        source_config = {"llm": {"enabled": True}}
        
        result = auto_extract_with_llm(html, source_config, fields=["name", "price"])
        
        assert "name" in result
        assert "price" in result
        assert result["name"] == "Test Product"

