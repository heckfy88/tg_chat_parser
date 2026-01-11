import json

from bs4 import BeautifulSoup


def parse_json_file(file_bytes: bytes):
    data = json.loads(file_bytes.decode("utf-8"))
    messages = []
    for msg in data.get("messages", []):
        messages.append({
            "from_id": msg.get("from_id"),
            "from": msg.get("from"),
            "text": extract_text(msg.get("text")),
            "text_entities": msg.get("text_entities", []),
        })
    return messages


def parse_html_file(file_bytes: bytes):
    html_text = file_bytes.decode("utf-8", errors="ignore")

    try:
        soup = BeautifulSoup(html_text, "lxml")
    except:
        soup = BeautifulSoup(html_text, "html.parser")

    messages = []

    for msg_div in soup.select("div.message"):

        classes = msg_div.get("class", [])

        # joined-сообщения не имеют автора
        is_joined = "joined" in classes

        from_name = None
        if not is_joined:
            from_span = msg_div.select_one(".from_name")
            if from_span:
                from_name = from_span.get_text(strip=True)

        text_div = msg_div.select_one(".text")

        text = ""
        mentions = []

        if text_div:
            text = text_div.get_text(" ", strip=True)

            for a in text_div.find_all("a", href=True):
                href = a["href"]
                label = a.get_text(strip=True)

                if href.startswith("https://t.me/") and label.startswith("@"):
                    mentions.append(label)

        messages.append({
            "from_id": None,
            "from": from_name,  # None для joined
            "text": text,
            "html_mentions": mentions,
            "text_entities": [],
            "is_joined": is_joined,  # 👈 полезно дальше
        })

    return messages


def extract_text(text_field):
    """text может быть строкой или массивом. Собираем всё в строку."""
    if isinstance(text_field, str):
        return text_field
    if isinstance(text_field, list):
        out = ""
        for part in text_field:
            if isinstance(part, str):
                out += part
            elif isinstance(part, dict):
                out += part.get("text", "")
        return out
    return ""
