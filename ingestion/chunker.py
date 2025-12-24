import spacy
import re

nlp = spacy.load("en_core_web_sm")

CHAPTER_HEADING_RE = re.compile(r"^chapter\s+\w+", re.IGNORECASE)

def clean_text(text: str) -> str:
    """
    Remove chapter headings and excessive whitespace.
    """
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if CHAPTER_HEADING_RE.match(line):
            continue
        if line.isupper() and len(line.split()) <= 6:
            # Likely chapter title
            continue
        lines.append(line)
    return " ".join(lines)


def chunk_text(structured_pages, max_chars=550, overlap_sents=3):
    """
    Dense, sentence-aware chunking optimized for fact retrieval.
    """

    chunks = []
    buffer = []
    buffer_len = 0
    meta = None

    for p in structured_pages:
        if not p["book"] or not p["chapter"]:
            continue

        current_meta = (p["book"], p["chapter"])

        if meta and current_meta != meta:
            _flush(chunks, buffer, meta)
            buffer, buffer_len = [], 0

        meta = current_meta

        text = clean_text(p["text"])
        doc = nlp(text)

        for sent in doc.sents:
            s = sent.text.strip()
            if not s:
                continue

            if buffer_len + len(s) > max_chars:
                _flush(chunks, buffer, meta)
                buffer = buffer[-overlap_sents:]
                buffer_len = sum(len(x) for x in buffer)

            buffer.append(s)
            buffer_len += len(s)

    if buffer:
        _flush(chunks, buffer, meta)

    return chunks


def _flush(chunks, buffer, meta):
    if not buffer:
        return
    chunks.append({
        "book": meta[0],
        "chapter": meta[1],
        "text": " ".join(buffer)
    })