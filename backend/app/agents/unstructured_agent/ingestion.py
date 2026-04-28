# Extract = take text out of a file and convert it into plain text (string)
# PURPOSE: Extracts raw text from PDF, DOCX, and TXT files
# This gives us the text we then split into chunks

import pdfplumber
from typing import Optional

class DocumentIngestionAgent:

    def extract(self, file_path: str) -> Optional[str]:
        # Route to correct extractor based on file type
        if file_path.endswith(".pdf"):
            return self.extract_pdf(file_path)
        elif file_path.endswith(".docx"):
            return self.extract_docx(file_path)
        elif file_path.endswith(".txt"):
            return self.extract_txt(file_path)
        return None

    def extract_pdf(self, file_path: str) -> Optional[str]:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf: #Why with? Automatically closes the file after use (safe & clean)
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        # Add page marker for reference
                        text += f"\n[Page {page_num + 1}]\n{page_text}\n"
            return text.strip()
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return None

    def extract_docx(self, file_path: str) -> Optional[str]:
        from docx import Document
        try:
            doc   = Document(file_path)
            # Each paragraph in the DOCX is a separate object
            lines = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(lines)
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return None

    def extract_txt(self, file_path: str) -> Optional[str]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"TXT read error: {e}")
            return None

# PyPDFLoader → Understanding
    # PDF → Text → Chunks → Embeddings → AI answers questions

    # 👉 Used for:

        # Chatbots
        # Q&A systems
        # semantic search


# 📊 pdfplumber → Analysis
    # PDF → Text → Extract numbers → DataFrame → Trend analysis

    # 👉 Used for:

        # financial insights
        # calculations
        # structured analysis