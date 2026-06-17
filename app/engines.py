
import pymupdf4llm
from pdf_oxide import PdfDocument


def parse_with_pdf_oxide(file_path: str) -> dict:
    """pdf_oxide parsing"""
    import json
    pages = []
    try:
        with PdfDocument(file_path) as doc:
            for i in range(doc.page_count()):
                structured_str = doc.extract_structured(i)
                data = json.loads(structured_str)
                
                regions = data.get("regions", [])
                page_boxes = []
                page_text_parts = []
                current_pos = 0
                
                for region in regions:
                    kind = region.get("kind", "text")
                    text = region.get("text", "").strip()
                    if not text:
                        continue
                    
                    bbox_dict = region.get("bbox", {})
                    x = bbox_dict.get("x", 0.0)
                    y = bbox_dict.get("y", 0.0)
                    w = bbox_dict.get("width", 0.0)
                    h = bbox_dict.get("height", 0.0)
                    
                    left = x
                    top = y
                    right = x + w
                    bottom = y + h
                    
                    start_pos = current_pos
                    end_pos = current_pos + len(text)
                    page_text_parts.append(text)
                    current_pos += len(text) + 2  # Join by '\n\n'
                    
                    page_boxes.append({
                        "class": kind.lower(),
                        "bbox": [left, top, right, bottom],
                        "pos": [start_pos, end_pos]
                    })
                
                page_text = "\n\n".join(page_text_parts)
                pages.append({
                    "page_no": i + 1,
                    "text": page_text,
                    "page_boxes": page_boxes
                })
        return {"pages": pages}
    except Exception as e:
        raise RuntimeError(f"pdf_oxide parsing failed: {e}") from e


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
                    pages.append({
                        "page_no": page_idx + 1,
                        "text": chunk.get("text", ""),
                        "page_boxes": chunk.get("page_boxes", [])
                    })

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
