def build_prompt(question, chunks):
    context = ""
    for i, c in enumerate(chunks, 1):
        context += (
            f"[{i}] {c['book']} | {c['chapter']}\n"
            f"{c['text']}\n\n"
        )

    return f"""
You are a careful literary question-answering assistant.

Instructions:
- Use ONLY the provided context excerpts.
- You MAY combine information from multiple excerpts.
- Do NOT use outside knowledge.
- Do NOT guess or hallucinate.
- If the answer cannot be reasonably inferred from the excerpts, say:
  "Not found in the book."

Question:
{question}

Context:
{context}

Answer:
"""