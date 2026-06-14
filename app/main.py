import os
import tempfile
from typing import Annotated, Literal

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from loguru import logger

from app.engines import (
    parse_with_pdf_oxide,
    parse_with_pymupdf4llm,
    parse_with_pypdfium2,
)

app = FastAPI(
    title="Fast Parser API",
    description="High-speed PDF text/markdown extraction microservice",
)


@app.post("/parse")
async def parse_pdf(
    file: Annotated[UploadFile, File(...)],
    engine: Literal["pdf_oxide", "pypdfium2", "pymupdf4llm"] = Query(
        "pdf_oxide", description="Select engine: pdf_oxide, pypdfium2, pymupdf4llm"
    ),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    tmp_path = None
    try:
        # 1. Save upload stream to temp file using chunks to avoid OOM
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            while chunk := await file.read(1024 * 1024):  # 1MB chunk
                tmp.write(chunk)
            tmp_path = tmp.name

        # 2. Parse PDF with requested engine
        if engine == "pdf_oxide":
            result = parse_with_pdf_oxide(tmp_path)
        elif engine == "pypdfium2":
            result = parse_with_pypdfium2(tmp_path)
        elif engine == "pymupdf4llm":
            result = parse_with_pymupdf4llm(tmp_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported engine: {engine}")

        return {"engine": engine, "content": result}

    except RuntimeError as e:
        logger.error(f"PDF parsing runtime error: {e}")
        raise HTTPException(status_code=400, detail=f"Parsing failed: {e!s}") from e
    except Exception as e:
        logger.exception(f"Unexpected error during PDF parsing: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error during PDF parsing"
        ) from e
    finally:
        # 3. Clean up temp file safely
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.error(f"Failed to remove temp file {tmp_path}: {e}")
