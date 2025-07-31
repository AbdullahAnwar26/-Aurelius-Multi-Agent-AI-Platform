import os
import fitz  # PyMuPDF
import docx

def extract_text(input_source: str) -> str:
    """
    Extracts text from supported file formats (.pdf, .docx, .txt) or directly from a string.

    Args:
        input_source (str): File path or raw text string.

    Returns:
        str: Extracted or input text.

    Raises:
        FileNotFoundError: If the input file doesn't exist.
        ValueError: If the file format is unsupported.
    """

    def read_pdf(file_path: str) -> str:
        try:
            with fitz.open(file_path) as doc:
                return "\n".join(page.get_text() for page in doc)
        except Exception as e:
            raise RuntimeError(f"Failed to extract PDF: {e}")

    def read_docx(file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            raise RuntimeError(f"Failed to extract DOCX: {e}")

    def read_txt(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read TXT: {e}")

    # If it's a valid file path
    if os.path.isfile(input_source):
        ext = os.path.splitext(input_source)[1].lower()

        reader_map = {
            '.pdf': read_pdf,
            '.docx': read_docx,
            '.txt': read_txt,
        }

        if ext in reader_map:
            return reader_map[ext](input_source).strip()
        else:
            raise ValueError(f"Unsupported file format: '{ext}'. Use .pdf, .docx, or .txt.")

    # If it's just a plain string input (not a file path)
    elif isinstance(input_source, str):
        return input_source.strip()

    else:
        raise FileNotFoundError(f"Invalid input or file not found: {input_source}")