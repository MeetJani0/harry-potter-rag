def build_prompt(question, chunks):
    context = ""
    for i, c in enumerate(chunks, 1):
        context += (
            f"[{i}] {c['book']} | {c['chapter']}\n"
            f"{c['text']}\n\n"
        )

    return f"""
You are a careful, story-aware assistant.

Rules:
- Answer ONLY using the provided context.
- Do NOT use outside knowledge.
- If the answer is not clearly supported, say "Not found in the book."

Question:
{question}

Context:
{context}

Answer:
"""