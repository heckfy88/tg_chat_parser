import json
import os
import re
from datetime import datetime
from io import BytesIO
from typing import Dict, Any

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from openpyxl import Workbook

load_dotenv()


class BotCommandHandler:
    USERNAME_REGEX = re.compile(r'@([A-Za-z0-9_]+)')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends explanation on how to use the bot."""
        context.user_data["files"] = []

        instructions = (
            "Hi! I can analyze exported Telegram chat data.\n\n"
            "📌 Please follow these steps:\n"
            "1. Export your Telegram chat using the official export tool.\n"
            "2. Make sure the file is in `.json` format.\n"
            "3. The file size must not exceed 20 MB.\n"
            "4. Send the `.json` file directly to this bot.\n\n"
            "I will process the data and provide you with insights!"
        )
        await update.message.reply_text(instructions)

    async def process(self, update, context):
        participants_by_id, participants_by_username = await self.extract_participants_from_files(update, context)

        count = len(participants_by_id)
        print(f"Найдено участников: {count}")

        # ---------- ТЕКСТОВЫЙ ВЫВОД ----------
        if count < 50:
            lines = ["📊 *Результаты анализа файлов:*\n", "👥 *Участники чата:*"]

            # Участники
            if participants_by_id:
                for uid, data in participants_by_id.items():
                    username = data["username"]
                    lines.append(f"- {username} (`user{uid}`)")
            else:
                lines.append("_Нет участников_\n")

            # Упоминания
            lines.append("\n🔔 *Упоминания (@username):*")
            if participants_by_username:
                for uname in participants_by_username:
                    lines.append(f"- {uname}")
            else:
                lines.append("_Нет упоминаний_")

            message_text = "\n".join(lines)
            await update.message.reply_text(message_text)

        # ---------- ЕСЛИ МЕНЬШЕ 50 УЧАСТНИКОВ — Excel не нужен ----------
            return list(participants_by_id.values())

        # ---------- ИНАЧЕ — ГЕНЕРИРУЕМ EXCEL ----------
        output = BytesIO()
        self.generate_excel(participants_by_id, output)
        output.seek(0)  # обязательно вернуться в начало файла

        await update.message.reply_document(document=output,
                                            filename=f"participants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

        return "Файл отправлен"

    async def extract_participants_from_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        files = context.user_data.get("files", [])

        participants_by_id: Dict[str, Dict[str, Any]] = {}
        participants_by_username: Dict[str, Dict[str, Any]] = {}

        for document in files:
            file = await document.get_file()
            data_bytes = await file.download_as_bytearray()

            try:
                data = json.loads(data_bytes.decode("utf-8"))
            except Exception as e:
                # пропускаем файл, если не JSON
                print(f"Не удалось распарсить файл: {e}")
                continue

            messages = data.get("messages", [])
            for msg in messages:

                # ---------- 1) Участники (from_id + from) ----------
                from_id = msg.get("from_id")
                username = msg.get("from")

                if from_id and username and username != "Deleted Account":
                    participants_by_id[from_id] = {"username": username}

                # ---------- 2) упоминания через text_entities ----------
                for ent in msg.get("text_entities", []):
                    if ent.get("type") == "mention":
                        uname = ent.get("text")
                        if uname and uname.startswith("@"):
                            participants_by_username[uname] = True

                # ---------- 3) упоминания в тексте ----------
                text = self.extract_text(msg.get("text"))
                for uname in self.USERNAME_REGEX.findall(text):
                    participants_by_username[f"@{uname}"] = True

            return participants_by_id, participants_by_username

    def extract_text(self, text_field):
        """
        text может быть строкой или массивом.
        Собираем всё в строку.
        """
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

    def generate_excel(self, participants: dict, output_file):
        wb = Workbook()
        ws = wb.active
        ws.title = "Participants"

        ws.append([
            "Дата экспорта",
            "UserID",
            "Nickname",
        ])

        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for key, value in participants.items():
            ws.append([
                today,
                key,
                value.get("username", ""),
            ])

        wb.save(output_file)


class JsonMessageHandler:
    _max_file_size: int = int(os.environ.get('MAX_FILE_SIZE', ''))
    _max_files_amount: int = int(os.environ.get('MAX_FILES_AMOUNT', ''))

    def __init__(self):
        if self._max_file_size == '':
            raise Exception("Max file size is not set. Notify admins")
        if not self._max_file_size.is_integer():
            raise Exception("Max file size is not integer. Notify admins")
        if self._max_files_amount == '':
            raise Exception("Max files amount is not set. Notify admins")
        if not self._max_files_amount.is_integer():
            raise Exception("Max files amount is not integer. Notify admins")

    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if (len(context.user_data.get("files", "")) + 1) > self._max_files_amount:
            await update.message.reply_text(f"Превышено максимально допустимое количество файлов: {self._max_files_amount}")
            return

        document = update.message.document

        if not document.file_name.lower().endswith(".json"):
            await update.message.reply_text("Принимаю только JSON-файлы 📄")
            return

        if document.file_size > (self._max_file_size * 1000 * 1000):
            await update.message.reply_text(f"Размер файла превышает максимально допустимый: {self._max_file_size} MB")
            return


        # Сохраняем сам объект документа
        files = context.user_data.get("files", [])
        files.append(document)
        context.user_data["files"] = files

        if len(files) == self._max_files_amount:
            await update.message.reply_text(f"Загружен {len(files)}-й файл, введите команду обработки")

        await update.message.reply_text(
            f"Добавлен файл: {document.file_name}\n"
            f"Всего файлов: {len(files)}\n\n"
            "Отправляй остальные или напиши /process."
        )
