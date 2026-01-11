import os
import re
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Set

from dotenv import load_dotenv
from openpyxl import Workbook
from telegram import Update
from telegram.ext import ContextTypes

from bot.util.file_util import parse_json_file, parse_html_file

load_dotenv()

USERNAME_RE = re.compile(r"@[A-Za-z0-9_]{5,32}")


def handle_mention(
        participants_by_id: Dict[str, Dict[str, Any]],
        unmatched_mentions: Set[str],
        mention: str
):
    if not isinstance(mention, str):
        return

    mention = mention.strip().lower()

    if not USERNAME_RE.fullmatch(mention):
        return

    # ---------- сопоставление ----------
    for user in participants_by_id.values():
        name = (user.get("username") or "").strip().lower().lstrip("@")
        if name == mention.lstrip("@"):
            user["mentions"].add(mention)
            return

    unmatched_mentions.add(mention)


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

        user_id_formatted_string = f"{user_id}" if user_id not in (None, "", data.get('username', '')) else ""

        ws.append([
            today,
            user_id_formatted_string,
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


def normalize_username(name: str) -> str:
    if not name:
        return ""

    name = name.strip()
    name = re.sub(r"\s+via\s+@[\w_]+", "", name, flags=re.IGNORECASE)

    return name


def parse_telegram_export(file_bytes: bytes, filename: str):
    filename = filename.lower()

    if filename.endswith(".json"):
        return parse_json_file(file_bytes)

    if filename.endswith(".html") or filename.endswith(".htm"):
        return parse_html_file(file_bytes)

    raise ValueError("Unsupported file format")


class BotCommandHandler:
    _excel_user_threshold: int = int(os.environ.get("EXCEL_USER_THRESHOLD", "50"))
    USERNAME_REGEX = re.compile(r'@([A-Za-z0-9_]+)')

    def __init__(self):
        if self._excel_user_threshold < 0:  # 0 - всегда выводим в excel
            raise Exception("Excel user threshold cannot be negative")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data["files"] = []

        instructions = (
            "Привет! Я - бот, который помогает анализировать групповые чаты Telegram\n"
            "📌Для работы со мной следуй инструкции:\n"
            "1. Экспортируй свой чат с помощью приложения Telegram.\n"
            "2. Убедись, что ты получил файлы в форматах .json, .html или .htm.\n"
            "3. Отправь файлы в чат со мной.\n"
            "Я обработаю данные и покажу тебе сводку!"
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
                    uid_string = f"({uid})" if uid not in (None, "", data.get('username', '')) else ""
                    if mentions_str:
                        lines.append(f"- {data.get('username', '')} {uid_string} → {mentions_str}")
                    else:
                        lines.append(f"- {data.get('username', '')} {uid_string}")
            else:
                lines.append("_Нет участников_")

            lines.append("\n🔔 *Упоминания (@username):*")
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
                from_name_raw = msg.get("from")
                from_name = normalize_username(from_name_raw)

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
                        handle_mention(participants_by_id, unmatched_mentions, ent.get("text"))

                # ---------- 3) Упоминания в тексте (JSON + HTML) ----------
                text = msg.get("text") or ""

                if isinstance(text, (bytes, bytearray)):
                    text = text.decode("utf-8", errors="ignore")

                for uname in (msg.get("html_mentions") or []):
                    handle_mention(participants_by_id, unmatched_mentions, uname)

        # если mention сопоставился участнику, он может остаться в unmatched_mentions
        # на случай, когда участник встретился ПОЗЖЕ, чем mention.
        matched = set()
        for user in participants_by_id.values():
            matched |= set(user.get("mentions", set()))
        unmatched_mentions -= matched

        return participants_by_id, unmatched_mentions
