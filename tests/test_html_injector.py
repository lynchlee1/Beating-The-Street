"""Unit tests for src/builder/html_injector.py."""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.builder.html_injector import generate_static_html


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def template_file(tmp_path):
    """Minimal HTML template written to a temporary file."""
    template = tmp_path / "index.html"
    template.write_text(
        "<!DOCTYPE html><html><head><title>Test</title></head>"
        "<body><div id='root'></div></body></html>",
        encoding="utf-8",
    )
    return template


@pytest.fixture()
def sample_payload():
    return {
        "ticker": "TEST",
        "generatedAt": "2024-01-01T00:00:00Z",
        "chartData": [{"date": "2024-03-31", "revenue": 1_000_000}],
        "availableMetrics": [],
        "averages": {},
        "growth": {},
        "valuation": {"currentMarketCap": 1e9},
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestGenerateStaticHTML:
    def test_creates_output_file(self, template_file, sample_payload, tmp_path):
        out = tmp_path / "report.html"
        result = generate_static_html(sample_payload, output_path=out, template_path=template_file)
        assert result.exists()

    def test_returns_path_object(self, template_file, sample_payload, tmp_path):
        out = tmp_path / "report.html"
        result = generate_static_html(sample_payload, output_path=out, template_path=template_file)
        assert isinstance(result, Path)

    def test_injects_window_var(self, template_file, sample_payload, tmp_path):
        out = tmp_path / "report.html"
        generate_static_html(sample_payload, output_path=out, template_path=template_file)
        content = out.read_text(encoding="utf-8")
        assert "window.__INITIAL_DATA__" in content

    def test_injected_json_is_valid(self, template_file, sample_payload, tmp_path):
        out = tmp_path / "report.html"
        generate_static_html(sample_payload, output_path=out, template_path=template_file)
        content = out.read_text(encoding="utf-8")

        # Extract JSON from the injected script tag
        start_marker = "window.__INITIAL_DATA__ = "
        end_marker = ";</script>"
        start = content.index(start_marker) + len(start_marker)
        end = content.index(end_marker, start)
        json_str = content[start:end]

        recovered = json.loads(json_str)
        assert recovered["ticker"] == "TEST"

    def test_injection_before_head_close(self, template_file, sample_payload, tmp_path):
        out = tmp_path / "report.html"
        generate_static_html(sample_payload, output_path=out, template_path=template_file)
        content = out.read_text(encoding="utf-8")
        injection_pos = content.index("window.__INITIAL_DATA__")
        head_close_pos = content.index("</head>")
        assert injection_pos < head_close_pos

    def test_missing_template_raises(self, sample_payload, tmp_path):
        non_existent = tmp_path / "does_not_exist.html"
        with pytest.raises(FileNotFoundError):
            generate_static_html(sample_payload, output_path=tmp_path / "out.html",
                                  template_path=non_existent)

    def test_creates_parent_directories(self, template_file, sample_payload, tmp_path):
        deep_out = tmp_path / "a" / "b" / "c" / "report.html"
        generate_static_html(sample_payload, output_path=deep_out, template_path=template_file)
        assert deep_out.exists()

    def test_unicode_data_preserved(self, template_file, tmp_path):
        payload = {"ticker": "テスト", "name": "회사 이름"}
        out = tmp_path / "report.html"
        generate_static_html(payload, output_path=out, template_path=template_file)
        content = out.read_text(encoding="utf-8")
        assert "テスト" in content
        assert "회사 이름" in content

    def test_template_without_head_tag(self, tmp_path, sample_payload):
        """Fallback: prepend injection when there's no </head> tag."""
        template = tmp_path / "bare.html"
        template.write_text("<html><body>bare</body></html>", encoding="utf-8")
        out = tmp_path / "out.html"
        generate_static_html(sample_payload, output_path=out, template_path=template)
        content = out.read_text(encoding="utf-8")
        assert "window.__INITIAL_DATA__" in content
        # Should be at the very start (fallback prepend)
        assert content.index("window.__INITIAL_DATA__") < content.index("<html>")

    def test_large_payload(self, template_file, tmp_path):
        """Ensure large datasets (80 quarters × many metrics) are handled."""
        from tests.fixtures.sample_raw import build_sample_raw
        from src.parser.calculator import build_parsed_data
        raw = build_sample_raw()
        parsed = build_parsed_data(raw)
        out = tmp_path / "large.html"
        result = generate_static_html(parsed, output_path=out, template_path=template_file)
        # Output should be non-trivial in size
        assert result.stat().st_size > 10_000
