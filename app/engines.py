import pymupdf4llm
import pypdfium2 as pdfium
from pdf_oxide import PdfDocument


def parse_with_pdf_oxide(file_path: str) -> dict:
    """pdf_oxide parsing"""
    pages_text = []
    try:
        with PdfDocument(file_path) as doc:
            for i in range(doc.page_count()):
                page_text = doc.extract_text(i)
                pages_text.append(page_text or "")
        return {"pages": [{"page_no": i + 1, "text": text} for i, text in enumerate(pages_text)]}
    except Exception as e:
        raise RuntimeError(f"pdf_oxide parsing failed: {e}") from e


def parse_with_pypdfium2(file_path: str) -> dict:
    """pypdfium2 parsing"""
    pdf = None
    pages_text = []
    try:
        pdf = pdfium.PdfDocument(file_path)
        for i in range(len(pdf)):
            page = pdf.get_page(i)
            textpage = page.get_textpage()
            text = textpage.get_text_bounded()
            pages_text.append(text or "")
            textpage.close()
            page.close()
        return {"pages": [{"page_no": i + 1, "text": text} for i, text in enumerate(pages_text)]}
    except Exception as e:
        raise RuntimeError(f"pypdfium2 parsing failed: {e}") from e
    finally:
        if pdf is not None:
            pdf.close()


def parse_with_pymupdf4llm(file_path: str) -> dict:
    """pymupdf4llm parsing"""
    try:
        # Standard markdown output
        result = pymupdf4llm.to_markdown(file_path)

        # Page chunks list
        chunks = pymupdf4llm.to_markdown(file_path, page_chunks=True)
        pages = []

        if isinstance(chunks, list):
            for chunk in chunks:
                if isinstance(chunk, dict):
                    page_idx = chunk.get("metadata", {}).get("page", 0)
                    pages.append({"page_no": page_idx + 1, "text": chunk.get("text", "")})

        markdown_str = ""
        if isinstance(result, str):
            markdown_str = result
        elif isinstance(result, list):
            pages_text = []
            for chunk in result:
                if isinstance(chunk, dict) and "text" in chunk:
                    pages_text.append(chunk["text"])
            markdown_str = "\n\n".join(pages_text)

        return {"markdown": markdown_str, "pages": pages}
    except Exception as e:
        raise RuntimeError(f"pymupdf4llm parsing failed: {e}") from e
