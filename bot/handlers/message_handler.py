import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes

load_dotenv()


class CustomMessageHandler:
    _max_file_size: int = int(os.environ.get('MAX_FILE_SIZE', ''))
    _max_files_amount: int = int(os.environ.get('MAX_FILES_AMOUNT', ''))
    MAX_TG_BOT_FILE_BYTES = 50 * 1024 * 1024

    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if (len(context.user_data.get("files", "")) + 1) > self._max_files_amount:
            await update.message.reply_text(
                f"Превышено максимально допустимое количество файлов: {self._max_files_amount}")
            return

        document = update.message.document

        if document.file_size and document.file_size > self.MAX_TG_BOT_FILE_BYTES:
            await update.message.reply_text(
                "Файл больше 50 МБ. Telegram не даёт боту скачать такие файлы.\n"
                "Пожалуйста, разбейте файл на части менее 50 МБ и отправь несколько файлов."
                "Потом нажми /process."
            )
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

    async def handle_not_json_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Принимаю только JSON-файлы 📄")
        return