def assign_book(page_num):
    if 8 <= page_num <= 276:
        return "Harry Potter and the Sorcerer’s Stone"
    elif 277 <= page_num <= 567:
        return "Harry Potter and the Chamber of Secrets"
    elif 568 <= page_num <= 941:
        return "Harry Potter and the Prisoner of Azkaban"
    elif 942 <= page_num <= 1562:
        return "Harry Potter and the Goblet of Fire"
    elif 1563 <= page_num <= 2408:
        return "Harry Potter and the Order of the Phoenix"
    elif 2409 <= page_num <= 2966:
        return "Harry Potter and the Half-Blood Prince"
    elif 2967 <= page_num <= 3623:
        return "Harry Potter and the Deathly Hallows"
    return None


def assign_structure(pages):
    structured = []
    current_chapter = None

    for p in pages:
        text = p["text"]
        book = assign_book(p["page"])

        # Detect chapter titles from text
        for line in text.splitlines():
            if line.strip().upper().startswith("CHAPTER"):
                current_chapter = line.strip()
                break

        structured.append({
            "book": book,
            "chapter": current_chapter,
            "page": p["page"],
            "text": text
        })

    return structured