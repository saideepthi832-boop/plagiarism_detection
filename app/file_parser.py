import fitz
from docx import Document
import os

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.pdf':
        doc = fitz.open(filepath)
        text = " ".join(page.get_text() for page in doc)
        doc.close()
        return text
    elif ext == '.docx':
        doc = Document(filepath)
        return " ".join(p.text for p in doc.paragraphs if p.text.strip())
    elif ext == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return ""

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'txt'}