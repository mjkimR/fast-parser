from unittest.mock import MagicMock, patch

import pytest

from app.engines import (
    parse_with_pdf_oxide,
    parse_with_pymupdf4llm,
    parse_with_pypdfium2,
)


@patch("app.engines.PdfDocument")
def test_parse_with_pdf_oxide_success(mock_pdf_doc):
    mock_doc_instance = MagicMock()
    mock_doc_instance.page_count.return_value = 2
    mock_doc_instance.extract_text.side_effect = ["Page 1 text", "Page 2 text"]
    mock_pdf_doc.return_value.__enter__.return_value = mock_doc_instance

    result = parse_with_pdf_oxide("dummy.pdf")
    assert result == "Page 1 text\n\nPage 2 text"
    mock_doc_instance.extract_text.assert_any_call(0)
    mock_doc_instance.extract_text.assert_any_call(1)


@patch("app.engines.PdfDocument")
def test_parse_with_pdf_oxide_failure(mock_pdf_doc):
    mock_pdf_doc.side_effect = Exception("Rust panic or file error")

    with pytest.raises(RuntimeError) as exc_info:
        parse_with_pdf_oxide("dummy.pdf")
    assert "pdf_oxide parsing failed" in str(exc_info.value)


@patch("app.engines.pdfium.PdfDocument")
def test_parse_with_pypdfium2_success(mock_pdf_doc):
    mock_pdf = MagicMock()
    mock_pdf.__len__.return_value = 1
    mock_page = MagicMock()
    mock_textpage = MagicMock()
    mock_textpage.get_text_bounded.return_value = "Hello PDFium"

    mock_page.get_textpage.return_value = mock_textpage
    mock_pdf.get_page.return_value = mock_page
    mock_pdf_doc.return_value = mock_pdf

    result = parse_with_pypdfium2("dummy.pdf")
    assert result == "Hello PDFium"
    mock_pdf.get_page.assert_called_once_with(0)
    mock_page.get_textpage.assert_called_once()
    mock_textpage.close.assert_called_once()
    mock_page.close.assert_called_once()
    mock_pdf.close.assert_called_once()


@patch("app.engines.pdfium.PdfDocument")
def test_parse_with_pypdfium2_failure(mock_pdf_doc):
    mock_pdf_doc.side_effect = Exception("PDFium error")

    with pytest.raises(RuntimeError) as exc_info:
        parse_with_pypdfium2("dummy.pdf")
    assert "pypdfium2 parsing failed" in str(exc_info.value)


@patch("app.engines.pymupdf4llm.to_markdown")
def test_parse_with_pymupdf4llm_success(mock_to_markdown):
    mock_to_markdown.return_value = "# Markdown Content"
    result = parse_with_pymupdf4llm("dummy.pdf")
    assert result == "# Markdown Content"
    mock_to_markdown.assert_called_once_with("dummy.pdf")


@patch("app.engines.pymupdf4llm.to_markdown")
def test_parse_with_pymupdf4llm_list_success(mock_to_markdown):
    mock_to_markdown.return_value = [
        {"text": "# Page 1 Markdown"},
        {"text": "# Page 2 Markdown"},
    ]
    result = parse_with_pymupdf4llm("dummy.pdf")
    assert result == "# Page 1 Markdown\n\n# Page 2 Markdown"
    mock_to_markdown.assert_called_once_with("dummy.pdf")


@patch("app.engines.pymupdf4llm.to_markdown")
def test_parse_with_pymupdf4llm_failure(mock_to_markdown):
    mock_to_markdown.side_effect = Exception("MuPDF error")

    with pytest.raises(RuntimeError) as exc_info:
        parse_with_pymupdf4llm("dummy.pdf")
    assert "pymupdf4llm parsing failed" in str(exc_info.value)


@pytest.mark.parametrize(
    "parse_func",
    [parse_with_pdf_oxide, parse_with_pypdfium2, parse_with_pymupdf4llm],
)
def test_engines_integration_success(simple_pdf_path, parse_func):
    result = parse_func(simple_pdf_path)
    assert "simple" in result.lower()
