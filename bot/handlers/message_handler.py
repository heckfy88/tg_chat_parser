import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes

load_dotenv()


class CustomMessageHandler:
    _max_file_size: int = int(os.environ.get('MAX_FILE_SIZE', '50')) # ограничение размера файла ТГ, при изменении поменять значение в env
    _max_files_amount: int = int(os.environ.get('MAX_FILES_AMOUNT', ''))

    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if (len(context.user_data.get("files", "")) + 1) > self._max_files_amount:
            await update.message.reply_text(
                f"Превышено максимально допустимое количество файлов: {self._max_files_amount}")
            return

        document = update.message.document

        if document.file_size and document.file_size > (self._max_file_size * 1024 * 1024):
            await update.message.reply_text(
                f"Файл больше {self._max_file_size} МБ. Telegram не даёт боту скачать такие файлы.\n"
                f"Пожалуйста, разбейте файл на части менее {self._max_file_size} МБ и отправь несколько файлов."
                "Потом нажми /process."
            )
            return

        # Сохраняем объект документа
        files = context.user_data.get("files", [])
        files.append(document)
        context.user_data["files"] = files

        if len(files) == self._max_files_amount:
            await update.message.reply_text(
                f"Загружен {len(files)}-й файл, введите команду обработки"
            )

        await update.message.reply_text(
            f"Добавлен файл: {document.file_name}\n"
            f"Всего файлов: {len(files)}\n\n"
            "Отправляй остальные или напиши /process."
        )

    async def handle_not_supported_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        document = update.message.document

        if not document:
            return

        await update.message.reply_text(
            "Этот тип файла не поддерживается\n\n"
            "Пожалуйста, отправь файл в формате:\n"
            "• JSON (.json)\n"
            "• HTML (.html, .htm)"
        )
