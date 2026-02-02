import os
from typing import List
import logging
import pdfplumber
import docx
import markdown_it
from langchain_core.documents import Document
import chardet

# Suppress pdfminer warnings about FontBBox
logging.getLogger("pdfminer").setLevel(logging.ERROR)

class DocParser:
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    @staticmethod
    def parse_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    @staticmethod
    def parse_markdown(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
        # Note: For structure splitting, we might handle it in the splitter service, 
        # but here we just extract raw text for now or return it as is.

    @staticmethod
    def parse_txt(file_path: str) -> str:
        # Detect encoding
        with open(file_path, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        
        return raw_data.decode(encoding)

    @staticmethod
    def parse(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return DocParser.parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return DocParser.parse_docx(file_path)
        elif ext in [".md", ".markdown"]:
            return DocParser.parse_markdown(file_path)
        elif ext == ".txt":
            return DocParser.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
