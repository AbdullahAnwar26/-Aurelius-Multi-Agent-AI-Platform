from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import os
import docx
import PyPDF2

class ResumeExtractorInput(BaseModel):
    filepath: Optional[str] = Field(None, description="Path to the file (PDF, DOCX, or TXT)")
    raw_text: Optional[str] = Field(None, description="Raw text contents of the resume")

class ResumeExtractorTool(BaseTool):
    name: str = "Resume Text Extraction Tool"
    description: str = "Extracts resume text from file (.pdf, .docx, .txt) or directly from raw text"
    args_schema: Type[BaseModel] = ResumeExtractorInput

    def _run(self, filepath: Optional[str] = None, raw_text: Optional[str] = None) -> str:
        if raw_text:
            return raw_text.strip()
        if not filepath or not os.path.isfile(filepath):
            return "No valid file path or raw text provided."
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".pdf":
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        if ext in [".doc", ".docx"]:
            doc = docx.Document(filepath)
            return "\n".join(para.text for para in doc.paragraphs)
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        return "Unsupported file type. Only PDF, DOCX, and TXT are supported."