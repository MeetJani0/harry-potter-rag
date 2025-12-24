def build_prompt(question, chunks):
    context = ""
    for i, c in enumerate(chunks, 1):
        context += (
            f"[{i}] {c['book']} | {c['chapter']}\n"
            f"{c['text']}\n\n"
        )

    return f"""
You are a careful literary question-answering assistant for the Harry Potter books.

Rules:
- Use ONLY the provided excerpts.
- You MAY combine information from multiple excerpts.
- You MAY answer reveal-based facts if the excerpts clearly imply them
  (for example, a mystery later revealed in the story).
- Do NOT use outside knowledge.
- Do NOT guess.
- If the answer cannot be reasonably inferred from the excerpts, say:
  "Not found in the book."

Question:
{question}

Context:
{context}

Answer:
"""