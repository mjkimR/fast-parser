import pymupdf4llm  # type: ignore
import pypdfium2 as pdfium  # type: ignore
from pdf_oxide import PdfDocument  # type: ignore


def parse_with_pdf_oxide(file_path: str) -> str:
    """Rust-based pdf_oxide parsing"""
    pages_text = []
    try:
        with PdfDocument(file_path) as doc:
            for i in range(doc.page_count()):
                page_text = doc.extract_text(i)
                if page_text:
                    pages_text.append(page_text)
        return "\n\n".join(pages_text)
    except Exception as e:
        raise RuntimeError(f"pdf_oxide parsing failed: {e}") from e


def parse_with_pypdfium2(file_path: str) -> str:
    """Google Chrome PDFium engine based pypdfium2 parsing"""
    pdf = pdfium.PdfDocument(file_path)
    pages_text = []
    try:
        for i in range(len(pdf)):
            page = pdf.get_page(i)
            textpage = page.get_textpage()
            text = textpage.get_text_bounded()
            if text:
                pages_text.append(text)
            textpage.close()
            page.close()
        return "\n\n".join(pages_text)
    except Exception as e:
        raise RuntimeError(f"pypdfium2 parsing failed: {e}") from e
    finally:
        pdf.close()


def parse_with_pymupdf4llm(file_path: str) -> str:
    """AGPL licensed pymupdf4llm parsing"""
    try:
        return pymupdf4llm.to_markdown(file_path)
    except Exception as e:
        raise RuntimeError(f"pymupdf4llm parsing failed: {e}") from e
