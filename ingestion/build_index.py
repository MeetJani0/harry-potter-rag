import os, pickle, faiss
from collections import defaultdict
from pdf_loader import load_pdf
from structure_parser import assign_structure
from chunker import chunk_text
from embeddings import embed
import re

def safe_folder_name(text: str) -> str:
    text = text.lower()
    text = text.replace("’", "")  # remove smart apostrophe
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

PDF_PATH = "data/harrypotter.pdf"
OUT_DIR = "vector_store"

pages = load_pdf(PDF_PATH)
structured = assign_structure(pages)
chunks = chunk_text(structured)

books = defaultdict(list)
for c in chunks:
    books[c["book"]].append(c)

os.makedirs(OUT_DIR, exist_ok=True)

for book, items in books.items():
    texts = [i["text"] for i in items]
    vectors = embed(texts)

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    safe = safe_folder_name(book)
    path = f"{OUT_DIR}/{safe}"
    os.makedirs(path, exist_ok=True)

    faiss.write_index(index, f"{path}/index.faiss")
    with open(f"{path}/meta.pkl", "wb") as f:
        pickle.dump(items, f)

    print(f"Indexed → {book}")