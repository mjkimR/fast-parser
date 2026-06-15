import os
import pytest

@pytest.fixture
def simple_pdf_path() -> str:
    """Fixture that returns the path to the simple.pdf test file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "files", "simple.pdf")


@pytest.fixture
def simple_pdf_bytes(simple_pdf_path) -> bytes:
    """Fixture that returns the raw bytes of the simple.pdf test file."""
    with open(simple_pdf_path, "rb") as f:
        return f.read()
