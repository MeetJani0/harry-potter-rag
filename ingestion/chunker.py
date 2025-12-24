import spacy

nlp = spacy.load("en_core_web_sm")

def chunk_text(structured_pages, max_chars=1200, overlap_sentences=2):
    """
    Sentence-aware chunking:
    - Never cuts sentences
    - Preserves narrative coherence
    - Overlaps by sentences, not characters
    """

    chunks = []
    buffer_sentences = []
    buffer_len = 0
    meta = None

    for p in structured_pages:
        if not p["book"] or not p["chapter"]:
            continue

        current_meta = (p["book"], p["chapter"])

        # Flush buffer on chapter change
        if meta and current_meta != meta:
            chunks.extend(_flush(buffer_sentences, meta))
            buffer_sentences = []
            buffer_len = 0

        meta = current_meta

        doc = nlp(p["text"])

        for sent in doc.sents:
            s = sent.text.strip()
            if not s:
                continue

            if buffer_len + len(s) > max_chars:
                chunks.append({
                    "book": meta[0],
                    "chapter": meta[1],
                    "text": " ".join(buffer_sentences)
                })

                # sentence-level overlap
                buffer_sentences = buffer_sentences[-overlap_sentences:]
                buffer_len = sum(len(x) for x in buffer_sentences)

            buffer_sentences.append(s)
            buffer_len += len(s)

    # final flush
    if buffer_sentences:
        chunks.append({
            "book": meta[0],
            "chapter": meta[1],
            "text": " ".join(buffer_sentences)
        })

    return chunks


def _flush(sentences, meta):
    if not sentences:
        return []
    return [{
        "book": meta[0],
        "chapter": meta[1],
        "text": " ".join(sentences)
    }]