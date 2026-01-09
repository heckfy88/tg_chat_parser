import json
import os
import re
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Set

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from openpyxl import Workbook

from bs4 import BeautifulSoup

load_dotenv()


def generate_excel(participants_by_id: Dict[str, Dict[str, Any]],
                   unmatched_mentions: Set[str],
                   output_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "Participants"

    ws.append(["Дата экспорта", "UserID", "Nickname", "Mention"])
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1) Одна строка на участника
    for user_id, data in participants_by_id.items():
        mentions = data.get("mentions", set())
        if isinstance(mentions, set):
            mentions_str = ", ".join(sorted(mentions))
        else:
            mentions_str = str(mentions) if mentions else ""

        ws.append([
            today,
            user_id,
            data.get("username", ""),
            mentions_str,
        ])

    # 2) В конце — mentions, которые не удалось сопоставить ни с одним участником
    for uname in sorted(unmatched_mentions):
        ws.append([
            today,
            "",
            "",
            uname,  # "@username"
        ])

    wb.save(output_file)


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

def parse_telegram_export(file_bytes: bytes, filename: str):
    filename = filename.lower()

    # ---------- JSON ----------
    if filename.endswith(".json"):
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

    # ---------- HTML ----------
    if filename.endswith(".html") or filename.endswith(".htm"):
        soup = BeautifulSoup(file_bytes, "lxml")
        messages = []

        for msg_div in soup.select("div.message"):
            from_name = None
            from_span = msg_div.select_one(".from_name")
            if from_span:
                from_name = from_span.get_text(strip=True)

            text_div = msg_div.select_one(".text")
            text = text_div.get_text(" ", strip=True) if text_div else ""

            messages.append({
                "from_id": None,
                "from": from_name,
                "text": text,
                "text_entities": [],
            })

        return messages

    raise ValueError("Unsupported file format")


class BotCommandHandler:
    _excel_user_threshold: int = int(os.environ.get("EXCEL_USER_THRESHOLD", "200"))
    USERNAME_REGEX = re.compile(r'@([A-Za-z0-9_]+)')

    def __init__(self):
        if self._excel_user_threshold < 0:  # 0 - всегда выводим в excel
            raise Exception("Excel user threshold cannot be negative")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data["files"] = []

        instructions = (
            "Hi! I can analyze exported Telegram chat data.\n\n"
            "📌 Please follow these steps:\n"
            "1. Export your Telegram chat using the official export tool.\n"
            "2. Make sure the file is in `.json` or `.html` format.\n"
            "3. Send the `.json` or `.html` file directly to this bot.\n\n"
            "I will process the data and provide you with insights!"
        )
        await update.message.reply_text(instructions)

    async def process(self, update, context):
        participants_by_id, unmatched_mentions = await self.extract_participants_from_files(update, context)

        count = len(participants_by_id)
        print(f"Найдено участников: {count}")

        # ---------- ТЕКСТОВЫЙ ВЫВОД ----------
        if count < self._excel_user_threshold:
            lines = ["📊 *Результаты анализа файлов:*\n", "👥 *Участники чата:*"]

            if participants_by_id:
                for uid, data in participants_by_id.items():
                    mentions = data.get("mentions", set())
                    mentions_str = ", ".join(sorted(mentions)) if mentions else ""
                    if mentions_str:
                        lines.append(f"- {data.get('username', '')} (`{uid}`) → {mentions_str}")
                    else:
                        lines.append(f"- {data.get('username', '')} (`{uid}`)")
            else:
                lines.append("_Нет участников_")

            lines.append("\n🔔 *Несопоставленные упоминания (@username):*")
            if unmatched_mentions:
                for uname in sorted(unmatched_mentions):
                    lines.append(f"- {uname}")
            else:
                lines.append("_Нет_")

            await update.message.reply_text("\n".join(lines))
            return

        # ---------- EXCEL ----------
        output = BytesIO()
        generate_excel(participants_by_id, unmatched_mentions, output)
        output.seek(0)

        await update.message.reply_document(
            document=output,
            filename=f"participants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )

    async def extract_participants_from_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        files = context.user_data.get("files", [])

        participants_by_id: Dict[str, Dict[str, Any]] = {}
        unmatched_mentions: Set[str] = set()

        def handle_mention(mention: str):
            """Пытаемся сопоставить mention с участником.
            Если нельзя — кладём в unmatched_mentions.
            """
            if not isinstance(mention, str):
                return

            mention = mention.strip()
            if not mention.startswith("@") or len(mention) <= 1:
                return

            mention_l = mention.lower()

            # Сопоставляем только если у участника from выглядит как @username
            for user in participants_by_id.values():
                # name = (user.get("username") or "").strip().lower()
                # if name.startswith("@") and name == mention_l:
                #     user["mentions"].add(mention_l)
                #     return
                name = (user.get("username") or "").strip().lower().lstrip("@")
                if name and name == mention_l.lstrip("@"):
                    user["mentions"].add(mention_l)
                    return

            unmatched_mentions.add(mention_l)

        for document in files:
            file = await document.get_file()
            data_bytes = await file.download_as_bytearray()

            try:
                messages = parse_telegram_export(data_bytes, document.file_name)
            except Exception as e:
                print(f"Не удалось обработать файл {document.file_name}: {e}")
                continue

            for msg in messages:

                # ---------- 1) Участники ----------
                from_id = msg.get("from_id")
                from_name = msg.get("from")

                if from_name and from_name != "Deleted Account":
                    # Для HTML у нас нет from_id → используем имя как ключ
                    uid = from_id or from_name

                    if uid not in participants_by_id:
                        participants_by_id[uid] = {
                            "username": from_name,
                            "mentions": set(),
                        }
                    else:
                        if not participants_by_id[uid].get("username"):
                            participants_by_id[uid]["username"] = from_name

                # ---------- 2) Упоминания из entities (JSON) ----------
                for ent in (msg.get("text_entities") or []):
                    if ent.get("type") == "mention":
                        handle_mention(ent.get("text"))

                # ---------- 3) Упоминания в тексте (JSON + HTML) ----------
                text = msg.get("text") or ""
                for uname in self.USERNAME_REGEX.findall(text):
                    if uname:
                        handle_mention(f"@{uname}")

        # (опционально) если mention сопоставился участнику, он может остаться в unmatched_mentions
        # на случай, когда участник встретился ПОЗЖЕ, чем mention.
        matched = set()
        for user in participants_by_id.values():
            matched |= set(user.get("mentions", set()))
        unmatched_mentions -= matched

        return participants_by_id, unmatched_mentions
