"""
test_ghost_publish.py — Tests for ghost_auto_publish.extract_content()

Covers three cases:
1. Normal HTML with title, tag, body content
2. Empty HTML (minimal valid structure)
3. Malformed/garbage HTML input
"""

import sys
import tempfile
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ghost_auto_publish import extract_content
import pytest


class TestExtractContentNormal:
    """Test extract_content with well-formed HTML input."""

    def test_extracts_title_from_h1(self, tmp_path):
        html = """<!DOCTYPE html>
<html><head><title>Test Post</title></head>
<body>
<h1>My Blog Post Title</h1>
<div class="hero-label">Tech</div>
<p>Hello world content here.</p>
</body></html>"""
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        assert result["title"] == "My Blog Post Title"
        assert result["tag"] == "Tech"
        assert "Hello world content" in result["html"]
        assert isinstance(result["img_data_list"], list)

    def test_extracts_title_from_hero_title_div(self, tmp_path):
        html = """<!DOCTYPE html>
<html><head><title>Fallback</title></head>
<body>
<div class="hero-title">Hero Title Here</div>
<p>Body text.</p>
</body></html>"""
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        assert result["title"] == "Hero Title Here"

    def test_extracts_base64_images(self, tmp_path):
        # Create a fake large base64 image (>50KB to trigger extraction)
        fake_b64 = "data:image/png;base64," + "A" * 60000
        html = f"""<!DOCTYPE html>
<html><head><title>Images</title></head>
<body>
<h1>Post With Image</h1>
<img src="{fake_b64}" alt="test" />
<p>After image.</p>
</body></html>"""
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        assert len(result["img_data_list"]) == 1
        assert "<!-- IMG_PLACEHOLDER -->" in result["html"]

    def test_removes_x_box_and_site_footer(self, tmp_path):
        html = """<!DOCTYPE html>
<html><head><title>Clean</title></head>
<body>
<h1>Title</h1>
<div class="x-box">This should be removed</div>
<p>Keep this.</p>
<div class="site-footer">Footer removed</div>
</body></html>"""
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        assert "x-box" not in result["html"]
        assert "This should be removed" not in result["html"]
        assert "Footer removed" not in result["html"]
        assert "Keep this" in result["html"]


class TestExtractContentEmpty:
    """Test extract_content with empty/minimal HTML."""

    def test_empty_body(self, tmp_path):
        html = """<!DOCTYPE html>
<html><head><title></title></head>
<body></body></html>"""
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        assert result["title"] == "Untitled" or result["title"] == ""
        assert result["tag"] == ""
        assert isinstance(result["img_data_list"], list)
        assert len(result["img_data_list"]) == 0

    def test_no_h1_falls_back_to_title_tag(self, tmp_path):
        html = """<!DOCTYPE html>
<html><head><title>Fallback Title</title></head>
<body><p>Just a paragraph.</p></body></html>"""
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        assert result["title"] == "Fallback Title"

    def test_completely_empty_file(self, tmp_path):
        f = tmp_path / "empty.html"
        f.write_text("", encoding="utf-8")

        result = extract_content(str(f))

        # Should not crash, returns defaults
        assert result["title"] == "Untitled"
        assert result["tag"] == ""
        assert result["img_data_list"] == []


class TestExtractContentMalformed:
    """Test extract_content with malformed/garbage HTML."""

    def test_garbage_input(self, tmp_path):
        html = "<div><p>Unclosed tags <span>nested <b>mess"
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        # Should not crash - returns something
        assert isinstance(result, dict)
        assert "title" in result
        assert "html" in result
        assert isinstance(result["img_data_list"], list)

    def test_binary_garbage(self, tmp_path):
        # Some non-UTF8 bytes that can still be written as text
        html = "\\x00\\x01\\x02 <h1>Still Works</h1> \\xff\\xfe"
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        assert isinstance(result, dict)
        assert "title" in result

    def test_file_not_found_raises(self):
        """FileNotFoundError should be raised for non-existent paths."""
        with pytest.raises(FileNotFoundError):
            extract_content("/nonexistent/path/file.html")

    def test_script_tags_in_body(self, tmp_path):
        html = """<!DOCTYPE html>
<html><head><title>XSS</title></head>
<body>
<h1>Normal Title</h1>
<script>alert('xss')</script>
<p>Content here.</p>
</body></html>"""
        f = tmp_path / "test.html"
        f.write_text(html, encoding="utf-8")

        result = extract_content(str(f))

        assert result["title"] == "Normal Title"
        # Script content may or may not be stripped (depends on BS4 config)
        assert isinstance(result["html"], str)
