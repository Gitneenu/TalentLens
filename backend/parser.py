import pdfplumber
import docx
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image
import re

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = extract_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_docx(file_path)
    elif file_path.endswith((".png", ".jpg", ".jpeg")):
        text = extract_image(file_path)
    else:
        text = ""

    return clean_text(text)


def extract_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text(x_tolerance=2, y_tolerance=2)
            if extracted:
                text += extracted + "\n"
    return text


def extract_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_image(file_path):
    return pytesseract.image_to_string(Image.open(file_path))

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)   # keep structure
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()
