from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_parse_pdf_invalid_extension():
    file_content = b"some plain text content"
    files = {"file": ("test.txt", file_content, "text/plain")}
    response = client.post("/pdf_oxide/parse", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported"


@patch("app.main.parse_with_pdf_oxide")
def test_parse_pdf_oxide_success(mock_parse):
    mock_parse.return_value = "parsed content oxide"
    file_content = b"%PDF-1.4 mock pdf data"
    files = {"file": ("test.pdf", file_content, "application/pdf")}

    response = client.post("/pdf_oxide/parse", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "pdf_oxide"
    assert data["content"] == "parsed content oxide"
    mock_parse.assert_called_once()


@patch("app.main.parse_with_pypdfium2")
def test_parse_pypdfium2_success(mock_parse):
    mock_parse.return_value = "parsed content pdfium"
    file_content = b"%PDF-1.4 mock pdf data"
    files = {"file": ("test.pdf", file_content, "application/pdf")}

    response = client.post("/pypdfium2/parse", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "pypdfium2"
    assert data["content"] == "parsed content pdfium"
    mock_parse.assert_called_once()


@patch("app.main.parse_with_pymupdf4llm")
def test_parse_pymupdf4llm_success(mock_parse):
    mock_parse.return_value = "parsed content mupdf"
    file_content = b"%PDF-1.4 mock pdf data"
    files = {"file": ("test.pdf", file_content, "application/pdf")}

    response = client.post("/pymupdf4llm/parse", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "pymupdf4llm"
    assert data["content"] == "parsed content mupdf"
    mock_parse.assert_called_once()


def test_parse_pdf_invalid_endpoint():
    file_content = b"%PDF-1.4 mock pdf data"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    response = client.post("/invalid_engine/parse", files=files)
    assert response.status_code == 404


@patch("app.main.parse_with_pdf_oxide")
def test_parse_pdf_runtime_error(mock_parse):
    mock_parse.side_effect = RuntimeError("Something went wrong")
    file_content = b"%PDF-1.4 mock pdf data"
    files = {"file": ("test.pdf", file_content, "application/pdf")}

    response = client.post("/pdf_oxide/parse", files=files)
    assert response.status_code == 400
    assert "Parsing failed" in response.json()["detail"]


@patch("app.main.parse_with_pdf_oxide")
def test_parse_pdf_unexpected_error(mock_parse):
    mock_parse.side_effect = ValueError("Unexpected value error")
    file_content = b"%PDF-1.4 mock pdf data"
    files = {"file": ("test.pdf", file_content, "application/pdf")}

    response = client.post("/pdf_oxide/parse", files=files)
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@pytest.mark.parametrize("engine", ["pdf_oxide", "pypdfium2", "pymupdf4llm"])
def test_parse_pdf_integration_success(simple_pdf_bytes, engine):
    files = {"file": ("simple.pdf", simple_pdf_bytes, "application/pdf")}
    response = client.post(f"/{engine}/parse", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == engine
    assert "simple" in data["content"].lower()
