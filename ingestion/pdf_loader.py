import fitz  # PyMuPDF

def load_pdf(path):
    doc = fitz.open(path)
    pages = []

    for i, page in enumerate(doc):
        pages.append({
            "page": i + 1,          # HUMAN page number
            "text": page.get_text()
        })

    return pages