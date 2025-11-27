"""
Tests for domain-specific QC validators.
"""

import pytest
from src.processors.qc.domain_validators import (
    validate_alfabeta,
    validate_quebec,
    validate_lafa,
    validate_template,
    validate_by_domain,
    get_domain_requirements,
)


class TestAlfabetaValidator:
    """Tests for Alfabeta domain validator."""

    def test_valid_alfabeta_record(self):
        """Test valid Alfabeta record."""
        record = {
            "name": "Test Product",
            "price": 99.99,
            "company": "Test Company",
            "source": "alfabeta",
        }
        assert validate_alfabeta(record) is True

    def test_missing_name(self):
        """Test record missing name."""
        record = {"price": 99.99, "source": "alfabeta"}
        assert validate_alfabeta(record) is False

    def test_invalid_price(self):
        """Test record with invalid price."""
        record = {"name": "Test", "price": -10, "source": "alfabeta"}
        assert validate_alfabeta(record) is False

    def test_missing_company_warning(self):
        """Test record missing company (should still pass but log warning)."""
        record = {"name": "Test", "price": 99.99, "source": "alfabeta"}
        # Should pass but log warning
        assert validate_alfabeta(record) is True


class TestQuebecValidator:
    """Tests for Quebec domain validator."""

    def test_valid_quebec_record(self):
        """Test valid Quebec record."""
        record = {"name": "Test", "price": 50.0, "currency": "CAD", "source": "quebec"}
        assert validate_quebec(record) is True

    def test_missing_required_fields(self):
        """Test record missing required fields."""
        record = {"price": 50.0, "source": "quebec"}
        assert validate_quebec(record) is False


class TestLafaValidator:
    """Tests for Lafa domain validator."""

    def test_valid_lafa_record(self):
        """Test valid Lafa record."""
        record = {
            "name": "Test",
            "price": 75.0,
            "product_url": "https://example.com/product",
            "source": "lafa",
        }
        assert validate_lafa(record) is True

    def test_missing_url(self):
        """Test record missing URL (required for Lafa)."""
        record = {"name": "Test", "price": 75.0, "source": "lafa"}
        assert validate_lafa(record) is False


class TestTemplateValidator:
    """Tests for template/default validator."""

    def test_valid_template_record(self):
        """Test valid template record."""
        record = {"name": "Test", "price": 100.0, "source": "unknown"}
        assert validate_template(record) is True

    def test_invalid_template_record(self):
        """Test invalid template record."""
        record = {"price": 100.0, "source": "unknown"}
        assert validate_template(record) is False


class TestDomainValidation:
    """Tests for domain validation routing."""

    def test_validate_by_domain_alfabeta(self):
        """Test domain validation for Alfabeta."""
        record = {"name": "Test", "price": 99.99, "source": "alfabeta"}
        assert validate_by_domain(record, "alfabeta") is True

    def test_validate_by_domain_unknown(self):
        """Test domain validation for unknown source (uses template)."""
        record = {"name": "Test", "price": 99.99, "source": "unknown"}
        assert validate_by_domain(record, "unknown") is True

    def test_validate_by_domain_extracts_source(self):
        """Test that source is extracted from record if not provided."""
        record = {"name": "Test", "price": 99.99, "source": "quebec"}
        assert validate_by_domain(record) is True


class TestDomainRequirements:
    """Tests for domain requirements API."""

    def test_get_alfabeta_requirements(self):
        """Test getting Alfabeta requirements."""
        reqs = get_domain_requirements("alfabeta")
        assert "required_fields" in reqs
        assert "name" in reqs["required_fields"]
        assert "price" in reqs["required_fields"]

    def test_get_unknown_requirements(self):
        """Test getting requirements for unknown source (returns template)."""
        reqs = get_domain_requirements("unknown_source")
        assert "required_fields" in reqs
        assert "name" in reqs["required_fields"]

