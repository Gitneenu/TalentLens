import pdfplumber
import docx
import pytesseract
from PIL import Image

def parse_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def parse_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def parse_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return parse_pdf(file_path)

    elif file_path.endswith(".docx"):
        return parse_docx(file_path)

    elif file_path.endswith((".png", ".jpg", ".jpeg")):
        return parse_image(file_path)

    else:
        return "Unsupported file format"