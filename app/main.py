import os
import tempfile
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
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


async def _execute_parse(file: UploadFile, parse_func, engine_name: str):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    tmp_path = None
    try:
        # 1. Save upload stream to temp file using chunks to avoid OOM
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            while chunk := await file.read(1024 * 1024):  # 1MB chunk
                tmp.write(chunk)
            tmp_path = tmp.name

        # 2. Parse PDF with the requested engine function
        result = parse_func(tmp_path)
        return {"engine": engine_name, "content": result}

    except RuntimeError as e:
        logger.error(f"PDF parsing runtime error for {engine_name}: {e}")
        raise HTTPException(status_code=400, detail=f"Parsing failed: {e!s}") from e
    except Exception as e:
        logger.exception(f"Unexpected error during PDF parsing for {engine_name}: {e}")
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


@app.post("/pdf_oxide/parse")
async def parse_pdf_oxide(file: Annotated[UploadFile, File(...)]):
    """Parse a PDF document using the pdf_oxide engine."""
    return await _execute_parse(file, parse_with_pdf_oxide, "pdf_oxide")


@app.post("/pypdfium2/parse")
async def parse_pypdfium2(file: Annotated[UploadFile, File(...)]):
    """Parse a PDF document using the pypdfium2 engine."""
    return await _execute_parse(file, parse_with_pypdfium2, "pypdfium2")


@app.post("/pymupdf4llm/parse")
async def parse_pymupdf4llm(file: Annotated[UploadFile, File(...)]):
    """Parse a PDF document using the pymupdf4llm engine."""
    return await _execute_parse(file, parse_with_pymupdf4llm, "pymupdf4llm")
