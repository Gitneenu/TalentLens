from geminiparser import parse_with_gemini
from parser import extract_text

# Use any resume file
file_path = "sample.pdf"   # change this

text = extract_text(file_path)

print("===== EXTRACTED TEXT =====")
print(text[:500])  # print first 500 chars

print("\n===== GEMINI OUTPUT =====")

result = parse_with_gemini(text)

print(result)