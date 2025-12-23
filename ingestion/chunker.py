def chunk_text(structured_pages, chunk_size=800, overlap=150):
    chunks = []
    buffer = ""
    meta = None

    for p in structured_pages:
        if not p["book"] or not p["chapter"]:
            continue

        new_meta = (p["book"], p["chapter"])

        if meta and new_meta != meta:
            chunks.extend(_split(buffer, meta))
            buffer = ""

        buffer += "\n" + p["text"]
        meta = new_meta

    if buffer:
        chunks.extend(_split(buffer, meta))

    return chunks


def _split(text, meta):
    book, chapter = meta
    out = []
    start = 0

    while start < len(text):
        out.append({
            "book": book,
            "chapter": chapter,
            "text": text[start:start + 800]
        })
        start += 800 - 150

    return out