def break_up(content):
    parts = []
    current_text = ""
    for element in content:
        if element["type"] == "text":
            current_text += element["content"]
        elif element["type"] == "figure":
            parts.append({"type": "text", "content": current_text})
            parts.append(element)
            current_text = ""
    if current_text:
        parts.append({"type": "text", "content": current_text})
    return parts