import pdfplumber
import docx
import pytesseract
from PIL import Image
import re
import requests
import tempfile
import os

# 🔷 Set Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# 🔷 MAIN FUNCTION
def extract_text(file_path_or_url):

    try:
        # 🔥 If it's a URL → download first
        if file_path_or_url.startswith("http"):
            file_path = download_file(file_path_or_url)
        else:
            file_path = file_path_or_url

        # 🔷 Detect file type
        if file_path.endswith(".pdf"):
            text = extract_pdf(file_path)
        elif file_path.endswith(".docx"):
            text = extract_docx(file_path)
        elif file_path.endswith((".png", ".jpg", ".jpeg")):
            text = extract_image(file_path)
        else:
            text = ""

        # 🔷 Clean text
        cleaned = clean_text(text)

        # 🔷 Remove temp file if downloaded
        if file_path_or_url.startswith("http") and os.path.exists(file_path):
            os.remove(file_path)

        return cleaned

    except Exception as e:
        print("EXTRACTION ERROR:", e)
        return ""


# 🔥 DOWNLOAD FILE FROM URL
def download_file(url):
    response = requests.get(url)
    response.raise_for_status()

    # Detect extension
    ext = get_extension_from_url(url)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp_file.write(response.content)
    temp_file.close()

    return temp_file.name


# 🔥 GET FILE EXTENSION
def get_extension_from_url(url):
    if ".pdf" in url:
        return ".pdf"
    elif ".docx" in url:
        return ".docx"
    elif ".png" in url:
        return ".png"
    elif ".jpg" in url or ".jpeg" in url:
        return ".jpg"
    else:
        return ".pdf"  # fallback


# 🔷 PDF
def extract_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text(x_tolerance=2, y_tolerance=2)
            if extracted:
                text += extracted + "\n"
    return text


# 🔷 DOCX
def extract_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


# 🔷 IMAGE (OCR)
def extract_image(file_path):
    img = Image.open(file_path)

    # Improve contrast
    img = img.convert("L")

    # Resize (important for OCR)
    img = img.resize((img.width * 2, img.height * 2))

    return pytesseract.image_to_string(img)

# 🔷 CLEAN TEXT
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()