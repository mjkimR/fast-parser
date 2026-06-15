import pymupdf4llm
import pypdfium2 as pdfium
from pdf_oxide import PdfDocument


def parse_with_pdf_oxide(file_path: str) -> str:
    """pdf_oxide parsing"""
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
    """pypdfium2 parsing"""
    pdf = None
    pages_text = []
    try:
        pdf = pdfium.PdfDocument(file_path)
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
        if pdf is not None:
            pdf.close()


def parse_with_pymupdf4llm(file_path: str) -> str:
    """pymupdf4llm parsing"""
    try:
        result = pymupdf4llm.to_markdown(file_path)
        if isinstance(result, str):
            return result
        if isinstance(result, list):
            pages_text = []
            for chunk in result:
                if isinstance(chunk, dict) and "text" in chunk:
                    pages_text.append(chunk["text"])
            return "\n\n".join(pages_text)
        raise TypeError(f"Expected str or list from to_markdown, got {type(result)}")
    except Exception as e:
        raise RuntimeError(f"pymupdf4llm parsing failed: {e}") from e

